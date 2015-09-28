'''
Three and OrderedTree data structures that are used to resolve methods from
function signatures.
'''

import collections


class Tree(object):

    '''A straightforward Tree implementation.'''

    __slots__ = []

    def __init__(self, head, tail=()):
        self.head = head
        self.tail = list(tail)

    def _subtree(self, value):
        return type(self)(value)

    def __getitem__(self, idx):
        if idx in [None, ()]:
            return self

        try:
            curr = self
            idx = list(idx)[::-1]
            while idx:
                curr = curr.tail[idx.pop()]
            return curr
        except TypeError:  # integer indices
            return self.tail[idx]

    def __repr__(self):
        tname = type(self).__name__
        N = len(self.tail)
        return '<%s (%r) with %s sub-trees>' % (tname, self.head, N)

    def pprint(self):
        '''Return a string with a pretty-printed version of the tree'''

        out = [str(self)]
        leaves = [(4 * len(i), i, x.head) for i, x in self.walkitems(True)]
        leaves = ['%s%r: %r' % (' ' * n, list(i), head) for
                  (n, i, head) in leaves]
        out.extend(leaves)
        return '\n'.join(out)

    def add(self, element):
        '''Adds a new element to the tree.'''

        sub = self._subtree(element)
        self.add_subtree(sub)

    def add_subtree(self, tree):
        '''Adds the given tree structure to tail'''

        self.tail.append(tree)

    def update(self, seq):
        '''Adds a sequence of elements to the tree'''

        for obj in seq:
            self.add(obj)

    def walk(self, ommit_self=False):
        '''Iterates through all the nodes (sub-trees) of the tree'''

        for _idx, node in self.walkitems(ommit_self):
            yield node

    def walkleaves(self, ommit_self=False):
        '''Iterates through all leaves of the tree.

        The leaves are the heads for each sub-node.'''

        return (node.head for node in self.walk(ommit_self))

    def walkitems(self, ommit_self=False, prefix=()):
        '''Iterates over tuples of (index, sub-tree) for all nodes in the
        tree. The index is a tuple that identifies each node in in the tree.
        '''

        if not ommit_self:
            yield prefix + (), self
        for i, x in enumerate(self.tail):
            for item in x.walkitems(prefix=prefix + (i,)):
                yield item


class OrderedTree(Tree):

    '''A partially ordered graph of objects with a single root.

    Each node has a `head` value and a list of `tail` and must be
    initialized with some ordering function.

    Examples
    --------

    Let us create a tree of types ordered by subclassing. We must put
    `object` as the root node since it has the smallest value.

    >>> tree = OrderedTree(issubclass, object)

    We can add new elements to the tree using the .add() and .update() methods.

    >>> tree.add(dict)
    >>> tree.update([collections.Mapping, list])

    These methods automatically put the objects in their correct positions in
    the tree graph. We may inspect using the pretty-printer

    >>> print(tree.pprint())                              # doctest: + ELLIPSIS
    <OrderedTree (<class 'object'>) with 2 sub-trees>
        [0]: <class '...Mapping'>
            [0, 0]: <class 'dict'>
        [1]: <class 'list'>

    Those indexes in square brackets represent the location of some given leaf
    in the tree. These can be used to access any sub-tree

    >>> tree[0, 0]
    <OrderedTree (<class 'dict'>) with 0 sub-trees>

    One can also inspect the future position of an element if it would be
    inserted into the tree.

    >>> tree.roots_of(collections.Sequence)
    [<OrderedTree (<class 'object'>) with 2 sub-trees>]

    >>> tree.tail_of(collections.Sequence)
    [<OrderedTree (<class 'list'>) with 0 sub-trees>]
    '''

    def __init__(self, ordering, head, tail=()):
        super().__init__(head, tail)
        self.ordering = ordering

    def _assure_higher(self, x):
        if not self.ordering(x.head, self.head):
            raise ValueError

    def _subtree(self, value):
        return type(self)(self.ordering, value)

    def add_subtree(self, tree):
        '''Adds a new sub-tree to the tree in its correct position'''

        head = tree.head
        ischild = self.ordering

        # Tests if it is a root to head
        if ischild(self.head, head):
            new_self = self._subtree(self.head)
            new_self.__dict__.update(self.__dict__)
            self.__dict__.clear()
            self.head = head
            self.tail = [new_self]
            return

        # Test if it has parents
        parents = [x for x in self.tail if ischild(head, x.head)]
        if parents:
            for parent in parents:
                parent.add_subtree(tree)
            return

        # Test if it is parent of some element
        tail = [x for x in self.tail if ischild(x.head, head)]
        self.tail.append(tree)
        if tail:
            for child in tail:
                self.tail.remove(child)
                tree.tail.append(child)

    def roots_of(self, element, force_single=False):
        '''Return a list with all nodes in the tree that can serve as a direct
        root to the given element.

        If ``force_single=True``, return the single root element or raise a
        ValueError if zero or more than one roots are found.
        '''

        ischild = self.ordering
        roots = set()
        if ischild(element, self.head):
            candidates = [self]
        else:
            candidates = None

        while candidates:
            subtree = candidates.pop()
            tail = subtree.tail
            parents = [x for x in tail if ischild(element, x.head)]
            if parents:
                candidates.extend(parents)
            else:
                roots.add(subtree)

        if force_single:
            if len(roots) != 1:
                raise ValueError('more than one root found', roots)
            return roots.pop()
        return list(roots)

    def tail_of(self, element):
        '''Return a list with all nodes in the tree that would be direct
        tail of the given element.
        '''

        ischild = self.ordering
        if ischild(self.head, element):
            return [self]

        roots = [self]
        tail = []

        while roots:
            subtree = roots.pop()
            if ischild(subtree.head, element):
                tail.append(subtree)
            else:
                roots.extend(subtree.tail)

        return tail

    def index(self, subtree):
        '''Return the index for some given sub-tree'''

        for index, sub in self.walkitems():
            if sub is subtree:
                return index
        raise IndexError('not found in tree: %r' % subtree)


