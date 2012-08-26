########################
###   MEMOIZER
########################

def memoized(self, typ, obj, **kwargs):
    """
        For a given typ:
            Determine identity of obj
                Memoize result of self.calculator.<typ>_value(obj, **kwargs)
    """
    identity = id(obj)
    if identity not in self.results[typ]:
        self.results[typ][identity] = getattr(self.calculator, "%s_value" % typ)(obj, **kwargs)
    return self.results[typ][identity]

def memoizer(typ):
    '''Return function that uses memoized for particular type'''
    def memoized(self, obj, **kwargs):
        return self.memoized(typ, obj, **kwargs)
    return memoized

def make_memoizer(calculator, *namespaces):
    '''
        Create a class for memoizing particular values under particular namespaces
        Will use <typ>_value(obj, **kwargs) methods on calculator to memoize results for an obj
        Where identity of obj is determined by id(obj)
    '''
    attrs = {}
    results = {}
    for value in namespaces:
        results[value] = {}
        attrs[value] = memoizer(value)
    
    attrs['results'] = results
    attrs['memoized'] = memoized
    attrs['calculator'] = calculator
    return type("Memoizer", (object, ), attrs)

########################
###   SECTION MASTER
########################

class SectionMaster(object):
    '''Determine information for sections for a given request'''
    def __init__(self, request):
        self.request = request
        self.memoized = make_memoizer(self, 'url_parts', 'active', 'exists', 'display', 'selected')()
        
    ########################
    ###   MEMOIZED VALUES
    ########################
    
    def url_parts_value(self, section):
        '''Determine list of url parts of parent and this section'''
        urls = []
        if not section:
            return []
        
        if hasattr(section, 'parent') and section.parent:
            urls.extend(self.memoized.url_parts(section.parent))
        
        url = section.url
        if type(url) in (str, unicode) and url.startswith("/"):
            url = url[1:]
        
        if not section.options.promote_children:
            urls.append(url)

        if not urls or urls[0] != '':
            urls.insert(0, '')
        
        return urls
    
    def active_value(self, section):
        '''Determine if section and parent are active'''
        if hasattr(section, 'parent') and section.parent:
            if not self.memoized.active(section.parent):
                return False
        return section.options.conditional('active', self.request)
    
    def exists_value(self, section):
        '''Determine if section and parent exists'''
        if hasattr(section, 'parent') and section.parent:
            if not self.memoized.exists(section.parent):
                return False
        return section.options.conditional('exists', self.request)
    
    def display_value(self, section):
        '''Determine if section and parent can be displayed'''
        if hasattr(section, 'parent') and section.parent:
            display, propogate = self.memoized.display(section.parent)
            if not display and propogate:
                return False, True
        return section.can_display(self.request)
    
    def selected_value(self, section, path):
        """Return True and rest of path if selected else False and no path."""
        url = section.url
        parent_selected = True
        if section.parent:
            parent_selected, path = self.memoized.selected(section.parent, path=path)

        if not parent_selected or not path:
            return False, []

        if (path[0] == '' and str(url) == '/') or (path[0].lower() == str(url).lower()):
            return True, path[1:]
        else:
            if section.options.promote_children:
                return True, path
            else:
                return False, []
        
    ########################
    ###   INFO
    ########################

    def iter_section(self, section, path):
        """
            Yield (url, alias) pairs for this section
            If section isn't active, nothing is yielded
            If section has values, url, alias is yielded for each value
            if Section has no values, it's own url and alias is yielded
        """
        if not section.options.conditional('active', self.request):
            # Section not even active
            return
        
        if section.options.values:
            # This section has multiple items to show in the menu
            parent_url_parts = self.memoized.url_parts(section.parent)
            for url, alias in section.options.values.get_info(self.request, path, parent_url_parts):
                yield url, alias
        else:
            # This item only has one item to show in the menu
            yield section.url, section.alias
    
    def get_info(self, section, path, parent=None):
        '''
            Yield Info objects for this section
            Used by templates to render the menus
        '''
        for url, alias in self.iter_section(section, path):
            for info in self._get_info(url, alias, section, path, parent):
                yield info

    def _get_info(self, url, alias, section, path, parent):
        """Closure to yield info for a url, alias pair"""
        info = Info(url, alias, section, parent)
        path_copy = list(path)
        
        # Use SectionMaster logic to keep track of parent_url and parent_selected
        # By giving it the info instead of section
        appear = lambda : self.memoized.exists(info) and self.memoized.active(info)
        display = lambda : self.memoized.display(info)[0]
        selected = lambda : self.memoized.selected(info, path=path_copy)
        url_parts = lambda: self.memoized.url_parts(info)
        
        # Give lazily loaded stuff to info and yield it
        info.setup(appear, display, selected, url_parts)
        yield info

########################
###   INFO OBJECT
########################

class Info(object):
    '''Object to hold information used by templates'''
    def __init__(self, url, alias, section, parent):
        self.url = url
        self.alias = alias
        self.parent = parent or section.parent
        self.section = section
        self.options = section.options
    
    def setup(self, appear, display, selected, url_parts):
        self.appear = appear
        self.display = display
        self.selected = selected
        self.url_parts = url_parts

    def setup_children(self, children):
        self.children = children

    def can_display(self, request):
        return self.section.can_display(request)

    @property
    def menu_sections(self):
        return self.section.menu_sections

    @property
    def full_url(self):
        return '/'.join(str(p) for p in self.url_parts()) or '/'

    def __repr__(self):
        return '<Info %s:%s>' % (self.url, self.alias)