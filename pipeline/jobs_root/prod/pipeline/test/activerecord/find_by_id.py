from foundation.activerecord.base import ActiveRecord

class Level(ActiveRecord):
    pass

level = Level.find(4)

print dir(level)

