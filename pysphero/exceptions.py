from pysphero.constants import Api2Error


class PySpheroException(Exception):
    ...


class PySpheroRuntimeError(PySpheroException):
    ...


class PySpheroTimeoutError(PySpheroException):
    ...


class PySpheroApiError(PySpheroException):
    def __init__(self, api_error: Api2Error):
        super().__init__(f"Api reponse error: {api_error.name}")


class PySpheroNotFoundError(PySpheroException):
    ...
