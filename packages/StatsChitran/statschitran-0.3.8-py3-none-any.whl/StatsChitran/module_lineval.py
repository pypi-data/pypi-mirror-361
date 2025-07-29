##given two points (x1,y1), (x2,y2) and a dataset X, spill out a vector Y
##Y should give the values of Y on the line corresponding to the given X
import numpy as np
import StatsChitran as sc
from StatsChitran import Vec, is_numeric
import matplotlib.pyplot as plt


def lineval(v1: sc.Vec, v2: sc.Vec, x: sc.Vec) -> sc.Vec:
    """
    Given two points, v1 = (x1,y1) and v2 = (x2,y2) and a list x, the function spills out a vector y which is the sequence of values of the line passing through v1 and v2 for the corresponding values of x
    :param v1: the first point in a list of the sc.Vec type. Needs to be a 2 element list.
    :param v2: the second point in a list of the sc.Vec type. Needs to be a 2 element list.
    :param x: the list of x-values for which the list of y values will be generated
    :return: the return is always a list of the sc.Vec type

    Examples
    ---------
    >>> #import the necessary libraries
    >>> import StatsChitran as sc
    >>> from StatsChitran import Vec, is_numeric
    >>> import matplotlib.pyplot as plt
    >>> #build the two datasets and plot the two lines
    >>> v1 = Vec([1, 1])
    >>> v2 = Vec([4, 4])
    >>> x = sc.arithprog(n = 1000, st = -10, d = 0.1)
    >>> y1 = lineval(v1, v2, Vec(x))
    >>> plt.plot(x, Vec.plist(y1), color = 'blue', label = 'y1')
    >>> v1 = Vec([0, 1])
    >>> v2 = Vec([80, 30])
    >>> y2 = lineval(v1, v2, Vec(x))
    >>> plt.plot(x, Vec.plist(y2), color = 'red', label = 'y2')
    >>> plt.xlabel('X-axis Label')
    >>> plt.ylabel('Y-axis Label')
    >>> plt.show()
            Here is a plot of the input(x) versus outputs(y1 and y2) lists:

    ![Input vs Output List](../images/module_lineval.png)

    """
    # v1 and v2 have to be two 2D point vectors(numeric) of type sc.Vec
    if ( len(Vec.plist(v1)) != 2 ) | ( len(Vec.plist(v2)) != 2 ):
        raise ValueError('v1 and v2 both have to be list type sc.Vec objects of lengths equal to 2')
    elif isinstance(v1, sc.Vec) and isinstance(v2, sc.Vec) and isinstance(x, sc.Vec) == False:
        raise ValueError('v1, v2 and x have to be list type sc.Vec objects')
    elif is_numeric(Vec.plist(v1)) and is_numeric(Vec.plist(v2)) and is_numeric(Vec.plist(x))== False:
        raise ValueError('v1, v2 and x have to be numeric objects converted to sc.Vec objects')
    else:
        x1 = v1[1]; x2 = v2[1]; y1 = v1[2]; y2 = v2[2]
        m = (y2 - y1)/(x2 - x1)
        c = (x2*y1 - y2*x1)/(x2 - x1)
        y = Vec.scale(x, m)
        y = Vec.shift(y, c)
        return y