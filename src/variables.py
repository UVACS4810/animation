import abc
from typing import Dict, Union

class Variables():
    data: Dict[str, float] = {}
    def __init__(self, num_of_frames) -> None:
        self.data["l"] = num_of_frames
        self.data["f"] = 0
    def new_frame(self) -> None:
        cur_frame = self.data["f"] + 1
        num_of_frames = self.data["l"]
        self.data.clear()
        self.data["l"] = num_of_frames
        self.data["f"] = cur_frame
    def get_var(self, name: str) -> float:
        return self.data[name]
    def add_var(self, name: str, val: float):
        self.data[name] = val
    