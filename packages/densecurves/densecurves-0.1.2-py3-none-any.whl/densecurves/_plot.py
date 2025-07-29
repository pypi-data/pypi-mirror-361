# 2D ###########################################################################

def plot(height: int, width: int, curve: callable) -> str:
    __grid = ''
    __pads = f'{{: {len(str(height * width)) + 1}}}'
    for __y in range(height):
        __l = ''.join(__pads.format(curve((__x, __y))) for __x in range(width))
        __grid += __l + '\n'
    return __grid
