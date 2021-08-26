# from enum import Enum


class AppError(Exception):
    ...


err = tuple[int, str]


class JSONError:
    INVALID_DATA: err = (1000, 'Invalid data')
