"""
Gameplay aids for 'Attack Vector: Tactical'.

Functions:

    avt.movement(vector_string)
        Get 'pretty-formatted' string for movement grid.

    avt.shellstar(
            Vector_to_target,
            crossing_Vector,
            muzzle_velocity,
            segment=0)
        Generate seeker shellstar info.

Classes:
    Vector
"""

from math import floor, pi, sin, sqrt
from decimal import Decimal
import movement_grid_remainders as remainders

_CARDINAL_H = ['A', 'B', 'C', 'D', 'E', 'F']
_CARDINAL_V = ['+', '-']
_CARDINALS = _CARDINAL_H + _CARDINAL_V

_TILE_RADIUS = 8

def SET_TILE_RADIUS(r) :
    """Set radius used in tile computation."""
    #assert type(r) == int, "invalid radius type"
    #assert r%2 == 0, "radius must be even"
    #assert r > 0, "radius must be greater than zero"
    global _TILE_RADIUS
    _TILE_RADIUS = r

_SIN60 = Decimal(sin(pi/3))
_HALF_DECIMAL = Decimal('0.5')

def _uvp_from_vectors(vectors) :
    """Convert 'vectors' dictionary to U,V,+ dictionary."""
    uvp = {
        'U' : Decimal(0),
        'V' : Decimal(0),
    }
    if vectors['B'] != 0 :
        uvp['U'] += vectors['B']
        uvp['V'] -= vectors['B']
    if vectors['E'] != 0 :
        uvp['U'] -= vectors['E']
        uvp['V'] += vectors['E']
    uvp['V'] += vectors['D']
    uvp['V'] -= vectors['A']
    uvp['U'] += vectors['C']
    uvp['U'] -= vectors['F']
    uvp['+'] = Decimal(vectors['+'] - vectors['-'])
    return uvp
#end _uvp_from_vectors

def __place_in_vector(d, magnitude, pos_dir, neg_dir) :
    """Place integer `magnitude` in vector dict `d` by direction.

    If `magnitude` is positive, is placed in `d[pos_dir]`.
    If `magnitude` is negative, is placed in `d[neg_dir]`.
    """
    if magnitude > 0 :
        d[pos_dir] = magnitude
    elif magnitude < 0 :
        d[neg_dir] = -magnitude
#end __place_in_vector

def __consolidate_120(d, dccw, dir, d_cw) :
    """Consolidate vectors dictionary d.

    Given that `dir`, `d_cw`, and `dccw` are valid directions
    in the vector dictionary `d` (center, clockwise, and
    counterclockwise, respectively), if values in `d[dccw]` and 
    `d[d_cw]` are nonzero, subtract smaller from opposite and add
    smaller to `d[dir]`
    """
    v_cw = d[d_cw]
    vccw = d[dccw]
    lesser, greater = None, None
    if v_cw > 0 and vccw >= v_cw :
        greater = (vccw, dccw)
        lesser = (v_cw, d_cw)
    elif vccw > 0 and v_cw >= vccw :
        greater = (v_cw, d_cw)
        lesser = (vccw, dccw)
    if lesser is not None :
        d[dir] = lesser[0]
        d[lesser[1]] = Decimal(0)
        d[greater[1]] = greater[0] - lesser[0]
#end __consolidate_120

def _vectors_from_uvp(uvp) :
    """Convert "UV+" dictionary to a vector dictionary."""
    vectors = dict(zip(_CARDINALS, 
                       (Decimal(0) for _ in range(len(_CARDINALS)))))
    __place_in_vector(vectors, uvp['+'], '+', '-')
    __place_in_vector(vectors, uvp['U'], 'C', 'F')
    __place_in_vector(vectors, uvp['V'], 'D', 'A')
    __consolidate_120(vectors, 'A', 'B', 'C')
    __consolidate_120(vectors, 'D', 'E', 'F')
    return vectors
#end _vectors_from_uvp

