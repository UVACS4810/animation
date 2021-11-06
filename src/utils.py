import dataclasses
import math
from typing import Any, Optional
import enum

from PIL import Image
import numpy as np


@dataclasses.dataclass
class ImageInfo():
    """This contains all the the metadata about the image file the program is processing
    \b filename: the name of the output file
    \b width: the with of the output file
    \b height: the height of the output file
    \b is_single_file: true if filename should be used as output filename.
    \b number_of_images: the number of files that will be produced.
    """
    filename: str
    width: int
    height: int
    is_single_file: bool = True
    number_of_images: int = 1

@dataclasses.dataclass
class RGB():
    r: float
    g: float
    b: float
    a: float = 255
    def __add__(self, other):
        return RGB(
            min((self.r + other.r), 255),
            min((self.g + other.g), 255),
            min((self.b + other.b), 255),
            min((self.a + other.a), 255),
        )
    def round(self):
        self.r = round(self.r)
        self.g = round(self.g)
        self.b = round(self.b)
        self.a = round(self.a)
@dataclasses.dataclass
class RGBFloat():
    r: float
    g: float
    b: float
    a: float = 1.0

    def as_rgb(self, rounded = False) -> RGB:
        r = max(0, min(255, self.r * 255))
        g = max(0, min(255, self.g * 255))
        b = max(0, min(255, self.b * 255))
        a = max(0, min(255, self.a * 255))
        if rounded:
            return RGB(round(r), round(g), round(b), round(a))
        else:
            return RGB(r, g, b, a)

class IfState(enum.Enum):
    NOI = 1 # No if statement available
    TII = 2 # True and in If statement
    FII = 3 # False and in if statement
    TIE = 4 # True and in else statement
    FIE = 5 # False and in else statement

@dataclasses.dataclass
class SceneData():
    """contains information that will need to last for the lifecycle of the image
    """
    vertex_list: list
    height: int
    width: int
    projection: np.ndarray = np.identity(4)
    color: RGBFloat = RGBFloat(1.0, 1.0, 1.0)
    near = 0
    far = 1
    if_state: IfState = IfState.NOI
    curent_object: Optional[str] = None
    depth_buffer: np.ndarray = dataclasses.field(init=False)
    def __post_init__(self):
        self.depth_buffer = np.ones((self.height, self.width))

    def clear(self):
        """Used to wipe info that will not cary over to the next image in the animation
        """
        self.vertex_list.clear()
        self.projection = np.identity(4)
        self.color = RGBFloat(1.0, 1.0, 1.0)
        self.depth_buffer = np.ones((self.height, self.width))
        self.if_state = IfState.NOI

def over_operator(ca: int, cb: int, aa: int, ab, a0: int) -> int:
    return round((ca * aa + cb*ab*(1-aa))/a0)

def add_pixel_colors(a: RGB, b: RGB) -> RGB:
    """Used to compute the new color of two pixels with alpha values. Uses the over
    operator to acomplish this

    Args:
        a (RGB): the over color
        b (RGB): the under color

    Returns:
        RGB: the new pixel color
    """
    aa = a.a/255
    ab = b.a/255
    a0 = aa + ab * (1-(aa))

    r = over_operator(a.r, b.r, aa, ab, a0)
    g = over_operator(a.g, b.g, aa, ab, a0)
    b = over_operator(a.b, b.b, aa, ab, a0)

    a0 = round(a0*255)
    return RGB(r, g, b, a0)

def convert_hex_to_rgb(hex: str) -> RGB:
    # we will get the "hex" value in the form "#rrggbb"
    # The first step will be to strip the "#" char.
    hex = hex.strip("#")
    # Next we will seperate the string into "rr" "gg" "bb"
    # Convert the values into integers
    rr = int(hex[0:2], base=16)
    gg = int(hex[2:4], base=16)
    bb = int(hex[4:6], base=16)
    aa = 255
    if len(hex) > 6:
        aa = int(hex[6:8], base=16)
    # store the values in an RGB class
    return RGB(rr, gg, bb, aa)

def line_to_list(line: str) -> "list[str]":
    # remove whitespace
    line.strip()
    return line.split()

def object_to_list(object) -> "list[Any]":
    vars_dict: dict = vars(object)
    output_list = []
    for key, val in vars_dict.items():
        if dataclasses.is_dataclass(val):
            vars_dict[key] = object_to_list(val)
            for item in object_to_list(val):
                output_list.append(item)
        else:
            output_list.append(val)
    return output_list


