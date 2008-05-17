from pipeline.interface.base import Interface
from pipeline.controller.base import FailedRequest
from pipeline.view.web import WebView

from mako.template import Template
from werkzeug import BaseRequest, BaseResponse
from werkzeug.routing import Map, Rule
from werkzeug.exceptions import HTTPException

import pipeline.utils
import sys
import os

class WebInterface(Interface):

    url_map = Map([])

    def process_request(self, environ, start_response):

        adapter = self.url_map.bind_to_environ(environ)

        try:
            endpoint, values = adapter.match()
            request = BaseRequest(environ)
            response = BaseResponse(mimetype='text/html')

            # response.data = environ["PATH_INFO"] 

            # return response

            try:
                method = getattr(self, endpoint)
            except AttributeError:
                raise HTTPException()

        except HTTPException, e:
            return e

        method(request, response, endpoint, values)

        view = WebView()
        module_name = self.__class__.__name__.replace("WebInterface", "").lower()

        self.content = view.execute(method.__name__, module_name, self.__dict__)

        filename = os.path.join(pipeline.utils.etc(), 'web', "layout.mako")

        try:
            mytemplate = Template(filename=filename)
        except IOError:
            sys.stderr.write("IO FAILURE!!")
            return 

        response.data = mytemplate.render(**self.__dict__)

        return response