class Vector :
    """Representation of velocity or position in hexagonal coordinates.

    Relies on AV:T's 'AVID' directions, (A, B, C, D, E, F, +, -) for
    user interaction, but converts to an intenal format for easier math.

    Created by (and interacts with user) through 'vector strings', each
    being either the empty string (""), indicating a zeroed vector,
    or a string containing a number of <number><direction> sequences
    separated by spaces, e.g. "5F", "4A 2C 6+", "1A 5d 2+ 3b 7- 6E".
    Note that case is unimportant in user input, but all output will be
    capitalized.

    Example instantiation: `vector_instance = avt.Vector("4A 2C 6+")`

    Basic arithmetic is supported for Vector instances, with addition and
    subtracting creating new Vector instances from the result.

    Python's built-in To-string method `str(<Vector>)` is supported,
    providing an instance's vector string.

    Vector instances have a number of useful routines:
        bearing()
            Get the (rounded) distance and AVID window of a Vector.
            Assumes relative to the zero vector.
        cartesian()
            Get a dictionary with 'X', 'Y', and 'Z' terms from Vector..
            Values are Decimal objects.
        movement_grid()
            Look up and format the movement grid for the Vector.
    """

    def __init__(self, vecstr) :
        """Create Vector instance from a vector string.

        Order and count of components is not important,
        e.g., "5F", "4A 2C 6+", "1A 5D 2+ 3B 7- 6E",
        as vectors are automatically normalized into at most two
        horizontal components adjacent to one another, and at most one
        vertical component.

        Raises ValueError if:
        + a number is negative
        + a duplicate direction is encountered
        + direction is not recognized

        Raises an error of some sort if `vecstr` is not a string.

        The empy string ("") returns the zero vector.
        """

        vectors = dict(zip(_CARDINALS, 
                           (Decimal(0) for _ in range(len(_CARDINALS)))))
        seen = []
        for elem in vecstr.strip().split() :
            num = int(elem[:-1])
            if num < 0 :
                raise ValueError("negative value {}".format(elem))
            dir = elem[-1].upper()
            if dir in seen :
                raise ValueError("duplicate direction {}".format(dir))
            if dir not in _CARDINALS :
                raise ValueError("invalid direction {}".format(dir))
            vectors[dir] = num
            seen.append(dir)
        self._uvp_vectors = _uvp_from_vectors(vectors)

    def __repr__(self) :
        """format in U,V,+ details"""
        return "UV+ ({},{},{})".format(
                self._uvp_vectors['U'],
                self._uvp_vectors['V'],
                self._uvp_vectors['+'])

    def _major_minor_vertical(self) :
        """return tuple of (magnitude, dirction) tuples

        if there are no suitable components, tuple has value of 0 and an
        undefined direction
        """
        vectors = _vectors_from_uvp(self._uvp_vectors)
        major = (Decimal(0), 'A')
        minor = (Decimal(0), 'A')
        vertical = (Decimal(0), '+')
        for dir in _CARDINAL_H :
            magnitude = vectors[dir]
            if magnitude > major[0] :
                if major[0] > minor[0] :
                    minor = major
                major = (magnitude, dir)
            elif magnitude > minor[0] :
                minor = (magnitude, dir)
        for dir in ['-', '+'] :
            magnitude = vectors[dir]
            if magnitude > vertical[0] :
                vertical = (magnitude, dir)
        return (major, minor, vertical)

    def __str__(self) :
        """Return formatted vector string with cardinal directions."""

        (major, minor, vertical) = self._major_minor_vertical()
        if major[0] == 0 :
            if vertical[0] == 0 :
                return "STILL"
            else :
                return "{}{}".format(vertical[0], vertical[1])
        else :
            arr = ["{}{}".format(major[0], major[1])]
            if minor[0] > 0 :
                arr.append("{}{}".format(minor[0], minor[1]))
            if vertical[0] > 0 :
                arr.append("{}{}".format(vertical[0], vertical[1]))
            return ' '.join(arr)

    def __add__(self, other) :
        uvp = dict()
        for k in ['U', 'V', '+'] :
            uvp[k] = self._uvp_vectors[k] + other._uvp_vectors[k]
        v = Vector("")
        v._uvp_vectors = uvp
        return v

    def __sub__(self, other) :
        uvp = dict()
        for k in ['U', 'V', '+'] :
            uvp[k] = self._uvp_vectors[k] - other._uvp_vectors[k]
        v = Vector("")
        v._uvp_vectors = uvp
        return v

    def _cartesian_magnitude(self) :
        global _HALF_DECIMAL
        global _SIN60
        (major, minor, vertical) = self._major_minor_vertical()
        h_dist = (major[0] + minor[0]*_HALF_DECIMAL)**2
        h_dist += (minor[0] * _SIN60)**2
        return (h_dist + vertical[0]**2).sqrt()

    def bearing(self, count=False) :
        """Get distance and AVID window of vector, relative to zero.

        Distance and window are separated by a space; distance is the
        integer (rounded, if relevant) from zero to this vector instance.
        The window is the bearing through which the vector is seen from
        the zero vector.

        By default, uses mathematical tricks to get exact distance.
        If `count` is True, this correction is not done and horizontal
        distance is the sum of horizontal components.

        Green-ring windows (B/C++, e.g.) may occur -- interpret per rules.
        """
        (major, minor, vertical) = self._major_minor_vertical()
        dir = major[1]
        
        if count :
            h_dist = major[0] + minor[0]
        else :
            h_dist = ( major[0] + minor[0] * Decimal('0.5') )**2
            h_dist += ( minor[0] * Decimal(sin(pi/3)) )**2
            h_dist = h_dist.sqrt()
        
        if major[0] == 0 :
            if vertical[0] == 0 :
                return "NONE"
            else :
                return "{} {}".format(
                        vertical[0],
                        "+++" if vertical[1] is '+' else "---")

        if (minor[0] * 3) >= major[0] :
            # through hex edge
            # format clockwise (A/B, not B/A)
            dir0, dir1 = major[1], minor[1]
            if dir1 < dir0 :
                dir0, dir1 = dir1, dir0
            dir = "{}/{}".format(dir0, dir1)

        v_dist = vertical[0]
        height = 0 # deviations from horizontal; +/++ categorization
        if abs(4*v_dist) > abs(h_dist) :
            height += 1
        if abs(v_dist) > abs(h_dist) :
            height += 1
        if abs(v_dist) >= abs(4*h_dist) :
            height += 1
        if height == 3 :
            dir = ''
        
        dist_pow = h_dist**2 + v_dist**2
        dist = floor(dist_pow.sqrt() + Decimal('0.5'))
        return "{} {}{}".format(dist, dir, vertical[1]*height)

    def movement_grid(self) :
        """Pretty-format a movement grid for this vector.

        If the zero vector, returns "STILL".
        Else, returns columns for each major horizontal, minor
        horizontal, and vertical movement component. First row is
        direction, second row is movement 'each' segment, remaining rows
        are the remainder grid, indexed by segment number.

        When a column is empty, there is no movement that applies. This
        may occur when there is no 'minor' or vertical component.
        """
        (major, minor, vertical) = self._major_minor_vertical()
        if major[0] == 0 and vertical[0] == 0 :
            return "STILL"

        majordir, minordir, vert_dir = ' ', ' ', ' '
        majoreach, minoreach, vert_each = ' ', ' ', ' '
        # copy to tuples; magnitudes may be modified
        major = [major[0], major[1]]
        minor = [minor[0], minor[1]]
        vertical = [vertical[0], vertical[1]]
        if major[0] > 0 :
            majordir = major[1]
            majoreach = floor(major[0] / 8)
            major[0] -= majoreach * 8
        if minor[0] > 0 :
            minordir = minor[1]
            minoreach = floor(minor[0] / 8)
            minor[0] -= minoreach * 8
        if vertical[0] > 0 :
            vert_dir = vertical[1]
            vert_each = floor(vertical[0] / 8)
            vertical[0] -= vert_each * 8

        header = [
            '|'.join([' ', majordir, minordir, vert_dir, '']),
            '|'.join([' ', str(majoreach), str(minoreach), str(vert_each), ''])
        ]

        grid = []
        v_maj = int(major[0])
        v_min = int(minor[0])
        v_vert = int(vertical[0])
        for i in range(8) :
            (maj, min) = remainders.HORIZONTAL[v_maj][v_min][i]
            h_sum = v_maj + v_min # - floor(v_min / 3)
            while h_sum > 7 :
                h_sum -= 8
            (_, vert) = remainders.VERTICAL[h_sum][v_vert][i]
            grid.append('|'.join([str(i+1), maj, min, vert, '']))
        return '\n'.join(header + grid)

    def cartesian(self) :
        """Get cartesian (X,Y,Z) components of the Vector.

        Returns a dictionary with keys of 'X', 'Y', and 'Z', with
        values of type `decimal.Decimal` for precision.

        Positive 'X' is in direction 'B/C', 'Y' in 'A', and 'Z' in '+'.
        """
        global _SIN60
        global _HALF_DECIMAL
        uvp = self._uvp_vectors
        
        return { 'x': uvp['U'] * _SIN60,
                 'y': -(uvp['V'] + uvp['U'] * _HALF_DECIMAL),
                 'z': uvp['+']
        }
