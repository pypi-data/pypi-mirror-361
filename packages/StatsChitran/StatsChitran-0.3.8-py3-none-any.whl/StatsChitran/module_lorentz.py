import numpy as np 
import pandas as pd
import matplotlib.pyplot as plt
import math
import StatsChitran as sc

def lorentz(x:list[float], x_0: float, gamma: float, probability: bool = True, amp:float = None ):
    """
    This function generates a list of numbers that follows a lorentzian distribution
    :param list float x: A floating list of the numbers over which a probability or statistical distribution is expected
    :param amp: The amplitude of the lorentzian, only expected if probability is false(Statistical distribution and not a probability distribution). Providing this value when probability is True throws an error
    :param x_0: The mean of the lorentzian.
    :param gamma: The HWHM of the lorentzian.
    :param probability: True for a probability distribution, False for a statistical distribution. Defaults to True.
    :return: list[float]
    :Example:
    >>> #import the necessary libraries
    >>> import numpy as np
    >>> import matplotlib.pyplot as plt
    >>> import StatsChitran as sc
    >>> #Build the x-values
    >>> X = sc.seqn(-10, 10, 1000)
    >>> #Build two lorentzians
    >>> Y1 = sc.lorentz(x=X, x_0=0, amp=1.5, gamma=1.5, probability=False)
    >>> Y2 = sc.lorentz(x=X, x_0=0, gamma=2.0)
    >>> #Plot the two lorentzians
    >>> plt.plot(X, Y1, color = 'blue', label = 'l1')
    >>> plt.plot(X, Y2, color = 'red', label = 'l2')
    >>> plt.xlabel('X-axis Label')
    >>> plt.ylabel('Y-axis Label')
    >>> plt.show()
        Here is a plot of the input(x) versus outputs(y1 and y2) lists:

    ![Input vs Output List](../images/module_lorentz.png)
    """
    ## Error checking
    if probability:
        if amp is not None:
            raise ValueError("When probability=True, 'amp' must not be set manually.")
        else:
            amp = 1.0
    else:
        if amp is None:
            raise ValueError("When probability=False, 'amp' must be set manually.")
    x = np.array(x)
    y = ( 1/(gamma*math.pi))*( amp/(1 + ((x - x_0)/gamma)**2))
    y = y.tolist()
    return y

