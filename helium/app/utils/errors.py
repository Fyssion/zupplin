# from tornado.web import HTTPError


class AppError(Exception):
    ...


class JsonError(AppError):
    def __init__(self, status_code: int = 400, message: str = 'Invalid request') -> None:
        self.status_code = status_code
        self.message = message


class BadRequest(JsonError):
    def __init__(self, status_code: int = 400, message: str = 'Bad Request') -> None:
        super().__init__(status_code, message)


class InvalidBody(JsonError):
    def __init__(self, status_code: int = 400, message: str = 'Invalid body') -> None:
        super().__init__(status_code, message)


class NotFound(JsonError):
    def __init__(self, status_code: int = 404, message: str = 'NotFound') -> None:
        super().__init__(status_code, message)


class Unauthorized(JsonError):
    def __init__(self, status_code: int = 401, message: str = 'Unauthorized') -> None:
        super().__init__(status_code, message)


class InvalidMethod(JsonError):
    def __init__(self, status_code: int = 405, message: str = 'Invalid Method') -> None:
        super().__init__(status_code, message)


err = tuple[int, str]


class JSONError:
    INVALID_DATA: err = (1000, 'Invalid data')
