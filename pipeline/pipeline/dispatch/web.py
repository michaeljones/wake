from werkzeug import BaseRequest, BaseResponse, SharedDataMiddleware, responder, DebuggedApplication
from werkzeug.routing import Map, Rule
from werkzeug.exceptions import HTTPException


url_map = Map([
    Rule('/', endpoint='index'),
    Rule('/<string:module>', endpoint='module_index'),
    Rule('/<string:module>/<path:remainder>', endpoint='module_method'),
])

def dispatch_request(environ, start_response):

    adapter = url_map.bind_to_environ(environ)
    endpoint, values = adapter.match()

    if endpoint == "index":
        try:
            endpoint, values = adapter.match()
            request = BaseRequest(environ)
            response = BaseResponse(mimetype='text/html')

            response.data = "Pipeline home page"

            return response

        except HTTPException, e:
            return e

    elif endpoint in ["module_method", "module_index"]:

        package_name = values["module"]
        module_name = package_name + ".interface.web"

        module = None
        try:
            module = __import__(module_name, globals(), locals(), [None])
        except ImportError, e:
            pipeline.report("Error - Unable to import module \"" + module_name + "\". Import error given:")
            pipeline.report("           %s" % e)
            return

        interface_name = package_name.capitalize() + "WebInterface" 

        InterfaceClass = None
        try:
            InterfaceClass = getattr(module, interface_name) 
        except AttributeError:
            pipeline.report("Error - Unable to find " + interface_name + " in module \"" + module_name + "\"")
            return
        
        interface = InterfaceClass()

        return interface.process_request(environ, start_response)



application = SharedDataMiddleware(responder(dispatch_request), {})
application = DebuggedApplication(application, evalex=True)




def local():
    from werkzeug import run_simple
    run_simple('localhost', 4000, application)


