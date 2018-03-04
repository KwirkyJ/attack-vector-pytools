# attack-vector-pytools
Tools to smooth gameplay for the tabletop game "Attack Vector: Tactical".

## Quick Start
### Installation
No installation required. Tools are a semi-module for Python 3.4+, used through
the Python interpreter.

Optionally, include the top-level directory in you system or user python path.
(This has not yet been attempted -- TODO)

### Launch / Execute
Invoke the Python3 interpreter of your choice. (It is recommended that you
open a terminal, navigate to the top-level directory of this project, and
invoke `python3` or your equivalent commant.)

Once the interpreter is running, import the utils module, e.g.,
`import avt_gameplay_utils as avt`.

After importing the tools, you are now ready to start playing.
See the tools descriptions below for more details.

## Tools Details

attack-vector-tools provides a number of functions and classes to facilitate
fast, accurate gameplay for Attack Vector. Note that some values will return
not exactly as expected, if duplicated with the rules -- this is because the
power of the computer allows for more complete mathematical modeling, and this
was capitalized upon.

The routines are heavily tests in a unit test battery, which can be run with
a simple `python3 test_avt_gameplay_utils.py` invocation from the command line.

#### Note - tool names
Tools are listed with an `avt.` prefix, following suggested import statement in
Quick Start.

#### Note - "vector strings"
Below, a "vector string" refers to a string that can be interpreted as a vector
on the AVID, any sequence of `<number><direction>` separated by spaces, where
`number` is a positive integer and `direction` is any of `A, B, C, D, E, F`.
Order is not important. For example, `"5B 3C 1+"`, `"4- 12F 8E"`. In some
cases, the vector string may contain more than three terms, e.g. 
`"5B 3C 3E 2D 2+"`, in which case the vectors will be properly consolidated.
The vector string is _not_ case-sensitive, so `"4f"` is equivalent to `"4F"`.
The "motionless" vector string is the empty string, `""`.

### function:` avt.movement(vector_string)`
Get a 'pretty-formatted' string to fill out one's movement grid.

The vector string may include more than three terms -- vectors are consolidated
into resulting three-term vector with adjacent horizontal terms.

Provides the resulting vector and a movement grid, where the grid has columns
for each direction, its "each" movement, and the remainder grid has an astrisk
if movement is to occur during the segment (number on the left).

An example is annotated below
```
$ print(avt.movement("3e 5f 1a 3b 2+"))  < comand line invocation
5F 1A 2+  < consolidated vector string

 |F|A|+|  < "major", "minor", and "vertical" directions
 |0|0|0|  < "each": how far to move each segment
1| | |*|  < "remainders": a star '*' indicates to move 1 in that direction
2|*| | |     during the corresponding segment
3|*| | |
4|*| | |
5| | |*|
6|*| | |
7|*| | |
8| |*| |
```

A column may be empty, in which case there is no additional movement.

Returns `"STILL"` if the vector is motionless.

### function: `avt.shellstar(Vector-to-target, crossing-Vector, muzzle-velocity [, segment=segment])`
Generate seeker shellstar info.

Takes a bearing vector to target and relative velocity vector of the target
as well as final "muzzle velocity" of the projectile(s).

Optionally provide a segment number; this is used for segment indexing
in the closure table. Must be a number 1..8

returns a printable string...
If no shot, reports `No Shot`
Else, gives:
+ approach window and evasion options,
+ time/distance track, and
+ impact velocity (as RoC)

#### shellstar examples

