1 Overview
==========

This assignment will have you render animations as a series of images, using the `pngs` command.

Most animator-specified computer animations are the combination of two components: a scene graph and time-varying parameters.

1.1 Scene Graph
---------------

In this assignment we’ll replicate a version of the scene graph used in many animation tools.

Each _object_ will have

*   a _parent_, which is either another object or the world
*   an _origin_, which is a 3-vector defaulting to (0,0,0) (not in the required part of the assignment)
*   a _scale_, which is a 3-vector defaulting to (1,1,1) (not in the required part of the assignment)
*   a _position_, which is a 3-vector defaulting to (0,0,0)
*   an _orientation_, which will be given either in Euler or Quaternion form defaulting to $\langle 1;0,0,0 \rangle$
*   geometry, given as vertices and triangles similar to HW2

The _camera_ is a special object with no geometry. To position an object’s points for rendering by the camera, use $C^{-1}$, $O$ where C is the matrix (constructed as described above) for the camera and O is the matrix (constructed as described above) for the object. Recall that:

*   For any two matrices $A$ and $B$, $(AB)^{-1} = B^{-1} A^{-1}$
*   The inverse of a translation by (x,y,z) is a translation by (-x,-y,-z)
*   The inverse of a scaling by $(x,y,z)$ is a translation by $(1/x, 1/y, 1/z)$
*   The inverse of a rotation matrix R is the transpose of that matrix $R^{-1} = R^{T}$
*   The inverse of a rotation quaterion $q$ is its conjugate $q^{*}$

You can compute the inverse of a transformation matrix more accurately using the above rules than you can using a generic matrix inversion routine.

All this organization may seem like more bother than its worth, but scene graphs make complicated and interesting animation much easier to create.

1.2 Time-varying parameters
---------------------------

We’ll add animation by allowing various numbers, such as the coordinates of an object’s position vector, to be defined by a time-varying variable.

Every file will have access to two variables: `f`, which is equal to the current frame number, and `l`, which is the number of frames in the animation.

If the _frames_ argument of the `pngs` command is `30`, `f` will range from 0 on the first frame to 29 on the last frame and `l` will be 30 for all frames.

You’ll implement several ways of defining additional variables. To avoid the complexities of a full programming language, we’ll guarantee that regardless of which variable definition forms you define

*   each variable will be defined only once; no `x = x + 1`\-type reassignments;
*   each variable will be defined before it is used; and
*   variable definitions will be individually simple to parse: no parentheses or the like.

The above limitations will make _writing_ the input files a bit tedious, but will keep _parsing_ them straightforward.

Some full animation systems will animate vectors separately from their coordinates, for example using slurps (spherical linear interpolation) or hlerps (hyperbolic linear interpolation). Those can be decomposed into per-coordinate trigonometry and other more involved functions; to keep the input files from getting out of hand we’ll only deal with them in that form.
