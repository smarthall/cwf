# coding: spec

from urls.section import Site, Section

describe 'Site':
    before_each:
        self.site = Site('test')
        self.sect1 = Section('some', name='sect1')
        self.sect2 = Section('very', name='sect2')
        self.sect3 = Section('nice', name='sect3')
        self.sect4 = Section('place', name='sect4')
        
        for sect in [self.sect1, self.sect2, self.sect3, self.sect4]:
            sect.add('meh')
            
        self.site2 = Site('testing')
        sect1 = Section('meh')
        sect2 = Section('blah')
        self.site2.add(sect1, inMenu=True)
        self.site2.add(sect2, inMenu=True)
            
        def lookAtPatterns():
            l = []
            for pattern in self.site.includes():
                l.append(pattern[0])
            return l
        
        def checkLengths(site, info=None, base=None, menu=None):
            if info:
                len(site.info) | should_be | info
            
            if base:
                len(site.base) | should.be | base
            
            if menu:
                [m for m in site.menu()] | should | have(menu).sections
        
        self.checkLengths = checkLengths
        self.lookAtPatterns = lookAtPatterns
    
    it 'should be possible to make a base section':
        base = self.site.makeBase()
        base.url | should.equal_to | ''
        self.site.base.stuff[0] | should.be | base
        self.checkLengths(self.site, base=1, info=0, menu=0)
        
        base = self.site.makeBase(inMenu=True)
        base.url | should.equal_to | ''
        self.site.base.stuff[0] | should.be | base
        self.checkLengths(self.site, base=1, info=0, menu=1)
    
    describe 'adding sections and sites':
            
        it 'should be possible to add one':
            self.site.add(self.sect1)
            
            self.checkLengths(self.site, info=1, base=0, menu=0)
            self.lookAtPatterns() | should.equal_to | ['^some/*']
            
        it 'should be possible to consecutively add more than one section':            
            self.site.add(self.sect1)
            self.site.add(self.sect2)
            self.site.add(self.sect3)
            self.site.add(self.sect4)
            
            self.checkLengths(self.site, info=4, base=0, menu=0)
            self.lookAtPatterns() | should.equal_to | ['^some/*', '^very/*', '^nice/*', '^place/*']
        
        it 'should be possible to add sections with different include names':            
            self.site.add(self.sect1, includeAs='blah')
            self.site.add(self.sect2)
            self.site.add(self.sect3, includeAs='meh')
            self.site.add(self.sect4)
            
            self.checkLengths(self.site, info=4, base=0, menu=0)
            self.lookAtPatterns() | should.equal_to | ['^blah/*', '^very/*', '^meh/*', '^place/*']
        
        it 'should be possible to add sections to menu when you add them':
            self.checkLengths(self.site, menu=0)       
            
            self.site.add(self.sect1, inMenu=True)
            self.site.add(self.sect2, inMenu=True)
            self.site.add(self.sect3, inMenu=True)
            self.site.add(self.sect4, inMenu=True)
            
            self.checkLengths(self.site, info=4, base=0, menu=4)
            [m for m in self.site.menu()] | should.equal_to | [self.sect1, self.sect2, self.sect3, self.sect4]
        
        it 'should be possible to add a section as a base':           
            self.site.add(self.sect1)
            self.site.add(self.sect2, base=True)
            self.site.add(self.sect3)
            self.site.add(self.sect4)
            
            self.checkLengths(self.site, info=3, base=1, menu=0)
            self.lookAtPatterns() | should.equal_to | ['^', '^some/*', '^nice/*', '^place/*']
            
        it 'should be possible to add a site as a base':           
            self.site.add(self.sect1)
            self.site.add(self.site2, base=True)
            self.site.add(self.sect3)
            self.site.add(self.sect4)
            
            self.checkLengths(self.site, info=3, base=1, menu=0)
            self.lookAtPatterns() | should.equal_to | ['^', '^some/*', '^nice/*', '^place/*']
        
        it 'should be possible to reorder a section by adding it again':           
            self.site.add(self.sect1, includeAs='blah')
            self.site.add(self.sect2)
            self.site.add(self.sect3, includeAs='meh')
            self.site.add(self.sect4)
            
            self.checkLengths(self.site, info=4, base=0, menu=0)
            self.lookAtPatterns() | should.equal_to | ['^blah/*', '^very/*', '^meh/*', '^place/*']
            
            self.site.add(self.sect2)
            self.checkLengths(self.site, info=4, base=0, menu=0)
            self.lookAtPatterns() | should.equal_to | ['^blah/*', '^meh/*', '^place/*', '^very/*']
            
            self.site.add(self.sect3, includeAs='meh')
            self.checkLengths(self.site, info=4, base=0, menu=0)
            self.lookAtPatterns() | should.equal_to | ['^blah/*', '^place/*', '^very/*', '^meh/*']
            
            self.site.add(self.sect3)
            self.checkLengths(self.site, info=5, base=0, menu=0)
            self.lookAtPatterns() | should.equal_to | ['^blah/*', '^place/*', '^very/*', '^meh/*', '^nice/*']
            
        it 'should be able to import a section from a string':
            self.site.add('urls.tests.fixture.sect1')
            self.checkLengths(self.site, info=1, base=0, menu=0)
            self.lookAtPatterns() | should.equal_to | ['^meh/*']
            
        it 'should be able to add a site from a string':
            self.site.add(site='urls.tests.fixture.theTestSite')
            self.checkLengths(self.site, info=1, base=0, menu=0)
            self.lookAtPatterns() | should.equal_to | ['^tester/*']
        
        it 'should be able to add all menu items from a site when adding it':
            self.checkLengths(self.site2, info=2, menu=2)
            
            self.site.add(site=self.site2, inMenu=True)
            self.checkLengths(self.site, info=1, menu=2)
    
    describe 'merging a site':
        it 'should be possible to merge the sections from one site into another':
            self.site.merge(self.site2)
            self.checkLengths(self.site, info=2, base=0, menu=0)
            
        it 'should be possible to merge the sections from one site into another including base':
            self.site2.makeBase()
            self.site.merge(self.site2)
            self.checkLengths(self.site, info=2, base=1, menu=0)
            
        it 'should be possible to merge the sections from one site into another without including base':
            self.site2.makeBase()
            self.site.merge(self.site2, keepBase=True)
            self.checkLengths(self.site, info=2, base=0, menu=0)
    
    describe 'patterns':
        it 'should not fail':
            self.site.patterns | should_not | throw(Exception)
            
        it 'should not fail when only a base section':
            self.site.makeBase()
            self.site.patterns | should_not | throw(Exception)
            
        it 'should not fail when only a base site':
            self.site.add(site=self.site2, base=True)
            self.site.patterns | should_not | throw(Exception)
        
        it 'should not fail when only sections':
            self.site.add(self.sect1)
            self.site.patterns | should_not | throw(Exception)
            
            self.sect1.adopt(self.sect2)
            self.site.patterns | should_not | throw(Exception)
            
            self.site.add(self.sect3)
            self.site.patterns | should_not | throw(Exception)
        
        it 'should not fail when only sites':
            self.site.add(site=self.site2)
            self.site.patterns | should_not | throw(Exception)
            
        it 'should not fail when a mixture of sites and sections and bases':
            self.site.makeBase()
            self.site.patterns | should_not | throw(Exception)
            
            self.site.add(self.sect1)
            self.site.patterns | should_not | throw(Exception)
            
            self.sect1.adopt(self.sect2)
            self.site.patterns | should_not | throw(Exception)
            
            self.site.add(site=self.site2)
            self.site.patterns | should_not | throw(Exception)
            
            self.site.add(site=self.site2, base=True)
            self.site.patterns | should_not | throw(Exception)
    
    describe 'paths1':
        before_each:
            self.site  = Site('site')
            self.site2 = Site('main')
            self.site3 = Site('other')
            
            self.s1 = Section('s1')
            self.s1_1 = self.s1.add('hello')
            
            self.site3.add(self.s1, includeAs='meh')
            self.site2.add(site=self.site3)
            self.site.add(site=self.site2)
            
        it 'should be able to split path for url to section beyond root ancestor':
            parentUrl, path, inside = self.site.getPath(self.s1_1.rootAncestor(), ['main', 'meh'])
            parentUrl | should.equal_to | ['main']
            path | should.equal_to | ['meh']
        
        it 'should be able to get path leading to a section':
            parentUrl = self.site.pathTo(self.s1)
            parentUrl | should.equal_to | ['main', 'other', 'meh']
    
    describe 'paths2':
        before_each:
            self.site  = Site('site')
            self.site2 = Site('main')
            self.site3 = Site('other')
            
            self.s1 = Section('s1')
            self.s1_1 = self.s1.add('hello')
            
            self.site3.add(self.s1, includeAs='meh')
            self.site2.add(site=self.site3)
            self.site.add(site=self.site2, base=True)
            
        it 'should be able to split path for url to section beyond root ancestor when bases involved':
            parentUrl, path, inside = self.site.getPath(self.s1_1.rootAncestor(), ['other', 'meh'])
            parentUrl | should.equal_to | ['other']
            path | should.equal_to | ['meh']
        
        it 'should be able to get path leading to a section when bases involved':
            parentUrl = self.site.pathTo(self.s1)
            parentUrl | should.equal_to | ['other', 'meh']
            
            
            
