from math import sqrt
def point_dist(p1, p2):
    x1, y1 = p1
    x2, y2 = p2
    return sqrt((x2-x1)**2 + (y2-y1)**2)

def get_closest_point(p1,p2,t):
    # using Pytagoras & quadratic function
    x1, y1 = p1
    x2, y2 = p2
    m = (y2 - y1) / (x2 - x1)
    b = y1 - m * x1
    alfa = m ** 2 + 1
    beta = 2 * (-x1 + m * (b - y1))
    teta = b ** 2 - 2 * b * y1 + x1 ** 2 + y1 ** 2 - t ** 2

    d = sqrt(beta ** 2 - 4 * alfa * teta)
    a = 2 * alfa
    x3_1 = -beta + d
    x3_1 /= a
    x3_2 = -beta - d
    x3_2 /= a

    if x3_1 >= x1 and x3_1 <= x2:
        y3_1 = m * x3_1 + b
        return (x3_1, y3_1)
    elif x3_2 > x1 and x3_2 < x2:
        y3_2 = m * x3_2 + b
        return (x3_2, y3_2)
    else:
        y3_1 = m * x3_1 + b
        y3_2 = m * x3_2 + b
        return (x3_1, y3_1), (x3_2, y3_2)

def get_closest_point2(p1,p2,t):
    # using vectors
    x1, y1 = p1
    x2, y2 = p2
    v1 = x2 - x1
    v2 = y2 - y1
    d = point_dist(p1, p2)
    e = t / d
    return x1 + e * v1, y1 + e * v2
