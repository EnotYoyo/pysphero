from pysphero.constants import Api2Error


class PySpheroException(Exception):
    ...


class PySpheroRuntimeError(RuntimeError):
    ...


class PySpheroTimeoutError(TimeoutError):
    ...


class PySpheroApiError(Exception):
    def __init__(self, api_error: Api2Error):
        super().__init__(f"Api reponse error: {api_error.name}")
