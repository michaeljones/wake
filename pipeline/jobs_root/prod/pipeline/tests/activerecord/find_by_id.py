from foundation.activerecord.base import ActiveRecord

class Node(ActiveRecord):
    pass

node = Node.find(4)

print dir(node)