class PosetMap(collections.MutableMapping):

    '''Wraps a partially ordered tree into a mapping.

    It behaves as a regular dict except when encountering a non-existing key.
    In this case, it uses the value associated with the direct root (or raises
    an error).


    Example
    -------

    The mapping must be initialized with at least one object and the ordering
    function

    >>> D = PosetMap(issubclass, {object: 'A'}); D
    PosetMap(issubclass, <class 'object'>: 'A')

    It works mostly as a regular dictionary, in which keys can be added,
    removed, iterated, etc. Non-existing keys, however, return the value
    assigned to its direct root in the tree graph.

    For example, let us populate the mapping with some number-related classes

    >>> from numbers import *
    >>> D[float] = 'B'
    >>> D[Number] = 'C'
    >>> D[Real] = 'D'
    >>> D[Integral] = 'E'

    It populates an ordered tree object under the hood, which is exposed in the
    ``.tree`` attribute.

    >>> print(D.tree.pprint())
    <OrderedTree (<class 'object'>) with 1 sub-trees>
        [0]: <class 'numbers.Number'>
            [0, 0]: <class 'numbers.Real'>
                [0, 0, 0]: <class 'float'>
                [0, 0, 1]: <class 'numbers.Integral'>

    If we ask for a key that is not present in the mapping, it uses the closest
    root node as a default value

    >>> D[int] is D[Integral]
    True
    '''

    def __init__(self, ordering, data):
        data = dict(data)
        key, value = data.popitem()
        self.tree = OrderedTree(ordering, key)
        self.tree.value = value

    def __repr__(self):
        try:
            func = self.tree.ordering.__name__
        except:
            func = '%s object' % type(self.tree.ordering).__name__
        data = ', '.join('%r: %r' % item for item in self.iteritems())
        return 'PosetMap(%s, %s)' % (func, data)

    def iteritems(self):
        for node in self.tree.walk():
            yield node.head, node.value

    def __delitem__(self, key):
        raise NotImplementedError

    def __getitem__(self, key):
        # Checks if key belongs to the tree
        for node in self.tree.walk():
            if node.head == key:
                return node.value

        # Uses the root as an approximation
        node = self.tree.roots_of(key, force_single=True)
        return node.value

    def __iter__(self):
        for k, _ in self.iteritems():
            yield k

    def __len__(self):
        return sum(1 for _ in self)

    def __contains__(self, key):
        for k in self:
            if k == key:
                return True
        return False

    def __setitem__(self, key, value):
        # Checks if key belongs to the tree and modify it
        for node in self.tree.walk():
            if node.head == key:
                node.value = value
                return

        subtree = OrderedTree(self.tree.ordering, key)
        subtree.value = value
        self.tree.add_subtree(subtree)

    def subkeys(self, key):
        '''Iterate over all keys in the mapping that are a subkey of the given
        key'''

        ischild = self.tree.ordering
        for k in self.tree.walk():
            if ischild(k.head, key):
                yield k.head


if __name__ == '__main__':
    import doctest
    doctest.testmod()
