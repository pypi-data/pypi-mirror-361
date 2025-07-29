###try to change vector indexing

class Vec:
    """
        This class, **Vec** is being used to define a new kind of vectors for python usage with arithmetic properties and indexing from 1.
    """
    #instance call
    def __init__(self, v):
        """
        Initialise an object with a value, v
        :param v: needs to be a numeric (float/int) list
        Examples
        ---------
        ##define a Vec object
        >>> obj = Vec([5, 6, 7, 8, 9, 10])
        """
        self.dat = v
        self.n = len(v) #defines the length of the vector

    #define proper indexing
    def __getitem__(self, ind):
        """
        Function called automatically when [] are used on this class' objects
        :param ind: This index is self generated from __getitem__
        :return: returns a single float value in accordance to the new indexes(starts from 1)
        Examples
        ---------
        ##define a Vec object and check its indexing
        >>> obj = Vec([5, 6, 7, 8, 9, 10])
        >>> print(obj[1], obj[2], obj[3], obj[4], obj[5], obj[6])
        5 6 7 8 9 10
        """
        if (ind < 1) | (ind > len(self.dat)):
            raise IndexError('List index out of range')
        return self.dat[ind - 1]

    #define the addition operator
    def __add__(self, other):
        """
        Function defines element wise addition amongst Vec objects built oot of python-lists of the same length
        :param other: The second object(class: Vec)
        :return: a list like object(class: Vec) as a result of element wise addition of the self and the other objects
        Examples
        ---------
        ##define a Vec object and check addition
        >>> v1 = Vec([1, 2, 3])
        >>> v2 = Vec([5, 6, 7])
        >>> v3 = v1 + v2
        >>> print(v3[1], v3[2], v3[3])
        6 8 10
        """
        if len(self.dat) != len(other.dat):
            raise ValueError('adding different vectors need to have the vector lengths')
        else:
            self.w = [None]*len(self.dat)
            for i in range(len(self.dat)):
                self.w[i] = self.dat[i] + other.dat[i]
            return Vec(self.w)

    #defines the subtraction operator
    def __sub__(self, other):
        """
        Function defines element wise subtraction amongst Vec objects built out of python-lists of the same length
        :param other: The second object(class: Vec)
        :return: a list like object(class: Vec) as a result of element wise subtraction of the self and the other objects
        Examples
        ---------
        ##define a Vec object and check subtraction
        >>> v1 = Vec([1, 2, 3])
        >>> v2 = Vec([5, 6, 7])
        >>> v3 = v1 - v2
        >>> print(v3[1], v3[2], v3[3])
        -4 -4 -4
        """
        if len(self.dat) != len(other.dat):
            raise ValueError('subtracting different vectors need to have the vector lengths')
        else:
            self.w = [None]*len(self.dat)
            for i in range(len(self.dat)):
                self.w[i] = self.dat[i] - other.dat[i]
            return Vec(self.w)

    #defines the multiplication operator
    def __mul__(self, other):
        """
        Function defines element wise multiplication amongst Vec objects built out of python-lists of the same length
        :param other: The second object(class: Vec)
        :return: a list like object(class: Vec) as a result of element wise multiplication of the self and the other objects
        Examples
        ---------
        ##define a Vec object and check multiplication
        >>> v1 = Vec([1, 2, 3])
        >>> v2 = Vec([5, 6, 7])
        >>> v3 = v1*v2
        >>> print(v3[1], v3[2], v3[3])
        5 12 21
        """
        if len(self.dat) != len(other.dat):
            raise ValueError('multiplying different vectors need to have the vector lengths')
        else:
            self.w = [None]*len(self.dat)
            for i in range(len(self.dat)):
                self.w[i] = self.dat[i]*other.dat[i]
            return Vec(self.w)

    #defines the division operator
    def __truediv__(self, other):
        """
        Function defines element wise division amongst Vec objects built out of python-lists of the same length
        :param other: The second object(class: Vec)
        :return: a list like object(class: Vec) as a result of element wise division of the self and the other objects
        Examples
        ---------
        ##define a Vec object and check division
        >>> v1 = Vec([1, 2, 3])
        >>> v2 = Vec([5, 6, 7])
        >>> v3 = v1/v2
        >>> print(v3[1], v3[2], v3[3])
        0.2 0.3333333333333333 0.42857142857142855
        """
        if len(self.dat) != len(other.dat):
            raise ValueError('dividing different vectors need to have the vector lengths')
        else:
            self.w = [None] * len(self.dat)
            for i in range(len(self.dat)):
                self.w[i] = self.dat[i] /other.dat[i]
            return Vec(self.w)

    #defines the floordiv operator
    def __floordiv__(self, other):
        """
        Function defines element wise floor division amongst Vec objects built out of python-lists of the same length
        :param other: The second object(class: Vec)
        :return: a list like object(class: Vec) as a result of element wise floor division of the self and the other objects
        Examples
        ---------
        ##define a Vec object and check floor division
        >>> v1 = Vec([1, 2, 3])
        >>> v2 = Vec([5, 6, 7])
        >>> v3 = v1//v2
        >>> print(v3[1], v3[2], v3[3])
        0 0 0
        """
        if len(self.dat) != len(other.dat):
            raise ValueError('dividing different vectors need to have the vector lengths')
        else:
            self.w = [None] * len(self.dat)
            for i in range(len(self.dat)):
                self.w[i] = self.dat[i] //other.dat[i]
            return Vec(self.w)

    #defines the power operator
    def __pow__(self, power, modulo=None):
        """
        Function defines element wise exponentiation using the ** operator for a list like Vec object
        :param power: must be a single float or an int. Is the power/exponent
        :param modulo: Not needed
        :return: a list like object(class: Vec) as a result of the element wise exponentiation
        Examples
        ---------
        ##define a Vec object and check floor division
        >>> v1 = Vec([1, 2, 3])
        >>> v2 = Vec([5, 6, 7])
        >>> v31 = v1**2
        >>> print(v31[1], v31[2], v31[3])
        1 4 9
        >>> v32 = v2**2
        >>> print(v32[1], v32[2], v32[3])
        25 36 49
        """
        if isinstance(power, int)|isinstance(power, float) == True:
            self.w = [None]*self.n
            for i in range(self.n):
                self.w[i] = self.dat[i]**power
        else:
            raise ValueError('The exponent or the power term needs to be of type float/int while using the ** or pow operator with a Vec class object as a base')
        return Vec(self.w)

    #defines the scale operator
    def scale(self, cons):
        """
        Function defines a constant scaling multiplication for entire list like Vec object
        :param cons: a scalar constant of type int or float
        :return: a list like object(class: Vec) as a result of the scaling
        Examples
        ---------
        ##define a Vec object and check scale operation
        >>> v1 = Vec([1, 2, 3])
        >>> v3 = Vec.scale(v1, 3)
        >>> print(v3[1], v3[2], v3[3])
        3 6 9
        """
        if isinstance(cons, int)|isinstance(cons, float) == True:
            self.w = [None]*self.n
            for i in range(self.n):
                self.w[i] = self.dat[i]*cons
        else:
            raise ValueError('The cons term needs to be of type int or float in the scale operation')
        return Vec(self.w)

    #defines the shift operator
    def shift(self, cons):
        """
        Function defines a constant translational shifting for entire list like Vec object
        :param cons: a scalar constant of type int or float
        :return: a list like object(class: Vec) as a result of the scaling
        Examples
        ---------
        ##define a Vec object and check shift operation
        >>> v1 = Vec([1, 2, 3])
        >>> v2 = 1
        >>> v3 = Vec.shift(v1, 1)
        >>> print(v3[1], v3[2], v3[3])
        2 3 4
        """
        if isinstance(cons, int) | isinstance(cons, float) == True:
            self.w = [cons]*self.n
            self.w = Vec(self.w)
            self.w = self.w + Vec(self.dat)
            return self.w
        else:
            raise ValueError('cons has to be a scalar of type int or float')
    #defines the subset operator
    def subset(self, start: int, end: int):
        """
        Function defines a subset on the Vec object using the start and end indexes
        :param start: The index from which you want to start the indexing
        :param end: The index to which you want to index
        :return: a list like object(class: Vec) as a result of the scaling
        Examples
        ---------
        ##define a Vec object and check subsetting
        >>> obj = Vec([5, 6, 7, 8, 9, 10])
        >>> dmp = obj.subset(2, 4)
        >>> print(dmp[1], dmp[2], dmp[3])
        6 7 8
        """
        if start < 1:
            raise ValueError('Minimum start index allowed is 1')
        elif end > self.n:
            raise ValueError('Maximum end index should not exceed length of vector')
        elif start >= end:
            raise ValueError('Start index should be less than end index')
        else:
            return Vec(self.dat[start - 1 : end])

    #defines the concatenation method
    def c(self, other):
        """
        Function used to concatenate two list like objects(class: Vec)
        :param other: The second list like object (class: Vec)
        :param self: The first List like object (class: Vec)
        :return: a list like object(class: Vec) as a result of the concatenation
        Examples
        ---------
        ##define a Vec object and check concatenation
        >>> obj1 = Vec([1, 3, 5])
        >>> obj2 = Vec([7, 8, 9])
        >>> res = Vec.c(obj1, obj2)
        >>> print(res[1], res[2], res[3], res[4], res[5], res[6])
        1 3 5 7 8 9
        """
        return Vec(self.dat + other.dat)

    #defines the return to python lists or plists
    @staticmethod
    def plist(v):
        """
        Function returns a python-list(plist) from a Vec list
        :param v: The list like object(class: Vec) that you want to return the python list out of
        :return: a python-list
        Examples
        ---------
        ##define a Vec object and check plist-ing
        >>> obj1 = Vec([1, 3, 5])
        >>> obj2 = Vec([7, 8, 9])
        >>> v31 = Vec.plist(v = obj1)
        >>> v32 = Vec.plist(v = obj2)
        >>> print(v31)
        [1, 3, 5]
        >>> print(v32)
        [7, 8, 9]
        """
        if isinstance(v, Vec):
            return v.dat
        else:
            raise ValueError('Object should be an instance of class Vec')
