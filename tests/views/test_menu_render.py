# coding: spec

from src.sections.section import Section
from src.sections.values import Values
from src.views.menu import Menu

import fudge

# Function to make a view that returns response
def make_view(response):
    def view(request, *args, **kwargs):
        res = HttpResponse(response)
        res.section = request.section
        return res
    return view

########################
###   URLS FOR TESTING
########################

section = Section('', name="templatetest")
section.first().configure(alias="Home")

    ########################
    ###   SECTION1

sect1 = section.add('one').configure(target=make_view("/one/"))
sect1_some = sect1.add('some').configure(alias='blah', target=make_view("/one/some/"))
sect1_blah = sect1.add('\w+').configure(
      match = 'blah'
    , target=make_view("/one/<blah>/")
    , values = Values(
        lambda info : ['2', '1', '3']
      , lambda info, value : ('%s_url' % value, 'alias_%s' % value)
      , sorter = True
      )
    )

    ########################
    ###   SECTION2

sect2 = section.add('2').configure(alias='two')
sect2_first = sect2.first().configure(alias='meh', target=make_view("/2/"))

sect2_1 = sect2.add('1').configure(target=make_view("/2/1/"))
sect2_1_1 = sect2_1.add('2').configure(active=False, target=make_view("/2/2/"))
sect2_1_2 = sect2_1.add('3').configure(target=make_view("/2/3/"))
sect2_1_2_1 = sect2_1_2.add('4').configure(target=make_view("/2/4/"))

    ########################
    ###   SECTION3

sect3 = section.add('3').configure(display=False, target=make_view("/3/"))
sect3.add('test1').configure(target=make_view("/3/test1"))

    ########################
    ###   SECTION4

sect4 = section.add('4').configure(target=make_view("/4/"), display=False, propogate_display=False)
sect4_1 = sect4.add('this').configure(target=make_view("/4/this/"))
sect4_2 = sect4.add('needs').configure(target=make_view("/4/needs/"))
sect4_4 = sect4.add('more').configure(target=make_view("/4/more/"))
sect4_5 = sect4.add('creativity').configure(target=make_view("/4/creativity/"))

sect4_2_1 = sect4_2.add('a').configure(target=make_view("/4/needs/a/"))
sect4_2_2 = sect4_2.add('path').configure(target=make_view("/4/needs/path/"))
sect4_2_3 = sect4_2.add('going').configure(target=make_view("/4/needs/going/"))
sect4_2_4 = sect4_2.add('somewhere').configure(target=make_view("/4/needs/somewhere/"))

sect4_2_2_1 = sect4_2_2.add('\w+').configure(
      values = Values(['1', '2', '3'], as_set=False)
    , target = make_view("/4/needs/path/\w+/")
    )

sect4_2_2_1_1 = sect4_2_2_1.add('meh').configure(target=make_view("/4/needs/path/\w+/meh/"))

sect4_4_1 = sect4_4.add('test').configure(target=make_view("/4/more/test/"))
sect4_4_2 = sect4_4.add('blah').configure(target=make_view("/4/more/blah/"))

########################
###   TESTS
########################

