import math

import numpy as np

import src.vertex as vertex
import src.utils as utils



def change_and_starting_position(p1: np.ndarray, p2: np.ndarray, step_in_y: bool = False, width: float = math.inf, height: float = math.inf) -> "list[np.ndarray]":
    delta_p: np.ndarray = p2 - p1
    # if delta y > delta x then we will step in y, else, step in x
    if not step_in_y:
        step_in_y = abs(delta_p[0]) < abs(delta_p[1])
    # set the step index
    # TODO: Is it ok to assume the first value will always be x and the second value will always be y?
    step_index: int = 1 if step_in_y else 0
    # We need to ensure that we are moving from a lower point to a higher point in our step directio
    if delta_p[step_index] < 0:
        # swap p1, p2
        p1, p2 = p2, p1
        # delta_p needs to be flipped
        delta_p = delta_p * -1
    # this is the amount that needs to be added to the previous point when we take a step in the step direction
    if delta_p[step_index] != 0:
        dp = delta_p / delta_p[step_index]
    else:
        dp = np.zeros(delta_p.shape)
    # the amount added to the initial point to get to the first int larger in the step direction
    dp0 = (math.ceil(p1[step_index]) - p1[step_index]) * dp if p1[step_index] > 0 else (0 - p1[step_index]) * dp
    # q is our starting point
    q: np.ndarray = p1 + dp0
    return [dp, q]

def dda(p1: np.ndarray, p2: np.ndarray, step_in_y: bool = False) -> "list[np.ndarray]":
    """Takes in two numpy arrays. Assumes that the first and second value in the arrays are
    x and y respectively. Setting the step_in_y flag will make sure the algorithm always 
    choses to step in y.
    width = the width of the screen to render the image on
    height = the height of the screen to render the image on
    Returns:
        np.ndarray: a numpy array where the first value is x and the second value is y
    """
    # this is the difference between the two points in all attributes
    delta_p = p2 - p1
    # if delta y > delta x then we will step in y, else, step in x
    if not step_in_y:
        step_in_y = abs(delta_p[0]) < abs(delta_p[1])
    # set the step index
    # TODO: Is it ok to assume the first value will always be x and the second value will always be y?
    step_index: int = 1 if step_in_y else 0
    # the edge where we will stop dda
    # We need to ensure that we are moving from a lower point to a higher point in our step directio
    if delta_p[step_index] < 0:
        # swap p1, p2
        p1, p2 = p2, p1
        # delta_p needs to be flipped
        delta_p = delta_p * -1
    # this is the amount that needs to be added to the previous point when we take a step in the step direction
    if delta_p[step_index] != 0:
        dp = delta_p / delta_p[step_index]
    else:
        dp = np.zeros(delta_p.shape)
    # the amount added to the initial point to get to the first int larger in the step direction
    dp0 = (math.ceil(p1[step_index]) - p1[step_index]) * dp
    
    # q is our starting point
    q: np.ndarray = p1 + dp0
    output_list: list[vertex.Vertex] = []
    while q[step_index] < p2[step_index]:
        output_list.append(q)
        # add the change to the current q
        q = q + dp
    return output_list

def triangle_fill(p1: vertex.Vertex, p2: vertex.Vertex, p3: vertex.Vertex, width: float = math.inf, height: float = math.inf) -> "list[vertex.Vertex]":
    # The first step is to order to 3 vertexes by their y coordinate.
    a = [p1, p2, p3]
    a.sort(key=lambda v: v.y)
    # convert a to a list of ndarrays
    a = list(map(lambda x: x.as_ndarray(), a))
    # bottom, middle, top
    pb, pm, pt = a
    # Find d~p and initial ~q for (~pb, ~pm); call them d~qa and ~qa
    dqa, qa = change_and_starting_position(pb, pm, True, width, height)
    # Find d~p and initial ~q for (~pb, ~pt); call them d~qc and ~qc
    dqc, qc = change_and_starting_position(pb, pt, True, width, height)
    output = []
    while qa[1] < pm[1] and qa[1] < height:
        output += dda(qa, qc)
        qa = qa + dqa
        qc = qc + dqc
    # Find d~p and initial ~q for (~pm, ~pt); call them d~qe and ~qe
    dqe, qe = change_and_starting_position(pm, pt, True, width, height)
    while qe[1] < pt[1] and qe[1] < height:
        output += dda(qe, qc)
        qe = qe + dqe
        qc = qc + dqc
    output = list(map(lambda x: vertex.ndarray_to_vertex(x, is_rounded=False), output))
    return output

def dda_on_vertex(p1: vertex.Vertex, p2: vertex.Vertex, step_in_y: bool = False) -> "list[vertex.Vertex]":
    p1_list: np.ndarray = np.array(utils.object_to_list(p1))
    p2_list: np.ndarray = np.array(utils.object_to_list(p2))
    dda_result = dda(p1_list, p2_list, step_in_y)
    output = list(map(vertex.ndarray_to_vertex, dda_result))
    return output

# performs linear interpolation between two np.ndarrays
def lerp(p1: np.ndarray, p2: np.ndarray, t: float) -> np.ndarray:
    """performs linear interpolation between two np.ndarrays

    Args:
        p1 (np.ndarray): point containing some collection of values
        p2 (np.ndarray): point containing some collection of values
        t (float): goes from 0.0 to 1.0

    Returns:
        np.ndarray: [description]
    """
    return p1 + ((p2 - p1) * t)
