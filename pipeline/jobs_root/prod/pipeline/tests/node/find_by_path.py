from pipeline.level import Level

tests = "bob bob:jim bob:jim:chris".split()

for entry in tests:

    level = Level.find_by_path(entry)

    print level.name
    try:
        print level.parent.name
    except AttributeError:
        print "no parent"



