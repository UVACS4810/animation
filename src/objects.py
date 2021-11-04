
import dataclasses
from typing import Union
from PIL.Image import init
import numpy as np
import src.utils as utils

@dataclasses.dataclass
class Object():
    parent: str = "world"
    origin: utils.Vec3 = utils.Vec3()
    scale: utils.Vec3 = utils.Vec3(1,1,1)
    position: utils.Vec3 = utils.Vec3()
    orient: Union[utils.Quaternion, utils.Euler] = utils.Quaternion()
    geometry: list = dataclasses.field(init=False)
    trans_matrix: np.ndarray = dataclasses.field(init=False)
    position_matrix: np.ndarray = dataclasses.field(init=False)

    def make_position_matrix(self):
        # translation matrix moving (0,0,0) to the objects origin
        to_origin = np.identity(4)
        to_origin[:3,3] = np.asarray(self.origin)
        # translation matrix moving (0,0,0) to the object’s position
        to_position = np.identity(4)
        to_position[:3,3] = np.asarray(self.position)
        # a scaling matrix
        
        # R is a rotation matrix defined by the object’s orientation