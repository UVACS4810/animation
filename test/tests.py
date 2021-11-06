from math import pi
import unittest

import numpy as np
import src.file_parse as file_parse
import src.lines as lines
import src.utils as utils
import src.vertex as vertex
import src.curves as curves
import src.variables as var
import src.objects as obj

class TestVertex(unittest.TestCase):
    def test_convert_vertex_to_list(self):
        r = 255
        g, b, x, y = 0, 0, 0, 0
        p1 = vertex.Vertex(x, y, r, g, b)
        p1_as_list = utils.object_to_list(p1)
        fields = [r, g, b, x, y]
        for field in fields:
            self.assertIn(field, p1_as_list)

    def test_as_ndarray(self):
        v = vertex.Vertex(1,1)
        l = [1,1,0,0,0]
        ll = np.array(l)
        self.assertEqual(ll.all(), v.as_ndarray().all())

class TestUtils(unittest.TestCase):
    def test_convert_hex_to_rgb(self):
        hex_color = "#aaaaff"
        rgb: utils.RGB = utils.RGB(170, 170, 255)
        self.assertEqual(utils.convert_hex_to_rgb(hex_color), rgb)

        hex_color = "#aaaaff01"
        rgb: utils.RGB = utils.RGB(170, 170, 255, 1)
        self.assertEqual(utils.convert_hex_to_rgb(hex_color), rgb)

    def test_add_RGB(self):
        c1 = utils.RGB(1, 1, 1)
        c2 = utils.RGB(1, 1, 1)
        expected = utils.RGB(2, 2, 2)
        self.assertEqual(c1 + c2, expected)
        # check overflow behavior

    def test_make_filename_list(self):
        # case with one image
        expected = ["whatnot.png"]
        image_info = utils.ImageInfo(filename="whatnot.png", width=1, height=1)
        self.assertEqual(expected, utils.make_filename_list(image_info=image_info))

        expected = ["whatnot000.png"]
        image_info.filename="whatnot"
        image_info.number_of_images= len(expected)
        image_info.is_single_file = False
        self.assertEqual(expected, utils.make_filename_list(image_info=image_info))

        # case with 5 images
        expected = [
            "whatnot000.png",
            "whatnot001.png",
            "whatnot002.png",
            "whatnot003.png",
            "whatnot004.png",
        ]
        image_info.number_of_images = len(expected)
        actual = utils.make_filename_list(image_info=image_info)
        self.assertEqual(expected, actual)

    def test_line_to_list(self):
        expected = ["xyrgb", "6" ,"3", "0", "0", "0"]
        lines: list(str) = [
            'xyrgb 6 3   0 0 0',
            "xyrgb 6 3 0 0 0",
            "   xyrgb 6 3 0 0      0",
            "xyrgb 6 3 0 0 0        ",
            "    xyrgb 6 3 0 0 0        ",
        ]
        for line in lines:
            out = utils.line_to_list(line)
            self.assertEqual(out, expected)
    def test_add_add_pixl_colors(self):
        # The top pixel should take precidence when it has a full opacity
        c1 = utils.RGB(255, 255, 0, 255)
        c2 = utils.RGB(255, 0, 0, 255)
        c_result = utils.add_pixel_colors(c1, c2)
        self.assertEqual(c_result, c1)

        # The bottom pixel will take precidence when the top pixel has no opacity
        c1 = utils.RGB(255, 255, 0, 0)
        c2 = utils.RGB(255, 0, 0, 255)
        c_result = utils.add_pixel_colors(c1, c2)
        self.assertEqual(c_result, c2)

        # When they are mixed it is a little harder to determine
        c1 = utils.RGB(100, 100, 100, 100)
        c2 = utils.RGB(100, 100, 100, 100)
        expected = utils.RGB(100, 100,100, 161)
        c_result = utils.add_pixel_colors(c1, c2)
        self.assertEqual(c_result, expected)

    def test_convert_RGBFloat_to_RGB(self):
        old = utils.RGBFloat(1.0, 1.0, 1.0, 1)
        expeced = utils.RGB(255, 255,255)
        self.assertEqual(old.as_rgb(), expeced)

        old = utils.RGBFloat(1.1, 1.5, 2.0, 1)
        self.assertEqual(old.as_rgb(), expeced)

        old = utils.RGBFloat(-1.0, 5/255, 1000, 1)
        expeced = utils.RGB(0, 5, 255)
        self.assertEqual(old.as_rgb(), expeced)

    def test_draw_data_clear(self):
        draw_data_orig = utils.SceneData([], 1, 1)
        draw_data_updated = utils.SceneData([], 1, 1)
        draw_data_updated.color = utils.RGBFloat(1.1, 1.0, 1.0)
        draw_data_updated.projection = np.ones_like(draw_data_updated.projection)
        self.assertNotEqual(draw_data_orig.color, draw_data_updated.color)
        self.assertFalse(np.array_equal(draw_data_orig.projection, draw_data_updated.projection))
        draw_data_updated.clear()
        self.assertEqual(draw_data_orig.color, draw_data_updated.color)
        self.assertTrue(np.array_equal(draw_data_orig.projection, draw_data_updated.projection))

    def test_draw_data_init(self):
        h = 20
        w = 10
        dd = utils.SceneData([], h, w)
        expected_db = np.ones((h, w))
        self.assertEqual(np.shape(dd.depth_buffer), np.shape(expected_db))

    def test_quaternion(self):
        q = utils.Quaternion()
        self.assertTrue(np.array_equal(np.asarray(q), np.asarray([1,0,0,0])))
        expected_rot_mat = np.identity(4)
        self.assertTrue(np.array_equal(expected_rot_mat, q.make_rotation()))
        # rotation matrix values came from https://www.andre-gaschler.com/rotationconverter/
        q2 = utils.Quaternion(1, 1, 0, 0)
        expected_rot_mat = np.asarray([[1,0,0,0],[0,0,-1,0],[0,1,0,0],[0,0,0,1]])
        self.assertTrue(np.array_equiv(expected_rot_mat, q2.make_rotation()))

    def test_euler(self):
        e = utils.Euler("xyz", pi/2, -pi/2, pi/2)
        exp_rot_mat = np.asarray([[0,0,-1,0], [0,1,0,0], [1,0,0,0],[0,0,0,1]])
        self.assertTrue(np.array_equiv(exp_rot_mat, np.round(e.make_rotation(), 10)))

