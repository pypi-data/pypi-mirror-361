import StatsChitran as sc
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

def seqn(st:float, end:float, n:int):
    """
    This function returns a sequence

    :param float st: The starting point of the sequence
    :param float end: The ending point of the sequence
    :param int n: The number of terms in the sequence
    :return: The list of numbers in the sequence
    :rtype: list[float]

    :Example:
        >>> #import the necessary libraries
        >>> import StatsChitranPython as sc
        >>> L = seq(0, 10, 21)
        >>> print(L)
        [0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0, 5.5, 6.0, 6.5, 7.0, 7.5, 8.0, 8.5, 9.0, 9.5, 10.0]
    """
    diff = (end - st)/(n-1)
    y = sc.arithprog(n=n, d=diff, st=st)
    return y
