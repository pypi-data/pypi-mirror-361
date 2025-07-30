import enum

class PTPMode(enum.Enum):
    JUMP_XYZ = 0
    MOVJ_XYZ = 1
    MOVL_XYZ = 2
    JUMP_ANGLE = 3
    MOVJ_ANGLE = 4
    MOVL_ANGLE = 5
    MOVJ_INC = 6
    MOVL_INC = 7
    MOVJ_XYZ_INC = 8
    JUMP_MOVL_XYZ = 9
