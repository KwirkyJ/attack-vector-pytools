import unittest
import avt_gameplay_utils as avt
from decimal import Decimal
from math import pi, sin

class TestVectorToMovementGrid(unittest.TestCase) :
    def test_nominal_three_vectors(self) :
        vector = avt.Vector("6B 5C 3+")
        expected = [
            " |B|C|+|",
            " |0|0|0|",
            "1|*| | |",
            "2| |*|*|",
            "3|*|*| |",
            "4|*| |*|",
            "5| |*| |",
            "6|*|*| |",
            "7|*| |*|",
            "8|*|*| |",
        ]
        self.assertEqual('\n'.join(expected), vector.get_movement_grid())

    def test_one_h_one_v(self) :
        vector = avt.Vector("13A 1-")
        expected = [
            " |A| |-|",
            " |1| |0|",
            "1| | |*|",
            "2|*| | |",
            "3| | | |",
            "4|*| | |",
            "5|*| | |",
            "6| | | |",
            "7|*| | |",
            "8|*| | |",
        ]
        self.assertEqual('\n'.join(expected), vector.get_movement_grid())

    def test_one_v(self) :
        vector = avt.Vector("8-")
        expected = [
            " | | |-|",
            " | | |1|",
            "1| | | |",
            "2| | | |",
            "3| | | |",
            "4| | | |",
            "5| | | |",
            "6| | | |",
            "7| | | |",
            "8| | | |",
        ]
        self.assertEqual('\n'.join(expected), vector.get_movement_grid())

    def test_one_h(self) :
        vector = avt.Vector("7F")
        expected = [
            " |F| | |",
            " |0| | |",
            "1| | | |",
            "2|*| | |",
            "3|*| | |",
            "4|*| | |",
            "5|*| | |",
            "6|*| | |",
            "7|*| | |",
            "8|*| | |",
        ]
        self.assertEqual('\n'.join(expected), vector.get_movement_grid())

    def test_opposites_h(self) :
        vector = avt.Vector("6F 3D 1-")
        self.assertEqual("3E 3F 1-", str(vector))
        expected = [
            " |E|F|-|",
            " |0|0|0|",
            "1| | |*|",
            "2|*| | |",
            "3| |*| |",
            "4|*| | |",
            "5| | | |",
            "6| |*| |",
            "7|*| | |",
            "8| |*| |",
        ]
        self.assertEqual('\n'.join(expected), vector.get_movement_grid())

    def test_three_h(self) :
        vector = avt.Vector("6F 3D 1A")
        self.assertEqual("4F 2E", str(vector))
        expected = [
            " |F|E| |",
            " |0|0| |",
            "1| | | |",
            "2|*| | |",
            "3|*| | |",
            "4| |*| |",
            "5| | | |",
            "6|*| | |",
            "7|*| | |",
            "8| |*| |",
        ]
        self.assertEqual('\n'.join(expected), vector.get_movement_grid())

    def test_menagerie(self) :
        vector = avt.Vector("9+ 6F 3D 1A 2-")
        self.assertEqual("4F 2E 7+", str(vector))
        expected = [
            " |F|E|+|",
            " |0|0|0|",
            "1| | |*|",
            "2|*| |*|",
            "3|*| |*|",
            "4| |*|*|",
            "5| | |*|",
            "6|*| |*|",
            "7|*| |*|",
            "8| |*| |",
        ]
        self.assertEqual('\n'.join(expected), vector.get_movement_grid())

    def test_everything_cancels(self) :
        vector = avt.Vector("14F 14D 14A 14B 14C 14E 6- 6+")
        expected = "STILL"
        self.assertEqual(expected, vector.get_movement_grid())
# end TestVectorToMovementGrid