#end class Vector

class AVID() :
    """Representation of a 'window' on the AVID skyball"""

    # options of all possible horizontal directions
    _WINDOWS_H = [
        "A",
        "A/B",
        "B",
        "B/C",
        "C",
        "C/D",
        "D",
        "D/E",
        "E",
        "E/F",
        "F",
        "F/A",
    ]

    # each major list is for the absolute value of height offset
    # each minor list the tuple representation of direction/height offsets
    #    orbiting an arbitrary direction at the offset distance equal to list index
    _OFFSETS = {
        0: [ # amber ring
            [ #0
                ( 0, 0)  # A     A/B
            ],
            [ #1
                ( 0, 1), # A+    A/B+
                (-1, 1), # F/A+  A+
                (-1, 0), # F/A   A
                (-1,-1), # F/A-  A-
                ( 0,-1), # A-    A/B-
                ( 1,-1), # A/B-  B-
                ( 1, 0), # A/B   B
                ( 1, 1), # A/B+  B+
            ],
            [ #2
                ( 0, 2), # A++   A/B++
                (-1, 2), # F/A++ A++
                (-2, 2), # F++   F/A++
                (-2, 1), # F+    F/A+
                (-2, 0), # F     F/A
                (-2,-1), # F-    F/A-
                (-2,-2), # F--   F/A--
                (-1,-2), # F/A-- A--
                ( 0,-2), # A--   A/B--
                ( 1,-2), # A/B-- B--
                ( 2,-2), # B--   B/C--
                ( 2,-1), # B-    B/C-
                ( 2, 0), # B     B/C
                ( 2, 1), # B+    B/C+
                ( 2, 2), # B++   B/C++
                ( 1, 2), # A/B++ B++
            ],
            [ #3
                ( 0, 3), # +++   +++
                (-3, 2), # E/F++ F++
                (-3, 1), # E/F+  F+
                (-3, 0), # E/F   F
                (-3,-1), # E/F-  F-
                (-3,-2), # E/F-- F--
                ( 0,-3), # ---   ---
                ( 3,-2), # B/C-- C--
                ( 3,-1), # B/C-  C-
                ( 3, 0), # B/C   C
                ( 3, 1), # B/C+  C+
                ( 3, 2), # B/C++ C++
            ],
            # 4,5,6 are found by taking the opposite window and index 6-i
        ],
        1: [ # blue ring (+1)
            [ #0
                ( 0, 0)  # A+    A/B+
            ],
            [ #1
                ( 0, 1), # A++   A/B++
                (-1, 1), # F/A++ A++
                (-1, 0), # F/A+  A+
                (-1,-1), # F/A   A
                ( 0,-1), # A     A/B
                ( 1,-1), # A/B   B
                ( 1, 0), # A/B+  B+
                ( 1, 1), # A/B++ B++
            ],
            [ #2
                ( 0, 2), # +++   +++
                (-2, 1), # F++   F/A++
                (-2, 0), # F+    F/A+
                (-2,-1), # F     F/A
                (-2,-2), # F-    F/A-
                (-1,-2), # F/A-  A-
                ( 0,-2), # A-    A/B-
                ( 1,-2), # A/B-  B-
                ( 2,-2), # B-    B/C-
                ( 2,-1), # B     B/C
                ( 2, 0), # B+    B/C+
                ( 2, 1), # B++   B/C++
            ],
            [ #3
                ( 6, 1), # D++   D/E+++
                (-5, 1), # D/E++ E++
                (-4, 1), # E++   E/F++
                (-3, 1), # E/F++ F++
                (-3, 0), # E/F+  F+
                (-3,-1), # E/F   F
                (-3,-2), # E/F-  F-
                (-3,-3), # E/F-- F--
                (-2,-3), # F--   F/A--
                (-1,-3), # F/A-- A--
                ( 0,-3), # A--   A/B--
                ( 1,-3), # A/B-- B--
                ( 2,-3), # B--   B/C--
                ( 3,-3), # B/C-- C--
                ( 3,-2), # B/C-  C-
                ( 3,-1), # B/C   C
                ( 3, 0), # B/C+  C+
                ( 3, 1), # B/C++ C++
                ( 4, 0), # C++   C/D++
                ( 5, 0), # C/D++ D++
            ]
        ],
        -1: [ # blue ring (-1)
            [ #0
                ( 0, 0)  # A-    A/B-
            ],
            [ #1
                ( 0, 1), # A     A/B  
                (-1, 1), # F/A   A
                (-1, 0), # F/A-  A-
                (-1,-1), # F/A-- A--
                ( 0,-1), # A--   A/B--
                ( 1,-1), # A/B-- B--
                ( 1, 0), # A/B-  B-
                ( 1, 1), # A/B   B
            ],
            [ #2
                ( 0, 2), # A+    A/B+
                (-1, 2), # F/A+  A+
                (-2, 2), # F+    F/A+
                (-2, 1), # F     F/A
                (-2, 0), # F-    F/A-
                (-2,-1), # F--   F/A--
                ( 0,-2), # ---   ---
                ( 2,-1), # B--   A/B--
                ( 2, 0), # B-    B/C-
                ( 2, 1), # B     B/C
                ( 2, 2), # B+    B/C+
                ( 1, 2), # A/B+  B+
            ],
        ],
        2: [ # green ring (+2)
            [ #0
                ( 0, 0), # A++   A/B++
            ],
            [ #1
                ( 0, 1), # +++   +++
                (-1, 0), # F/A++ A++
                (-2, 0), # F++   F/A++
                (-1,-1), # F/A+  A+
                ( 0,-1), # A+    F/A+
                ( 1,-1), # A/B+  B+
                ( 2, 0), # B+    B/C+
                ( 1, 0), # A/B++ B++
            ],
            [ #2
                ( 6, 0), # D++   D/E++
                (-5, 0), # D/E++ E++
                (-4, 0), # E++   E/F++
                (-3, 0), # E/F++ F++
                (-2,-1), # F+    F/A+
                (-2,-2), # F     F/A
                (-1,-2), # F/A   A
                ( 0,-2), # A     A/B
                ( 1,-2), # A/B   B
                ( 2,-2), # B     B/C
                ( 2,-1), # B+    B/C+
                ( 3, 0), # B/C++ C++
                ( 4, 0), # C++   C/D++
                ( 5, 0), # C/D++ D++
            ],
            [ #3
                ( 6,-1), # D+    D/E+
                (-5,-1), # D/E+  E+
                (-4,-1), # E+    E/F+
                (-3,-1), # E/F+  F+
                (-3,-2), # E/F   F
                (-3,-3), # E/F-  F-
                (-2,-3), # F-    F/A-
                (-1,-3), # F/A-  A-
                ( 0,-3), # A-    A/B-
                ( 1,-3), # A/B-  B-
                ( 2,-3), # B-    B/C-
                ( 3,-3), # B/C-  C-
                ( 3,-2), # B/C   C
                ( 3,-1), # B/C+  C+
                ( 4,-1), # C+    C/D+
                ( 5,-1), # C/D+  D+
            ]
        ],
        -2: [ # green ring (-2)
            [ #0
                ( 0, 0), # A--   A/B--
            ],
            [ #1
                ( 0, 1), # A-    A/B-
                (-1, 1), # F/A-  A-
                (-2, 0), # F--   F/A--
                (-1, 0), # F/A-- A--
                ( 0,-1), # ---   ---
                ( 1, 0), # A/B-- B--
                ( 2, 0), # B--   B/C--
                ( 1, 1), # A/B-  B-
            ],
            [ #2
                ( 0, 2), # A     A/B
                (-1, 2), # F/A   A
                (-2, 2), # F     F/A
                (-2, 1), # F-    F/A-
                (-3, 0), # E/F-- F--
                (-4, 0), # E--   E/F--
                (-5, 0), # D/E-- E--
                ( 6, 0), # D--   D/E--
                ( 5, 0), # C/D-- D--
                ( 4, 0), # C--   C/D--
                ( 3, 0), # B/C-- C--
                ( 2, 1), # B-    B/C-
                ( 2, 2), # B     B/C
                ( 1, 2), # A/B   B
            ],
        ],
        3: [ # fuchsia (+/-3) -- absolute window tuples
            [ # 0
                ( 0, 3),
            ],
            [ # 1
                ( 0, 2),
                ( 1, 2),
                ( 2, 2),
                ( 3, 2),
                ( 4, 2),
                ( 5, 2),
                ( 6, 2),
                ( 7, 2),
                ( 8, 2),
                ( 9, 2),
                (10, 2),
                (11, 2),
            ],
            [ # 2
                ( 0, 1),
                ( 1, 1),
                ( 2, 1),
                ( 3, 1),
                ( 4, 1),
                ( 5, 1),
                ( 6, 1),
                ( 7, 1),
                ( 8, 1),
                ( 9, 1),
                (10, 1),
                (11, 1),
            ],
            [ # 3 -- horizon
                ( 0, 0),
                ( 1, 0),
                ( 2, 0),
                ( 3, 0),
                ( 4, 0),
                ( 5, 0),
                ( 6, 0),
                ( 7, 0),
                ( 8, 0),
                ( 9, 0),
                (10, 0),
                (11, 0),
            ],
        ],
    }

    def _dir_vert_to_label(self, direction, vertical) :
        if vertical == 3 :
            return "+++"
        elif vertical == -3 :
            return "---"
        return self._WINDOWS_H[direction] + ('-' if vertical < 0 else '+') * abs(vertical)

    def __init__(self, label) :
        """Convert window name (F-, B/C--, +++) to an internal representation

        Raises ValueError if the name is invalid
        """

        if label == '+++' :
            self.direction = 0
            self.vertical = 3
            self.label = label
            return
        elif label == '---' :
            self.direction = 0
            self.vertical = -3
            self.label = label
            return

        dir, vert = 0, 0
        _dir0 = None

        if label.endswith("++") :
            vert = 2
            label = label[:-2]
        elif label.endswith("+") :
            vert = 1
            label = label[:-1]
        elif label.endswith("--") :
            vert = -2
            label = label[:-2]
        elif label.endswith("-") :
            vert = -1
            label = label[:-1]
        label = label.upper()

        if label not in self._WINDOWS_H :
            if '/' in label:
                label = label[::-1]
                if label not in self._WINDOWS_H :
                    raise ValueError("bad direction: " + label)
            else :
                raise ValueError("bad direction: " + label)

        for i in range(len(self._WINDOWS_H)) :
            if label == self._WINDOWS_H[i] :
                dir = i
                break

        dir = dir % 12
        self.label = self._dir_vert_to_label(dir, vert)
        self.direction = dir
        self.vertical = vert

    def to_tuple(self) :
        """return direction and vertical offset of the window

        horizontal direction cycles clockwise, A -> 0, A/F -> 11
        vertical if offet from horizon
            "amber"   -> 0,
            "blue"    -> +/-1,
            "green"   -> +/-2,
            "fuchsia" -> +/-3
        """
        return (self.direction, self.vertical)

    def __str__(self) :
        """get the string name of the AVID window"""
        return self.label[:]

    def offset_ring(self, dist) :
        """return a list of windows the given offset distance from this

        `dist` must be an integer between 0 and 6.

        List starts with the most vertical option and rotates clockwise,
        as viewed from outside the avid.
        If vertical ( +++, --- ), rotates from A towards A/B
        """

        origin_d = self.direction
        origin_v = self.vertical

        if origin_v in [3 or -3] :
            raise ValueError("not yet implemented")

        if dist > 3 :
            # "flip to opposite side"
            dist = 6 - dist
            origin_v *= -1
            origin_d += 6

        return [self._dir_vert_to_label((origin_d + dd)%12, origin_v + dv) 
                for (dd, dv) in self._OFFSETS[origin_v][dist]]

    def offset(self, dist, direction) :
        """get window name `dist` offsets in `direction`

        `dist` must be an integer between 0 and 6, inclusive.

        `direction` must resolve into a valid window.

        New window may 'overshoot' the direction window.
        """
        pass
