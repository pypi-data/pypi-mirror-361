from typing import List
import numpy as np

##Arithmetic Progression
def arithprog( n: int, d: float, st: float = 0.0) -> List[float]:
    """
    This function generates a list of numbers following a arithmetic progression.

    :param int n: Length of the sequence.
    :param float d: Difference of the kth term from the (k + 1)th term for any k.
    :param float st: Starting value of the sequence.
    :return: A list of numbers representing the geometric progression.
    :rtype: list[float]

    :Example:
     >>> L = arithprog( n = 4, d = 2, st = 2.0)
     >>> print(L)
        [2.0, 4.0, 6.0, 8.0]
    """
    ret_list = []
    for i in range(1, n+1):
        num = st + (i - 1)*d
        ret_list.append(num)
    return ret_list







##Geometric Progression
def geomprog( n: int, r: float, st: float = 1.0) -> List[float]:
    """
    This function generates a list of numbers following a geometric progression.

    :param int n: Length of the sequence.
    :param float r: Ratio of the (k+1)th to kth term for any k.
    :param float st: Starting value of the sequence.
    :return: A list of numbers representing the geometric progression.
    :rtype: list[float]

    :Example:
     >>> geomprog(n = 5, r = 3, st = 2)
        [2, 6, 18, 54, 162]
    """
    ret_list = []
    for i in range(1, n+1):
        num = st*( r**(i - 1) )
        ret_list.append(num)
    return ret_list

#is numeric
def is_numeric(lst):
    """
    This function returns True if all entries are numeric(int or float)

    :param list lst: A python list
    :return: A boolean bit specifying whether all members are numeric
    :rtype: list[float]

    :Example:
    >>> L1 = [1, 2, 3.0, 4]
    >>> L2 = [1, 2, 3.0, 4, 'a']
    >>> L3 = [1, 2, 3.0, 4, np.nan]
    >>> print(is_numeric(L1))
    >>> print(is_numeric(L2))
    >>> print(is_numeric(L3))

        True
        False
        True
    """
    return all(isinstance(k, (int, float)) for k in lst)