class TestLines(unittest.TestCase):
    def test_dda(self):
        # test to enseure that only the smaller endpoint will be included
        p1 = vertex.Vertex(10, 10)
        p2 = vertex.Vertex(20, 20)
        output = lines.dda_on_vertex(p1, p2)
        has_x_10: bool = False
        has_y_10: bool = False
        for out in output:
            if out.x == 10:
                has_x_10 = True
            if out.x == 20:
                self.fail("should not contain a vertex with x=20")
            if out.y == 10:
                has_y_10 = True
            if out.y == 20:
                self.fail("should not contain a vertex with y=20")
        self.assertTrue(has_x_10)
        self.assertTrue(has_y_10)

        # tests to ensure accuracy
        p1 = vertex.Vertex(0,0)
        p2 = vertex.Vertex(0,5)
        expected = [
            vertex.Vertex(0,0),
            vertex.Vertex(0,1),
            vertex.Vertex(0,2),
            vertex.Vertex(0,3),
            vertex.Vertex(0,4),
        ]
        actual = lines.dda_on_vertex(p1, p2)
        self.assertEqual(actual, expected)
        p1 = vertex.Vertex(0,.1)
        p2 = vertex.Vertex(0,5)
        expected = [
            vertex.Vertex(0,1),
            vertex.Vertex(0,2),
            vertex.Vertex(0,3),
            vertex.Vertex(0,4),
        ]
        actual = lines.dda_on_vertex(p1, p2)
        self.assertEqual(actual, expected)

        p1 = vertex.Vertex(0,0)
        p2 = vertex.Vertex(5,0)
        expected = [
            vertex.Vertex(0, 0),
            vertex.Vertex(1, 0),
            vertex.Vertex(2, 0),
            vertex.Vertex(3, 0),
            vertex.Vertex(4, 0),
        ]
        actual = lines.dda_on_vertex(p1, p2)
        self.assertEqual(actual, expected)

        p1 = vertex.Vertex(0,0)
        p2 = vertex.Vertex(0,0)
        expected = []
        actual = lines.dda_on_vertex(p1, p2)
        self.assertEqual(actual, expected)


    def test_triangle_fill(self):
        p1 = vertex.Vertex(1,1)
        p2 = vertex.Vertex(1,3)
        p3 = vertex.Vertex(3,1)
        t_points = lines.triangle_fill(p1,p2,p3)
        expected = [
            vertex.Vertex(x=1, y=1, r=0, g=0, b=0),
            vertex.Vertex(x=2, y=1, r=0, g=0, b=0),
            vertex.Vertex(x=1, y=2, r=0, g=0, b=0)
        ]
        self.assertEqual(t_points, expected)

    def test_triangle_fill_wil_zeroes(self):
        p1 = vertex.Vertex(0,0)
        p2 = vertex.Vertex(0,0)
        p3 = vertex.Vertex(0,0)
        t_points = lines.triangle_fill(p1,p2,p3)
        expected = []
        self.assertEqual(t_points, expected)

    def test_lerp(self):
        # Testing linear interpolation between np.ndarrays
        p1 = np.array([0,0,0,0])
        p2 = np.array([2,2,2,2])
        t = .5
        expected = np.array([1,1,1,1])
        real = lines.lerp(p1, p2, t)
        self.assertEqual(expected.all(), real.all())

        t = 1
        expected = np.array([2,2,2,2])
        real = lines.lerp(p1, p2, t)
        self.assertEqual(expected.all(), real.all())

        t = 0
        expected = np.array([0,0,0,0])
        real = lines.lerp(p1, p2, t)
        self.assertEqual(expected.all(), real.all())

