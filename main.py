from typing import Dict
from src.vertex import Vertex
import sys

import src.file_parse as file_parse
import src.utils as utils
import src.variables as var
import src.objects as obj
def main():
    # get the file name
    args = sys.argv
    cmnd_line_args = utils.parse_args(args)

    # open the file
    with open(cmnd_line_args.file, "r") as file:
        lines = file.readlines()
        # Read the first line to determine meta info about the file
        first_line: str
        if lines:
            first_line = lines[0]
        else:
            print("not enough lines")
            raise
        
        # Get the image info from the first line
        image_info = file_parse.get_image_info(first_line)
        # Make array of images
        images = utils.make_images(image_info)
        image_filenames = utils.make_filename_list(image_info)
        # Initialize the structures needed to render the scene
        draw_data = utils.SceneData(
            vertex_list=[],
            height=image_info.height,
            width=image_info.width
        )
        variables = var.Variables(image_info.number_of_images)
        objects: Dict[str, obj.Object] = {}
        if len(lines) <= 1:
            raise Exception("Nothing to draw")
        for image in images:
            for i in range(1, len(lines)):
                line = utils.line_to_list(lines[i])
                if line:
                    file_parse.parse_line(line, image, draw_data, variables, objects)
            # Whipe the data of variables and objects
            objects.clear()
            variables.new_frame()
            draw_data.clear()
        assert(len(image_filenames) == len(images))
        # Save each of the files
        for i in range(len(image_filenames)):
            print(f"saving file {image_filenames[i]}")
            images[i].save(image_filenames[i])

# Main method
if __name__ == "__main__":
    main()
