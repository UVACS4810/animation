
import math

import numpy as np
from PIL import Image

import src.three_d as three_d
import src.utils as utils
from src.variables import Variables
import src.vertex as vertex


def get_image_info(line: str) -> utils.ImageInfo:
    """parses the first line of the file to get the metadata

    Args:
        line (str): the first line of a file

    Returns:
        ImageInfo: the input file metadata
    """
    line_as_list = utils.line_to_list(line)
    # Set the Image info
    image_info = utils.ImageInfo(
        width=int(line_as_list[1]),
        height=int(line_as_list[2]),
        filename=line_as_list[3],
    )
    # Set the values for the case in which we are making multiple png files
    if line_as_list[0] == "pngs":
        image_info.number_of_images = int(line_as_list[-1])

    return image_info

def get_vertex_by_index(verts, index: str) -> vertex.Vertex:
    if (index.strip("-")).isnumeric():
        index = int(index)
    else:
        raise Exception("The index of a vertex must be a number", index)
    # if its a negative index just use that idex
    if index < 0:
        return verts[index]
    return verts[index - 1]

def var_val(var: str, variables: Variables) -> float:
    if var.isdigit():
        return float(var)
    return variables.get_var(var)

def parse_line(line: "list[str]", image: Image, draw_data: utils.SceneData, variables: Variables) -> None:
    """
    parse keywords:
    """
    keyword: str = line[0]
    ### DRAW DATA UPDATES ###
    if keyword == "xyz":
        new_vertex: vertex.Vertex = vertex.Vertex(
            x=float(line[1]),
            y=float(line[2]),
            z=float(line[3]),
            r=draw_data.color.r,
            g=draw_data.color.g,
            b=draw_data.color.b,
            a=draw_data.color.a,
        )
        draw_data.vertex_list.append(new_vertex)

    elif keyword == "color":
        r = float(line[1])
        g = float(line[2])
        b = float(line[3])
        draw_data.color = utils.RGBFloat(r, g, b)

    elif keyword == "loadp":
        # Take the 1x16 list and turn it into a 4x4 ndarray
        draw_data.projection = np.asarray(line[1:], float).reshape(4,4)
    
    ### DRAWING TRIANGLES ###
    elif keyword == "trif":
        i1, i2, i3 = line[1:4]
        p1 = get_vertex_by_index(draw_data.vertex_list, i1)
        p2 = get_vertex_by_index(draw_data.vertex_list, i2)
        p3 = get_vertex_by_index(draw_data.vertex_list, i3)
        three_d.draw_3d_triangle(image, draw_data, p1, p2, p3)
    
    elif keyword == "trig":
        i1, i2, i3 = line[1:4]
        p1 = get_vertex_by_index(draw_data.vertex_list, i1)
        p2 = get_vertex_by_index(draw_data.vertex_list, i2)
        p3 = get_vertex_by_index(draw_data.vertex_list, i3)
        three_d.draw_3d_triangle(image, draw_data, p1, p2, p3, gouraud=True)
    
    elif keyword == "add":
        dest, a, b = line[1:4]
        a_val = var_val(a, variables)
        b_val = var_val(b, variables)
        variables.add_var(dest, a_val + b_val)
    elif keyword == "sub":
        dest, a, b = line[1:4]
        a_val = var_val(a, variables)
        b_val = var_val(b, variables)
        variables.add_var(dest, a_val - b_val)
    elif keyword == "mul":
        dest, a, b = line[1:4]
        a_val = var_val(a, variables)
        b_val = var_val(b, variables)
        variables.add_var(dest, a_val * b_val)
    elif keyword == "div":
        dest, a, b = line[1:4]
        a_val = var_val(a, variables)
        b_val = var_val(b, variables)
        variables.add_var(dest, a_val / b_val)
    elif keyword == "pow":
        dest, a, b = line[1:4]
        a_val = var_val(a, variables)
        b_val = var_val(b, variables)
        variables.add_var(dest, a_val ** b_val)
    elif keyword == "sin":
        dest, a= line[1:3]
        a_val = var_val(a, variables)
        variables.add_var(dest, math.sin(math.radians(a_val)))
    elif keyword == "cos":
        dest, a= line[1:3]
        a_val = var_val(a, variables)
        variables.add_var(dest, math.cos(math.radians(a_val)))
    elif keyword == "object":
        name, parent = line[1:3]
        
