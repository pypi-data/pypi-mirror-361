from urllib.parse import parse_qs

from .api import RouteMap
from .request.request import ReqType, RequestCtx
from .responses import NotFoundResponse


class WsgiDispatcher:
    """
    A WSGI dispatcher that handles requests and responses.
    """

    def __init__(self, route_map: RouteMap):
        self.route_map = route_map

    def __call__(self, environ, start_response):
        """
        Call the WSGI application with the given environment and start response.
        """
        query_params = parse_qs(environ.get("QUERY_STRING", ""))
        query_params = {k: v[0] for k, v in query_params.items()}
        path = environ.get("PATH_INFO", "/")
        reqctx = RequestCtx.new(
            ReqType(environ["REQUEST_METHOD"]),
            path,
            body=environ.get("wsgi.input"),
            headers={
                k.replace("HTTP_", ""): v
                for k, v in environ.items()
                if k.startswith("HTTP_")
            },
            query_params=query_params,
        )


        try:
            response = self.route_map.dispatch(reqctx)
        except KeyError:
            response = NotFoundResponse()

        start_response(
            str(response.code),
            response.headers.items(),
        )
        if isinstance(response.body, str):
            return [response.body.encode("utf-8")]
        elif hasattr(response.body, "model_dump_json"):
            return [response.body.model_dump_json().encode("utf-8")]
        else:
            raise ValueError("Response body must be a string or a Pydantic model.")
