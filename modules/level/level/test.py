from level.controller import LevelController

def test():

    controller = LevelController()

    test = ["make", "job", "job_name"]
    controller.process_request(test)

    test = ["remove", "job", "job_name"]
    controller.process_request(test)


