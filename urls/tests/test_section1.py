# coding: spec

from urls.section import Values
                
def compare(x, y):
    if x > y:
        return -1
    elif x==y:
        return 0
    else: # x<y
        return 1
        
describe 'cwf Values':
        
    it 'should be able to store values as an iterable':
        v = Values([1,2,3])
        v.getValues([]) | should.equal_to | [(1, 1), (2, 2), (3, 3)]
        
        v = Values(xrange(3))
        v.getValues([]) | should.equal_to | [(0, 0), (1, 1), (2, 2)]
        
    it 'should be able to store values as a callable object return an iterable':
        v = Values(lambda p: [1,2,3])
        v.getValues([]) | should.equal_to | [(1, 1), (2, 2), (3, 3)]
        
        v = Values(lambda p: xrange(3))
        v.getValues([]) | should.equal_to | [(0, 0), (1, 1), (2, 2)]
        
    it 'should pass path into callable used to get values':
        v = Values(lambda p: p)
        v.getValues(['', 'some', 'path']) | should.equal_to | [('', ''), ('some', 'some'), ('path', 'path')]
        
    it 'should possible to remove duplicates':
        v = Values([1, 1, 2, 3, 4, 2, 2, 3], asSet=True)
        result = v.getValues([]) 
        result | should.include_all_of | [(1, 1), (2, 2), (3, 3), (4, 4)]
        result | should | have(4).elements
        
        v = Values(lambda p: [1, 1, 2, 3, 4, 2, 2, 3], asSet=True)
        result = v.getValues([]) 
        result | should.include_all_of | [(1, 1), (2, 2), (3, 3), (4, 4)]
        result | should | have(4).elements
        
    it 'should be possble to specify a transformation of values':
        v = Values([1, 2, 3], lambda p, v : ('%s_' % v, '__%s' % v))
        v.getValues([]) | should.equal_to | [('1_', '__1'), ('2_', '__2'), ('3_', '__3')]
    
    describe 'sorting values':
        it 'should be possible to specify sorting without a function':
            v = Values([4, 3, 2, 1], sorter=True)
            v.getValues([]) | should.equal_to | [(1, 1), (2, 2), (3, 3), (4, 4)]
            
        it 'should be possible to specify sorting with a function':
            v = Values([1, 2, 3, 4], sorter=compare)
            v.getValues([]) | should.equal_to | [(4, 4), (3, 3), (2, 2), (1, 1)]
        
        it 'should be possible to specify sorting before transformation':
            v = Values([1, 2, 3, 4], lambda p, v : (5-v, v), sorter=True, sortWithAlias=False)
            v.getValues([]) | should.equal_to | [(4, 1), (3, 2), (2, 3), (1, 4)]
            
        it 'should be possible to specify sorting after transformation':
            v = Values([1, 2, 3, 4], lambda p, v : (5-v, v), sorter=True, sortWithAlias=True)
            v.getValues([]) | should.equal_to | [(1, 4), (2, 3), (3, 2), (4, 1)]
        
        
        
        
        
        
        
        
        
        
        
        
        
        
    