```
$ print(avt.shellstar(avt.Vector("6A"), avt.vector("20A 6B"), 24))
No Shot
```
```
$ print(avt.shellstar(avt.Vector("4D 1E 7-"), avt.Vector("12D 4C 9-"), 24, segment=8))
     D++
B/C (A+) E/F  < (A+) is impact window, surrounded by up, down, left, and right.
     A--
>2/8 to evade  < Thrust requirements to exceed to evade 'a little' and 'a lot'.
0:8 8  < Time-distance track. Because a segment was provided, `turn:segment` is
1:1 8    printed, where `turn` is the turn relatve to when the seeker was
1:2 7    launched.
1:3 6
1:4 5
1:5 3
1:6 3
1:7 1
1:8 1
2:1 0  < an anomaly -- the low rate of closure rounded down to 0 in this case.
2:2 HIT
RoC: 1 < "Rate of Closure" upon impact.
```
Regarding the anomaly above (and the otherwise somewhat unintuitive distance
resulting from the given RoC), this is the result of a more accurate modeling
'under the hood'.

Were the `segment` not provided above, the time-distance track would have read:
```
+0 8
+1 8
+2 7
+3 6
+4 5
+5 3
+6 3
+7 1
+8 1
+9 0
+10 HIT
```
...with the time being segments elapsed since launch.

#### Note - missiles are not yet implemented. Coming soon.

### class: `avt.Vector`
Representation of velocity or position in hexagonal coordinates.

Relies on AV:T's 'AVID' directions, (A, B, C, D, E, F, +, -) for user
interaction, but converts to an intenal format for easier math.

Created by (and interacts with user) through 'vector strings', each being
either the empty string (""), indicating a zeroed vector, or a string
containing a number of `<number><direction>` sequences separated by spaces,
e.g., "5F", "4A 2C 6+", "1A 5d 2+ 3b 7- 6E". Note that case is unimportant in
user input, but all output will be capitalized.

Example instantiation: `vector_instance = avt.Vector("4A 2C 6+")`

Basic arithmetic is supported for Vector instances, with addition and
subtracting creating new Vector instances from the result.

Python's built-in To-string method `str(<Vector>)` is supported, 
providing an instance's vector string.

Vector instances have a number of useful routines:
+ `<Vector>.bearing()`
    + Get the (rounded) distance and AVID window of a vector.
    + Assumes relative to the zero vector.
+ `<Vector>.cartesian()`
    + Get a dictionary with 'X', 'Y', and 'Z' terms.
    + Values are Decimal objects.
+ `<Vector>.movement_grid()`
    + Look up and format the movement grid for the vector.

### function: `avt.Vector(vector_string)`
Create Vector instance from a vector string.

Order and count of components is not important, e.g., "5F", "4A 2C 6+",
"1A 5D 2+ 3B 7- 6E", as vectors are automatically normalized into at most two
horizontal components adjacent to one another, and at most one vertical
component.

Raises ValueError if:
+ a number is negative
+ a duplicate direction is encountered
+ direction is not recognized

Raises an error of some sort if `vecstr` is not a string.

The empy string ("") returns the zero vector.

### function: `<Vector>.bearing()`
Get distance and AVID window of vector, relative to zero.

Distance and window are separated by a space; distance is the integer
(rounded, if relevant) from zero to this vector instance. The window is the
bearing through which the vector is seen from the zero vector.

By default, uses mathematical tricks to get exact distance. If `count` is True,
this correction is not done and horizontal distance is the sum of horizontal
components.

"Green-ring windows" (B/C++, e.g.) may occur -- interpret per rules.

### function: `<Vector>.cartesian()`
Get cartesian (X,Y,Z) components of the Vector.

Returns a dictionary with keys of 'X', 'Y', and 'Z', with values of type
`decimal.Decimal` for precision.

Positive 'X' is in direction 'B/C', 'Y' in 'A', and 'Z' in '+'.

### function: `<Vector>.movement_grid()`
Pretty-format a movement grid for this vector.

If the zero vector, returns "STILL".
Else, returns columns for each major horizontal, minor horizontal, and vertical
movement component.
+ First row is direction
+ second row is movement 'each' segment
+ remaining rows are the remainder grid, indexed by segment number.

When a column is empty, there is no movement that applies. This
may occur when there is no 'minor' or vertical component.


