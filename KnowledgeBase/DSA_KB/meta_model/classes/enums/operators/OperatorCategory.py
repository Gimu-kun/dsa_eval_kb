from enum import Enum


class OperatorCategory(Enum):
    ARITHMETIC = "Arithmetic"
    COMPARISON = "Comparison"
    LOGICAL = "Logical"
    ASSIGNMENT = "Assignment"
    CONTROL_FLOW = "ControlFlow"
    ITERATION = "Iteration"
    DATA_ACCESS = "DataAccess"
    FUNC_CALL = "FuncCall"