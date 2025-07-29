from asgikit.asgi import AsgiException


class HttpException(AsgiException):
    pass


class ClientDisconnectError(HttpException):
    pass


class RequestBodyAlreadyConsumedError(HttpException):
    pass


class ResponseAlreadyStartedError(HttpException):
    pass


class ResponseNotStartedError(HttpException):
    pass


class ResponseAlreadyEndedError(HttpException):
    pass