class TestCurves(unittest.TestCase):
    def test_draw_bezier_point(self):
        p1 = vertex.Vertex(0,0)
        p2 = vertex.Vertex(2, 2)
        p3 = vertex.Vertex(4,4)
        p4 = vertex.Vertex(6,0)
        vertex_list = [p1,p2,p3,p4]
        result = curves.draw_bezier_point(vertex_list, .5)
        expected = vertex.Vertex(3.0, 2.25)
        self.assertEqual(result,expected)

class TestFileParse(unittest.TestCase):
    def test_add(self):
        lines = [
            ["add", "a", "f", "0"],
            ["add", "b", "f", "1"],
            ["add", "c", "b", "a"],
        ]
        frames = 5
        v = var.Variables(frames)
        exp = 1
        for _ in range(frames):
            for line in lines:
                file_parse.parse_line(line, None, None, v)
            self.assertEqual(v.get_var("c"), exp)
            exp += 2
            v.new_frame()
    
    def test_var_val(self):
        v = var.Variables(10)
        v.add_var("a", 4)
        val = file_parse.var_val("a", v)
        self.assertEqual(val, 4)
        v.add_var("-b", -2)
        val = file_parse.var_val("-b", v)
        self.assertEqual(val, -2)
        v.add_var("x5", 1)
        val = file_parse.var_val("x5", v)
        self.assertEqual(val, 1)
        d = "1"
        val = file_parse.var_val(d, v)
        self.assertEqual(val, float(d))
        d = "-1"
        val = file_parse.var_val(d, v)
        self.assertEqual(val, float(d))
        d = "-0.0"
        val = file_parse.var_val(d, v)
        self.assertEqual(val, float(d))
        d = ".11111"
        val = file_parse.var_val(d, v)
        self.assertEqual(val, float(d))
        d = "100e10"
        val = file_parse.var_val(d, v)
        self.assertEqual(val, float(d))


class TestObject(unittest.TestCase):
    def test_make_position_matrix(self):
        objects = {}
        o = obj.Object()
        objects["one"] = o
        self.assertFalse(o.position_matrix)
        o.make_position_matrix(objects)
        self.assertTrue(o.position_matrix.any())
        expected = np.identity(4)
        self.assertTrue(np.array_equiv(o.position_matrix, expected))

        o2 = obj.Object("one")
        objects["two"] = o2
        o2.origin = utils.Vec3(1,2,3)
        o2.scale = utils.Vec3(3,2,1)
        o2.make_position_matrix(objects)
        expected = np.asarray([[3,0,0,-2],[0,2,0,-2],[0,0,1,0],[0,0,0,1]])
        self.assertTrue(np.array_equiv(o2.position_matrix, expected))
    
    def test_transform_vertex(self):
        objects = {}
        o = obj.Object()
        objects["one"] = o
        o.position = utils.Vec3(1,2,3)
        vert_to_transform = vertex.Vertex(0,0,0)
        expected_after_transform = vertex.Vertex(1,2,3)
        real_after_transform = o.transform_vertex(vert_to_transform, objects)
        self.assertEqual(expected_after_transform, real_after_transform)
        