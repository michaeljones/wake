from pipeline.interface.web import WebInterface
from level.controller import LevelController
from optparse import OptionParser

from werkzeug.routing import Map, Rule

import sys

class LevelWebInterface(WebInterface):

    name = "Level"

    url_map = Map([
        Rule('/level/list', endpoint='list'),
        Rule('/level/list/<string:info>', endpoint='list_info'),
    ])

    def list(self, request, response, endpoint, values):

        self.info = "Testing"

        return response

    def list_info(self, request, response, endpoint, values):

        return response


