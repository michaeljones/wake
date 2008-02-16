
class ODIter(object):
    """
    Not in use
    """

    def __init__(self, odict): 
        self.index = -1
        self.odict = odict
        self.length = len(self.odict)

    def __iter__(self):
        return self

    def next(self):
        self.index += 1
        try: 
            key = self.odict._sequence[self.index]
            return (key, self.odict[key])
        except IndexError:
            raise StopIteration




class OrderedDict(dict):
    """ 
    Not in use
    """

    def __init__(self):

        dict.__init__(self)

        self._sequence = []

    def __setitem__(self, key, value):
        self._sequence.append(key)
        dict.__setitem__(self, key, value)


    def __getitem__(self, key):

        return dict.__getitem__(self, key)
        
    def __len__(self):
        return len(self._sequence)

    def __iter__(self):
        pass

    def iterkeys(self): 
        return iter(self._sequence)

    __iter__ = iterkeys

    def itervalues(self):
        pass

    def iteritems(self):
        return ODIter(self)



