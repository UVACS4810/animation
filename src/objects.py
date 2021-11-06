
import dataclasses
from typing import Dict, Union
from PIL.Image import init
import numpy as np
import src.utils as utils
from src.vertex import Vertex

@dataclasses.dataclass
class Object():
    parent: str = "world"
    origin: utils.Vec3 = utils.Vec3()
    scale: utils.Vec3 = utils.Vec3(1,1,1)
    position: utils.Vec3 = utils.Vec3()
    orient: Union[utils.Quaternion, utils.Euler] = utils.Quaternion()
    geometry: list = dataclasses.field(init=False)
    position_matrix: np.ndarray = None

    def make_position_matrix(self, objs: Dict[str, "Object"]):
        # translation matrix moving (0,0,0) to the objects origin
        to_origin = np.identity(4)
        to_origin[:3,3] = np.asarray(self.origin)
        # translation matrix moving (0,0,0) to the object’s position
        to_position = np.identity(4)
        to_position[:3,3] = np.asarray(self.position)
        # a scaling matrix
        scaling = np.identity(4)
        scaling[0,0] = self.scale.x
        scaling[1,1] = self.scale.y
        scaling[2,2] = self.scale.z
        # R is a rotation matrix defined by the object’s orientation
        rot = self.orient.make_rotation()
        # inverse
        # translation matrix moving (0,0,0) to the objects origin
        to_origin_inverse = np.identity(4)
        to_origin_inverse[:3,3] = np.asarray([-self.origin.x, -self.origin.y, -self.origin.z])
        self.position_matrix = np.matmul(scaling, to_origin_inverse)
        self.position_matrix = np.matmul(rot,self.position_matrix)
        self.position_matrix = np.matmul(to_position, self.position_matrix)
        self.position_matrix = np.matmul(to_origin, self.position_matrix)
        # get the parent objects position_matrix
        if self.parent != "world":
            parent_obj = objs[self.parent]
            # Recursively make parent matrices
            if parent_obj.position_matrix is None:
                parent_obj.make_position_matrix(objs)
            self.position_matrix = np.matmul(parent_obj.position_matrix, self.position_matrix)
        
    def transform_vertex(self, v: Vertex, objs: Dict[str, "Object"]) -> Vertex:
        nv = v
        pos = np.asarray([nv.x, nv.y, nv.z, nv.w])
        if self.position_matrix is None:
            self.make_position_matrix(objs)
        # TODO: is this the way to 
        new_pos = np.matmul(self.position_matrix, pos)
        nv.x = new_pos[0]
        nv.y = new_pos[1]
        nv.z = new_pos[2]
        nv.w = new_pos[3]
        return nv
        
