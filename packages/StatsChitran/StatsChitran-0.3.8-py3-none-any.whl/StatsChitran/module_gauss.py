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
    :param probability: True for a probability distribution, False for a probability distribution. Defaults to False.
    :return: list[float]
    :Example:
    >>> import numpy as np
    >>> import matplotlib.pyplot as plt
    >>> np.linspace(-7, 7, 100000)
    >>> x = x.tolist()
    >>> y = gauss(x, sig = 3, probability=True)
        Here is a plot of the input and output lists:

    .image:: ../images/module_gauss.png
        :alt: Input vs Output List plot
        :align: center
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