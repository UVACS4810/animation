import copy

import numpy as np
from PIL import Image
from typing import Dict
import src.lines as lines
from src.objects import Object
import src.utils as utils
import src.vertex as vertex


def transform_vertex(point: vertex.Vertex, draw_data: utils.SceneData, objs: Dict[str, Object]) -> vertex.Vertex:
    """Ideas for this were taken from http://www.songho.ca/opengl/gl_transform.html

    Args:
        image (Image): The image we will add the pixel to
        point (vertex.Vertex): The point to be added
        draw_data (utils.DrawData): Data needed to draw the image
    """
    copy_point = copy.deepcopy(point)
    # Apply the model view transformations
    if objs[draw_data.curent_object].position_matrix is None:
        objs[draw_data.curent_object].make_position_matrix(objs)
    eye_coordinates: np.ndarray = np.matmul(objs[draw_data.curent_object].position_matrix, copy_point.position_data())
    # Apply the projection matrix
    clip_coordinates = np.matmul(draw_data.projection, eye_coordinates)
    # divide each x, y, and z by w
    copy_point.x = clip_coordinates[0] / clip_coordinates[3]
    copy_point.y = clip_coordinates[1] / clip_coordinates[3]
    copy_point.z = clip_coordinates[2] / clip_coordinates[3]
    copy_point.w = clip_coordinates[3]
    # apply a viewport transformation
    copy_point.x = (copy_point.x + 1) * draw_data.width/2
    copy_point.y = (copy_point.y + 1) * draw_data.height/2
    return copy_point

def draw_3d_triangle(image: Image, draw_data: utils.SceneData, objs: Dict[str, Object], i1: vertex.Vertex, i2: vertex.Vertex, i3: vertex.Vertex, gouraud: bool = False):
    # First, transform the vertexes provided
    p1 = transform_vertex(i1, draw_data, objs)
    p2 = transform_vertex(i2, draw_data, objs)
    p3 = transform_vertex(i3, draw_data, objs)

    # Rasterize the triangle into fragments, interpolating a z value 
    # (and other values as extras require) for each pixel. 
    verts: list[vertex.Vertex] = lines.triangle_fill(p1, p2, p3, width=draw_data.width, height=draw_data.height)
    # Only continue with those pixels that are on the screen and 
    # have z between 0 and 1. 
    for vert in verts:
        # check x
        if not 0 <= vert.x < draw_data.width:
            continue
        # check y
        if not 0 <= vert.y < draw_data.height:
            continue
        # check z bounds
        if not draw_data.near <= vert.z <= draw_data.far:
            continue
        # check depth buffer
        if draw_data.depth_buffer[(int(vert.y), int(vert.x))] < vert.z:
            continue
        # Set the pixel and depth buffer values
        pixel = vert.as_pixel()
        draw_data.depth_buffer[(pixel.y, pixel.x)] = vert.z
        if gouraud:
            color: utils.RGB = utils.RGB(pixel.r, pixel.g, pixel.b)
        else:
            color: utils.RGB = draw_data.color.as_rgb(rounded=True)

        image.im.putpixel((pixel.x, pixel.y), (color.r, color.g, color.b, color.a))
