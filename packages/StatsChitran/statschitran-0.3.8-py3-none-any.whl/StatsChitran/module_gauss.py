from typing import List
import math as m
import numpy as np
import matplotlib.pyplot as plt



class Constants:
    PI: float = 3.14159


def gauss(x: List[float], amp: float = None, mu: float = 0.0, sig: float = 1.0, probability: bool = False )  -> List[float]:
    """
    This function generates a list of numbers that follows a gaussian distribution
    :param list float x: A floating list of the numbers over which a probability or statistical distribution is expected
    :param amp: The amplitude of the gaussian, only expected if probability is false(Statistical distribution and not a probability distribution). Providing this value when probability is True throws an error
    :param mu: The mean of the gaussian. Defaults to zero
    :param sig: The standard deviation of the gaussian, defaults to 1
    :param probability: True for a probability distribution, False for a statistical distribution. Defaults to False.
    :return: list[float]
    :Example:
    >>> #import the necessary libraries
    >>> import numpy as np
    >>> import matplotlib.pyplot as plt
    >>> #Build the x-values
    >>> np.linspace(-7, 7, 100000)
    >>> x = x.tolist()
    >>> #Build two gaussians
    >>> y1 = gauss(x, sig = 3, probability=True)
    >>> y2 = gauss(x, mu = 1, sig = 1.5, probability=True)
    >>> #Plot the two gaussians
    >>> plt.plot(x, y1, color = 'blue', label = 'g1')
    >>> plt.plot(x, y2, color = 'red', label = 'g2')
    >>> plt.xlabel('X-axis Label')
    >>> plt.ylabel('Y-axis Label')
    >>> plt.show()
        Here is a plot of the input(x) versus outputs(y1 and y2) lists:

    ![Input vs Output List](../images/module_gauss.png)
    """
    ##Error checking. Can't have a probability distribution and an amplitude both assigned
    if( ( probability == True ) and ( amp != None) ):
        raise ValueError('amp cant be manually assigned when probability is True')
    elif ( (probability == False) and (amp == None) ):
        raise ValueError('amp has to be specified when probability is False')
    elif (probability == True):
        amp = 1/(sig*m.sqrt(2*Constants.PI))
    else:
        pass
    x = np.array(x)
    y = amp*np.exp(-1*( ( x - mu )/(m.sqrt(2)*sig) )**2 )
    y = y.tolist()
    return y