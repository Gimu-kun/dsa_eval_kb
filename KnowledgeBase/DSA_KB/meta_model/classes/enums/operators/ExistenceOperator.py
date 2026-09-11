from enum import Enum


class ExistenceOperator(Enum):
    EXIST = "EXIST"
    NOT_EXIST = "NOT_EXIST"
    IS_NULL = "IS_NULL"
    NOT_NULL = "NOT_NULL"