class TestVectorClassCreation(unittest.TestCase) :
    def test_zeroed_default(self) :
        vec = avt.Vector("")
        self.assertEqual("STILL", str(vec))

    def test_one_h(self) :
        vec = avt.Vector("22E")
        self.assertEqual("22E", str(vec))

    def test_two_case_insensitive(self) :
        vec = avt.Vector("18d 12c")
        self.assertEqual("18D 12C", str(vec))

    def test_two_h(self) :
        vec = avt.Vector("22F 8A")
        self.assertEqual("22F 8A", str(vec))

    def test_two_h_order_reversed(self) :
        vec = avt.Vector("4D 22E")
        self.assertEqual("22E 4D", str(vec))

    def test_two_h_opposites(self) :
        vec = avt.Vector("22E 8B")
        self.assertEqual("14E", str(vec))

    def test_two_h_opposites_cancel(self) :
        vec = avt.Vector("4F 4C")
        self.assertEqual("STILL", str(vec))

    def test_two_v_opposites(self) :
        vec = avt.Vector("8+ 3-")
        self.assertEqual("5+", str(vec))

    def test_two_h_120(self) :
        vec = avt.Vector("4F 3B")
        self.assertEqual("3A 1F", str(vec))

    def test_three_h_120(self) :
        vec = avt.Vector("4F 3B 1D")
        self.assertEqual("2A 1F", str(vec))

    def test_two_h_120_b(self) :
        vec = avt.Vector("4E 3A")
        self.assertEqual("3F 1E", str(vec))

    def test_menagerie(self) :
        vec = avt.Vector("14F 3B 6+ 10D 2- 4A 2C")
        self.assertEqual("6F 3E 4+", str(vec))
        self.assertEqual("UV+ (-9,3,4)", repr(vec))

    def test_duplicate_vectors_raise_error(self) :
        with self.assertRaises(ValueError) :
            vec = avt.Vector("4E 3A 7E")

    def test_duplicate_vertical_vectors_raise_error(self) :
        with self.assertRaises(ValueError) :
            vec = avt.Vector("4+ 4+ 3- 7E")

    def test_negative_value(self) :
        with self.assertRaises(ValueError) :
            vec = avt.Vector("-4E 3A")

    def test_invalid_direction(self) :
        with self.assertRaises(ValueError) :
            vec = avt.Vector("4J")

    def test_no_direction(self) :
        with self.assertRaises(ValueError) :
            vec = avt.Vector("3")

    def test_no_value(self) :
        with self.assertRaises(ValueError) :
            vec = avt.Vector("A")
#end TestVectorClassCreation

class TestVectorClassMath(unittest.TestCase) :
    def test_add_stills(self) :
        v1 = avt.Vector("")
        v2 = avt.Vector("")
        self.assertEqual("STILL", str(v1+v2))
        self.assertEqual("STILL", str(v1))
        self.assertEqual("STILL", str(v2))

    def test_add_still_to_moving(self) :
        v1 = avt.Vector("3F 2-")
        v2 = avt.Vector("")
        self.assertEqual("3F 2-", str(v1+v2))
        self.assertEqual("3F 2-", str(v1))
        self.assertEqual("STILL", str(v2))

    def test_add_moving_to_still(self) :
        v1 = avt.Vector("")
        v2 = avt.Vector("3F 2-")
        self.assertEqual("3F 2-", str(v1+v2))
        self.assertEqual("STILL", str(v1))
        self.assertEqual("3F 2-", str(v2))

    def test_add_two_movers(self) :
        v1 = avt.Vector("3F 2-")
        v2 = avt.Vector("5D 3E 1+")
        self.assertEqual("6E 2D 1-", str(v1+v2))
        self.assertEqual("3F 2-", str(v1))
        self.assertEqual("5D 3E 1+", str(v2))

    def test_subtract_stills(self) :
        v1 = avt.Vector("")
        v2 = avt.Vector("")
        self.assertEqual("STILL", str(v1-v2))
        self.assertEqual("STILL", str(v1))
        self.assertEqual("STILL", str(v2))

    def test_subtract_still_from_moving(self) :
        v1 = avt.Vector("3F 2-")
        v2 = avt.Vector("")
        self.assertEqual("3F 2-", str(v1-v2))
        self.assertEqual("3F 2-", str(v1))
        self.assertEqual("STILL", str(v2))

    def test_subtract_moving_from_still(self) :
        v1 = avt.Vector("")
        v2 = avt.Vector("3f 2-")
        self.assertEqual("3C 2+", str(v1-v2))
        self.assertEqual("STILL", str(v1))
        self.assertEqual("3F 2-", str(v2))

    def test_subtract_two_movers(self) :
        v1 = avt.Vector("3F 2-")
        v2 = avt.Vector("5D 3E 1+")
        self.assertEqual("8A 3-", str(v1-v2))
        self.assertEqual("3F 2-", str(v1))
        self.assertEqual("5D 3E 1+", str(v2))
#end TestVectorClassMath