describe "Rendering the menu":
    before_each:
        self.section = section
        self.request = fudge.Fake("request")
        self.request.user = fudge.Fake("user")

    describe "Rendering Global":

        def lookat_global(self, section, path, desired):
            menu = type("Menu", (Menu, ), {'path' : path.split('/')})(self.request, section)
            rendered = menu.render(menu.global_nav(), 'menu/base.html')
            self.assertHTMLEqual(desired, rendered)
                
        it 'makes a global menu with base selected':
            self.lookat_global(self.section, "/", """
                <ul>
                    <li class="selected"><a href="/">Home</a></li>
                    <li><a href="/one">One</a></li>
                    <li><a href="/2">two</a></li>
                </ul>
            """)
        
        it 'makes a global menu with section other than base selected':
            self.lookat_global(self.section, "/one/", """
                <ul>
                    <li><a href="/">Home</a></li>
                    <li class="selected"><a href="/one">One</a></li>
                    <li><a href="/2">two</a></li>
                </ul>
                """)
        
        it 'is case insensitive':
            self.lookat_global(self.section, "/oNe/", """
                <ul>
                    <li><a href="/">Home</a></li>
                    <li class="selected"><a href="/one">One</a></li>
                    <li><a href="/2">two</a></li>
                </ul>
                """)
        
        it 'smakes global menu when the url is longer than selected section':
            self.lookat_global(self.section, "/one/some/", """
                <ul>
                    <li><a href="/">Home</a></li>
                    <li class="selected"><a href="/one">One</a></li>
                    <li><a href="/2">two</a></li>
                </ul>
                """)

    describe "Rendering side":

        def lookat_side(self, section, path, desired):
            menu = type("Menu", (Menu, ), {'path' : path.split('/')})(self.request, section)
            rendered = menu.render(menu.side_nav(), 'menu/base.html')
            print desired
            print '---'
            print rendered
            self.assertHTMLEqual(desired, rendered)

        it "knows which section to render from":
            self.lookat_side(self.section, "/one/", """
                <ul>
                    <li><a href="/one/some">blah</a></li>
                    <li><a href="/one/1_url">alias_1</a></li>
                    <li><a href="/one/2_url">alias_2</a></li>
                    <li><a href="/one/3_url">alias_3</a></li>
                </ul>
                """)
            
        it 'makes a heirarchial menu with values':
            site = Section(name='site')

            blah = site.add('blah')
            meh = blah.first().configure(alias='latest')
            
            b = blah.add('meh')
            b2 = b.add('\d{4}').configure(match='year', values=Values([2010, 2009], as_set=False))
            h = b2.add('\d+').configure(match='asdf', values=Values([1]))
            
            self.lookat_side(site, '/blah/meh/2010/1/', """
                <ul>
                    <li><a href="/blah/">latest</a></li>
                    <li class="selected">
                        <a href="/blah/meh">Meh</a>
                        <ul>
                            <li class="selected">
                                <a href="/blah/meh/2010">2010</a>
                                <ul>
                                    <li class="selected">
                                        <a href="/blah/meh/2010/1">1</a>
                                    </li>
                                </ul>
                            </li>
                            <li><a href="/blah/meh/2009">2009</a></li>
                        </ul>
                    </li>
                </ul>
                """)

            
    #         (menu, 'heirarchial') |should| render_as(desired)
                
    #     it 'should support sections with multiple values':
    #         menu = Menu(self.request, self.site, ['one', '1_'], self.sect1)
    #         desired = """
    #         <ul>
    #             <li><a href="/one/some">blah</a></li>
    #             <li class="selected"><a href="/one/1_">_1</a></li>
    #             <li><a href="/one/2_">_2</a></li>
    #             <li><a href="/one/3_">_3</a></li>
    #         </ul>
    #         """
            
    #         (menu, 'heirarchial') |should| render_as(desired)
                
    #     it 'should make a heirarchial menu and not include children when parent isnt selected':
    #         menu = Menu(self.request, self.site, ['2'], self.sect2)
    #         desired = """
    #         <ul>
    #             <li class="selected"><a href="/2">meh</a></li>
    #             <li><a href="/2/1">1</a></li>
    #         </ul>
    #         """
            
    #         (menu, 'heirarchial') |should| render_as(desired)
                
    #     it 'should make a heirarchial menu and do include children when parent is selected':
    #         menu = Menu(self.request, self.site, ['2', '1', '3', '4'], self.sect2)
    #         desired = """
    #         <ul>
    #             <li><a href="/2">meh</a></li>
    #             <li class="selected">
    #                 <a href="/2/1">1</a>
    #                 <ul>
    #                     <li class="selected">
    #                         <a href="/2/1/3">3</a>
    #                         <ul>
    #                             <li class="selected"><a href="/2/1/3/4">4</a></li>
    #                         </ul>
    #                     </li>
    #                 </ul>
    #             </li>
    #         </ul>
    #         """
            
    #         (menu, 'heirarchial') |should| render_as(desired)
                
    #     it 'should not show sections that have display set to False':
    #         menu = Menu(self.request, self.site, ['3'], self.sect3)
    #         desired = ""
            
    #         (menu, 'heirarchial') |should| render_as(desired)
    
    # describe 'layered menu':
    #     it 'should be able to handle no selected section':
    #         menu = Menu(self.request, self.site, ['one'], self.sect1)
    #         desired = """
    #         <ul>
    #             <li><a href="/one/some">blah</a></li>
    #             <li><a href="/one/1_">_1</a></li>
    #             <li><a href="/one/2_">_2</a></li>
    #             <li><a href="/one/3_">_3</a></li>
    #         </ul>
    #         """
            
    #         (menu, 'layered') |should| render_as(desired)
        
    #     it 'should only create layers from children with selected parents':
    #         menu = Menu(self.request, self.site, ['2'], self.sect2)
    #         desired = """
    #         <ul>
    #             <li class="selected"><a href="/2">meh</a></li>
    #             <li><a href="/2/1">1</a></li>
    #         </ul>
    #         """
            
    #         (menu, 'layered') |should| render_as(desired)
                
    #     it 'should be able to make a layered menu':
    #         menu = Menu(self.request, self.site, ['4', 'needs', 'path', '2'], self.sect4)
    #         desired = """
    #         <ul>
    #             <li><a href="/4/this">This</a></li>
    #             <li class="selected"><a href="/4/needs">Needs</a></li>
    #             <li><a href="/4/more">More</a></li>
    #             <li><a href="/4/creativity">Creativity</a></li>
    #         </ul>
    #         <ul>
    #             <li><a href="/4/needs/a">A</a></li>
    #             <li class="selected"><a href="/4/needs/path">Path</a></li>
    #             <li><a href="/4/needs/going">Going</a></li>
    #             <li><a href="/4/needs/somewhere">Somewhere</a></li>
    #         </ul>
    #         <ul>
    #             <li><a href="/4/needs/path/1">1</a></li>
    #             <li class="selected"><a href="/4/needs/path/2">2</a></li>
    #             <li><a href="/4/needs/path/3">3</a></li>
    #         </ul>
    #         <ul>
    #             <li><a href="/4/needs/path/2/meh">Meh</a></li>
    #         </ul>
    #         """
            
    #         (menu, 'layered') |should| render_as(desired)
            
    #     it 'should not show sections that have display set to False':
    #         menu = Menu(self.request, self.site, ['3'], self.sect3)
    #         desired = ""
            
    #         (menu, 'layered') |should| render_as(desired)