### STUFF FOR ARG PARSING ###
@dataclasses.dataclass
class CmdLineArgs():
    file: str

def parse_args(args: list) -> CmdLineArgs:
    return CmdLineArgs(file = args[1])

def make_filename_list(image_info: ImageInfo) -> "list[str]":
    # List of names for image files
    names_list = []
    # if image_info.is_single_file:
    #     names_list.append(image_info.filename)
    # else:
    for i in range(image_info.number_of_images):
        name = image_info.filename + f"{i:03d}" + ".png"
        names_list.append(name)
    return names_list


### MAKING IMAGES ###
def make_images(image_info: ImageInfo) -> list:
    images = []
    for _ in range(image_info.number_of_images):
        image = Image.new("RGBA", (image_info.width, image_info.height), (0,0,0,0))
        images.append(image)
    return images

### ORIENTATION CLASSES ###
@dataclasses.dataclass
class Vec3():
    x: float = 0
    y: float = 0
    z: float = 0
    def __array__(self, dtype=None):
        return np.asarray([self.x, self.y, self.z])


@dataclasses.dataclass
class Quaternion():
    w: float = 1
    x: float = 0
    y: float = 0
    z: float = 0

    def __array__(self, dtype=None):
        return np.asarray([self.w, self.x, self.y, self.z])
    
    def make_rotation(self) -> np.ndarray:
        n = self.w**2 + self.x**2 + self.y**2 + self.z**2
        s = 0 if n == 0 else 2/n
        row_0 = [
            1-s*(self.y**2 + self.z**2),
            s*(self.x*self.y - self.z*self.w),
            s*(self.x*self.z + self.y*self.w),
            0
        ]
        row_1 = [
            s*(self.x*self.y + self.z*self.w),
            1-s*(self.x**2 + self.z**2),
            s*(self.y*self.z - self.x*self.w),
            0
        ]
        row_2 = [
            s*(self.x*self.z - self.y*self.w),
            s*(self.y*self.z + self.x*self.w),
            1-s*(self.x**2 + self.y**2),
            0
        ]
        row_3 = [0,0,0,1]
        return np.asarray([row_0, row_1, row_2, row_3])

@dataclasses.dataclass
class Euler():
    """an alternative representation of the orientation of an object.

    \b `order` = The order of the rotations given by the xyz argument, which
    will contain three letters (x, y, and z) in an arbitrary order 
    (e.g. yxz or zxy or …)

    \b `first`, `second`, `third` = rotate the object `x` degrees around the 
    axis given by the corresponding letter in `order`
    """
    # rotation matrix code from https://www.meccanismocomplesso.org/en/3d-rotations-and-euler-angles-in-python/
    order: str = "xyz"
    first: float = 0
    second: float = 0
    third: float = 0

    def __array__(self, dtype=None):
        return np.asarray([self.x, self.y, self.z])
    
    def make_rotation(self) -> np.ndarray:
        rot = np.identity(4)
        for i, val in enumerate([self.first, self.second, self.third]):
            if self.order[i] == "x":
                rot = np.matmul(rot, self._rot_x(val))
            elif self.order[i] == "y":
                rot = np.matmul(rot, self._rot_y(val))
            elif self.order[i] == "z":
                rot = np.matmul(rot, self._rot_z(val))
        return rot
    def _rot_x(self,theta):
        theta = math.radians(theta)
        return np.asarray([[ 1, 0              , 0              , 0],
                           [ 0, math.cos(theta),-math.sin(theta), 0],
                           [ 0, math.sin(theta), math.cos(theta), 0],
                           [ 0, 0              ,0               , 1]])
        
    def _rot_y(self,theta):
        theta = math.radians(theta)
        return np.asarray([[ math.cos(theta), 0, math.sin(theta), 0],
                           [ 0              , 1, 0              , 0],
                           [-math.sin(theta), 0, math.cos(theta), 0],
                           [ 0              , 0, 0              , 1]])
        
    def _rot_z(self,theta):
        theta = math.radians(theta)
        return np.asarray([[ math.cos(theta), -math.sin(theta), 0, 0 ],
                           [ math.sin(theta), math.cos(theta) , 0, 0 ],
                           [ 0              , 0               , 1, 0 ],
                           [ 0              , 0               , 0, 1 ]])