class TestVectorClassToBearing(unittest.TestCase) :
    def test_static(self) :
        self.assertEqual("NONE", avt.Vector("").to_bearing())

    def test_23B(self) :
        self.assertEqual("23 B", avt.Vector("23B").to_bearing())

    def test_8D_5C(self) :
        self.assertEqual("11 C/D", avt.Vector("8D 5C").to_bearing())

    def test_5D_8C_rawcount(self) :
        self.assertEqual("13 C/D", avt.Vector("8C 5D").to_bearing(count=True))

    def test_8up(self) :
        self.assertEqual("8 +++", avt.Vector("8+").to_bearing())

    def test_4down(self) :
        self.assertEqual("4 ---", avt.Vector("4-").to_bearing(count=True))

    def test_5D_8C_12up(self) :
        self.assertEqual("17 C/D++", avt.Vector("8C 5D 12+").to_bearing())

    def test_12E_14up(self) :
        self.assertEqual("18 E++", avt.Vector("12E 14+").to_bearing())

    def test_2A_12down(self) :
        self.assertEqual("12 ---", avt.Vector("2A 12-").to_bearing())
#end TestVectorClassToBearing

class TestVectorClassToCartesian(unittest.TestCase) :
    sin60 = Decimal(sin(pi/3))

    def test_static(self) :
        self.assertEqual(
                {'x':Decimal(0), 'y':Decimal(0), 'z':Decimal(0)},
                avt.Vector("").to_cartesian())

    def test_3f_7a_2up(self) :
        self.assertEqual(
                {   'x':Decimal('-3') * self.sin60,
                    'y':Decimal('8.5'),
                    'z':Decimal(2)
                },
                avt.Vector("3f 7a 2+").to_cartesian())
#end TestVectorClassToCartesian

class TestGetBearingFromCoords(unittest.TestCase) :
    pass
#end TestGetBearingFromCoords

class TestGetBearingVectorFromTile(unittest.TestCase) :
    def setUp(self) :
        avt.SET_TILE_RADIUS(8)

    def tearDown(self) :
        avt.SET_TILE_RADIUS(8)

    def test_same_corner(self) :
        v = avt.get_bearing_vector_from_tile(3,2,8,0,-3, 4,1,0,16,-3)
        self.assertEqual("STILL", str(v))
        self.assertEqual("NONE", v.to_bearing())

    def test_in_same_tile(self) :
        v = avt.get_bearing_vector_from_tile(-3,2,4,9,4, -3,2,15,5,0)
        self.assertEqual("7C 4B 4-", str(v))
        self.assertEqual("10 B/C-", v.to_bearing())

    def test_big_gap(self) :
        v = avt.get_bearing_vector_from_tile(3,2,4,13,-3, -1,7,9,2,3)
        self.assertEqual("42D 19E 6+", str(v))
        self.assertEqual("54 D/E", v.to_bearing())

    def test_big_vertical(self) :
        v = avt.get_bearing_vector_from_tile(0,7,4,11,-13, -1,7,9,6,17)
        self.assertEqual("8F 3E 30+", str(v))
        self.assertEqual("32 E/F++", v.to_bearing())

    def test_different_radius(self) :
        avt.SET_TILE_RADIUS(6)
        v = avt.get_bearing_vector_from_tile(2,3,4,4,3, 3,4,8,6,8)
        self.assertEqual("22C 2D 5+", str(v))
        self.assertEqual("24 C", v.to_bearing())
#end TestGetBearingVectorFromTile

class TestGetBearingFromGrid(unittest.TestCase) :
    pass
#end TestGetBearingFromGrid

class TestCV(unittest.TestCase) :
    def test_example(self) :
        self.assertEqual("15 E/F", avt.cv('8a 9b', '8f 12a 2+'))
#end TestCV

class TestMovement(unittest.TestCase) :
    def test_example(self) :
        self.assertEqual(
                '\n'.join([
                    "4F 2E 7+",
                    "",
                    " |F|E|+|",
                    " |0|0|0|",
                    "1| | |*|",
                    "2|*| |*|",
                    "3|*| |*|",
                    "4| |*|*|",
                    "5| | |*|",
                    "6|*| |*|",
                    "7|*| |*|",
                    "8| |*| |",
                ]),
                avt.movement("9+ 6F 3D 1A 2-"))
#end TestMovement