#end class AVID

def get_bearing_vector_from_tile(j0, k0, u0, v0, h0, j1, k1, u1, v1, h1) :
    """Given tile coordinates for two locations, get bearing Vector.

    Takes j,k,u,v,h (tile coords, grid coords, height) of `from` and
    `to`, returning relative vector to `to`.
    """
    dj = j1 - j0
    dk = k1 - k0
    du = u1 - u0
    dv = v1 - v0
    dh = h1 - h0
    M = dk + 2*dj
    N = dk - dj
    uvp = {
        'U' : du + _TILE_RADIUS * M,
        'V' : dv + _TILE_RADIUS * N,
        '+' : dh
    } 
    v = Vector("")
    v._uvp_vectors = uvp
    return v

def movement(vector_string) :
    """Get a 'pretty-formatted' string to fill out one's movement grid.

    The vector string may include more than three terms -- vectors
    are consolidated into resulting three-term vector with adjacent
    horizontal terms.

    Provides the resulting vector and a movement grid, where the grid
    has columns for each direction, its "each" movement, and the
    remainder grid has an astrisk if movement is to occur during the
    segment (number on the left)
    """
    v = Vector(vector_string)
    return '\n'.join([str(v), "", v.movement_grid()])

_TO_EVADE = [
    "N/A"
    "0/1",
    "0/2",
    "1/3",
    "1/4",
    "1/5",
    "2/6",
    "2/7",
    "2/7",
    "2/8",
]

