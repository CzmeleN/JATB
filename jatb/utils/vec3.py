import ctypes as C

class Vec3(C.LittleEndianStructure):
    _pack_ = 1
    _fields_ = [("x", C.c_float), ("y", C.c_float), ("z", C.c_float)]

def vec3_to_tuple(v: Vec3) -> tuple[float, float, float]:
    return (v.x, v.y, v.z)

