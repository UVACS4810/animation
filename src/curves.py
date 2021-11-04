
from src.utils import RGB
from src.vertex import Vertex

import src.vertex as vertex
import src.lines as lines
from src.utils import RGB

def make_permutations(x_initial, x, y_initial, y, color: RGB):
    v1 = Vertex(x_initial + x, y_initial + y, color.r, color.g, color.b, color.a)
    v2 = Vertex(x_initial + x, y_initial - y, color.r, color.g, color.b, color.a)
    v3 = Vertex(x_initial - x, y_initial + y, color.r, color.g, color.b, color.a)
    v4 = Vertex(x_initial - x, y_initial - y, color.r, color.g, color.b, color.a)
    v5 = Vertex(x_initial + y, y_initial + x, color.r, color.g, color.b, color.a)
    v6 = Vertex(x_initial + y, y_initial - x, color.r, color.g, color.b, color.a)
    v7 = Vertex(x_initial - y, y_initial + x, color.r, color.g, color.b, color.a)
    v8 = Vertex(x_initial - y, y_initial - x, color.r, color.g, color.b, color.a)
    
    return [v1, v2, v3, v4, v5, v6, v7, v8]
def draw_circle(x_initial: int, y_initial: int, radius: int, color: RGB) -> "list[vertex.Vertex]":
    x = -1 * radius
    y = 0
    p = -1 * radius - 1
    px = -8 * radius
    py = 4
    pxx = 8
    pyy = 8
    output = []
    while y <= -x:
        output += make_permutations(x_initial, x, y_initial, y, color)
        y += 1
        p += py
        py += pyy
        if p > 0:
            x += 1
            p += px
            px += pxx
    return output

def draw_bezier_point(points: "list[Vertex]", u: float):
    copy_points = list(map(lambda c: c.as_ndarray(), points))
    for k in range(1, len(points)):
        for i in range(0, len(points) - k):
            copy_points[i] = (1-u) * copy_points[i] + u * copy_points[i+1]
    bezier_point = vertex.ndarray_to_vertex(copy_points[0], is_rounded=False)
    return bezier_point

def draw_bezier_curve(points: "list[Vertex]", divisions: int = 1000) -> "list[Vertex]":
    curve_points = []
    for i in range(divisions):
        u = i/float(divisions-1)
        curve_points.append(draw_bezier_point(points, u))
    # draw lines between each of points on the curve
    verts = []
    for i in range(len(curve_points)-1):
        v1 = curve_points[i]
        v2 = curve_points[i+1]
        verts += lines.dda_on_vertex(v1, v2)
    return verts