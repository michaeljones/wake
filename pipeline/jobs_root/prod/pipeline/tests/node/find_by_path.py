from pipeline.node import Node

tests = "bob bob:jim bob:jim:chris".split()

for entry in tests:

    node = Node.find_by_path(entry)

    print node.name
    try:
        print node.parent.name
    except AttributeError:
        print "no parent"