class TestAVID(unittest.TestCase) :
    def test_creation(self) :
        examples = [
            ("+++",   ( 0, 3), "+++",   "up"),
            ("---",   ( 0,-3), "---",   "down"),
            ("B/C-",  ( 3,-1), "B/C-",  "edge below"),
            ("F/A++", (11, 2), "F/A++", "edge angels-high"),
            ("C+",    ( 4, 1), "C+",    "cardinal above"),
            ("c/D+",  ( 5, 1), "C/D+",  "case-insensitive"),
            ("C/B--", ( 3,-2), "B/C--", "reversed cardinal directions"),
        ]
        for (label, id, window, msg) in examples :
            avid = avt.AVID(label)
            self.assertEqual(id, avid.to_tuple(), msg)
            self.assertEqual(window, str(avid), msg)

    def test_creation_errors(self) :
        examples = [
            "K",
            "B+++",
            "B*",
            "A/E",
            "AE",
            "++",
            "++++",
        ]
        for label in examples :
            with self.assertRaises(ValueError) :
                avt.AVID(label)

    def test_offset_ring_Fm_same(self) :
        avid = avt.AVID("F-")
        self.assertEqual(["F-"], avid.offset_ring(0))

    def test_offset_ring_Fm_opposite(self) : # F- -> A+
        avid = avt.AVID("F-")
        self.assertEqual(["C+"], avid.offset_ring(6))

    def test_offset_ring_Fp_ring(self) :
        expected = [
            "F++",
            "E/F++",
            "E/F+",
            "E/F",
            "F",
            "F/A",
            "F/A+",
            "F/A++",
        ]
        avid = avt.AVID("F+")
        self.assertEqual(expected, avid.offset_ring(1))

    def test_offset_ring_Fm_arbitrary(self) :
        expected =[
            "F+",
            "E/F+",
            "E+",
            "E",
            "E-",
            "E--",
            "---",
            "A--",
            "A-",
            "A",
            "A+",
            "F/A+",
        ]
        avid = avt.AVID("F-")
        self.assertEqual(expected, avid.offset_ring(2))

    def test_offset_ring_Bpp(self) :
        avid = avt.AVID("b++")
        self.assertEqual(["B++"], avid.offset_ring(0))
#end TestAVID

class TestShellstar(unittest.TestCase) :
    def test_run_away(self) :
        to_target = avt.Vector("6a")
        target_v  = avt.Vector("26a")
        self.assertEqual("No Shot", avt.shellstar(to_target, target_v, 24))

    def test_standstill(self) :
        expected = [
            "   +++",
            "F (D/E) C",
            "   ---",
            ">2/6 to evade",
            "+0 17",
            "+1 14",
            "+2 11",
            "+3 8",
            "+4 5",
            "+5 2",
            "+6 HIT",
            "RoC: 3",
        ]
        self.assertEqual(
                '\n'.join(expected),
                avt.shellstar(avt.Vector("13A 5B 4-"), avt.Vector(""), 24))

    def test_orthagonal(self) :
        expected = [
            "   +++",
            "E (C/D) B",
            "   ---",
            ">1/5 to evade",
            "0:4 13",
            "0:5 10",
            "0:6 7",
            "0:7 4",
            "0:8 1",
            "1:1 HIT",
            "RoC: 3",
        ]
        self.assertEqual(
                '\n'.join(expected),
                avt.shellstar(avt.Vector("13A"), avt.Vector("3E 3F"), 24, segment=4))

    def test_slow_closure(self) :
        expected = [
            "     D++",
            "B/C (A+) E/F",
            "     A--",
            ">2/8 to evade",
            "0:8 8",
            "1:1 8",
            "1:2 7",
            "1:3 6",
            "1:4 5",
            "1:5 3",
            "1:6 3",
            "1:7 1",
            "1:8 1",
            "2:1 0",
            "2:2 HIT",
            "RoC: 1",
        ]
        self.assertEqual(
                '\n'.join(expected),
                avt.shellstar(avt.Vector("4D 1E 7-"), avt.Vector("12D 4C 9-"), 24, segment=8))

    def test_vertical_impact_window(self) :
        expected = [
            "(---)",
            "Evade in Amber Ring",
            ">1/3 to evade",
            "+0 8",
            "+1 5",
            "+2 2",
            "+3 HIT",
            "RoC: 3",
        ]
        self.assertEqual(
                '\n'.join(expected),
                avt.shellstar(avt.Vector("4D 1E 7+"), avt.Vector("12A 3C"), 20))
#end TestShellstar

if __name__ == "__main__" :
    unittest.main()