def to_string_rounded(num) :
    """represent numbers as whole integers 'N' or half-integers 'N.5' """

    strnum = str(num)
    if '.' in strnum :
        strnum, frac = strnum.split(".")
        frac_deci = Decimal("0."+frac)
        if frac_deci  <= Decimal("0.25") :
            pass
        elif frac_deci <= Decimal("0.75") :
            strnum += ".5"
        else :
            strnum = str(Decimal(strnum) + Decimal("1"))
    return strnum

def shellstar(
        vector_to_target,
        crossing_vector,
        muzzle_velocity,
        segment = None,
        burn = None) :
    """Generate seeker shellstar info.

    Takes a bearing vector to target and relative velocity vector of the target
    as well as final "muzzle velocity" of the projectile(s).

    Optionally provide a segment number; this is used for segment indexing
    in the closure table. Must be a number 1..8

    TODO: If a burn table is provided, it is used to override closing distance from
    muzzle velocity until burnout or impact.

    returns a printable string...
    If no shot, reports No Shot
    Else, gives:
        approach window and evasion options,
        time/distance track, and
        impact velocity (as RoC)
    """

    # ##################################################### #
    # calculate target's movements assuming no acceleration #
    # ##################################################### #

    target_movement = []

    grid = crossing_vector.movement_grid()
    if grid is "STILL" :
        target_movement = ['' for _ in range(8)]
    else :
        grid = grid.split('\n')
        mmv_line = grid[0][2:]
        each_line = grid[1][2:]
        grid_lines = grid[2:]
        which = mmv_line.split('|')[:-1]
        each = each_line.split('|')[:-1]
        remainders = [line.split('|')[1:-1] for line in grid_lines]

        for remainder_seq in remainders :
            str_seq = []
            for grouping in zip(which, each, remainder_seq) :
                # groups: major, minor, vertical
                (_which, _each, _rem) = grouping
                if _which is not ' ' :
                    k = 0
                    if _each is not  ' ' :
                        k += int(_each)
                    k += 1 if _rem is '*' else 0
                    if k is not 0 :
                        str_seq.append("{:d}{}".format(k, _which))
            target_movement.append(' '.join(str_seq))
    # end if moving
        

    # ##################################### #
    # prepare variables to begin simulation #
    # ##################################### #

    show_segments = segment is not None
    segment_i = ((segment-1) % 8) if show_segments else 0
    turn_i = 0
    segments_elapsed = 0
    muzzle_velocity = Decimal(muzzle_velocity)
    closure_report = []
    distance_to = vector_to_target._cartesian_magnitude()
    prev_distance = distance_to
    in_flight = True

    # ######################################## #
    # simulate projectile and target movements #
    # ######################################## #

    while in_flight :
        if distance_to > prev_distance :
            return "No Shot"
        else :
            seg_pre = "{}:{}".format(turn_i, segment_i+1) if show_segments \
                      else "+{}".format(segments_elapsed) 
            dist = "HIT" if distance_to <= 0 else floor(distance_to + _HALF_DECIMAL)
            closure_report.append("{} {}".format(seg_pre, dist))
            #TODO: burn notice
        
        if distance_to <= 0 :
            in_flight = False
            break

        prev_distance = distance_to
        segments_elapsed += 1
        displacement = target_movement[segment_i]
        if displacement != '' :
            vector_to_target = vector_to_target + Vector(displacement)
        distance_to = vector_to_target._cartesian_magnitude()
        distance_to -= muzzle_velocity / 8 * segments_elapsed

        if segment_i == 7 :
            turn_i += 1
            segment_i = 0
        else :
            segment_i += 1
    # end projectile flight loop

    segments_elapsed -= 1 # bookkeeping correction

    # ############### #
    # compose results #
    # ############### #

    # --------------------------------------
    # impact window and evasion directions
    # --------------------------------------

    impact_vector = Vector("") - vector_to_target
    impact_window = impact_vector.bearing().split()[1]
    evasion_options = []
    if impact_window in ["+++", "---"] :
        evasion_options.append("({})".format(impact_window))
        evasion_options.append("Evade in Amber Ring")
    else :
        orthagonal_windows = AVID(impact_window).offset_ring(3)
        up_window = orthagonal_windows[0]
        right_window = None
        left_window = None
        down_window = None
        for w in orthagonal_windows :
            if '+' not in w and '-' not in w :
                right_window = w
                break
        orthagonal_windows = orthagonal_windows[floor(len(orthagonal_windows)/2):]
        down_window = orthagonal_windows[0]
        for w in orthagonal_windows :
            if '+' not in w and '-' not in w :
                left_window = w
                break
        evasion_options.append("{}  {}".format(' ' * len(left_window), up_window))
        evasion_options.append("{} ({}) {}".format(left_window, impact_window, right_window))
        evasion_options.append("{}  {}".format(' ' * len(left_window), down_window))
        

    # ---------------
    # Rate of closure
    # ---------------

    target_xyz_v = crossing_vector.cartesian()
    seeker_xyz = vector_to_target.cartesian() # vector to impact point
    _from_dist_to_mv = muzzle_velocity / vector_to_target._cartesian_magnitude()
    seeker_xyz_v = {k: v * _from_dist_to_mv for k,v in seeker_xyz.items()}

    impact_v = Decimal(0)
    for k in target_xyz_v.keys() :
        impact_v += (seeker_xyz_v[k] - target_xyz_v[k])**2
    impact_v = impact_v.sqrt()

    if impact_v < Decimal('0.25') :
        return "No Shot"

    # ------------
    # Evasion Info
    # ------------

    global _TO_EVADE
    try :
        to_evade = _TO_EVADE[segments_elapsed]
    except IndexError :
        to_evade = _TO_EVADE[-1]

    return '\n'.join([
        '\n'.join(evasion_options),
        ">{} to evade".format(to_evade),
        '\n'.join(closure_report),
        "RoC: {}".format(to_string_rounded(impact_v / 8)),
    ])
#end shellstar()


