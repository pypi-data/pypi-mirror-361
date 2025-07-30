################################################################################
# polymath/extensions/item_ops.py: item restructuring operations
################################################################################

import numpy as np
from polymath.qube import Qube

def extract_numer(self, axis, index, classes=(), recursive=True):
    """Extract an object from one numerator axis.

    Parameters:
        axis (int): The item axis from which to extract a slice.
        index (int): The index value at which to extract the slice.
        classes (tuple, optional): A single class or list or tuple of classes.
            The class of the object returned will be the first suitable class
            in the list. Otherwise, a generic Qube object will be returned.
            Defaults to empty tuple.
        recursive (bool, optional): True to include matching slices of the
            derivatives in the returned object; otherwise, the returned object
            will not contain derivatives. Defaults to True.

    Returns:
        Qube: An object extracted from the specified numerator axis.

    Raises:
        ValueError: If the axis is out of range.
    """

    # Position axis from left
    if axis >= 0:
        a1 = axis
    else:
        a1 = axis + self._nrank_
    if a1 < 0 or a1 >= self._nrank_:
        raise ValueError('axis is out of range (%d,%d): %d',
                         (-self._nrank_, self._nrank_, axis))
    k1 = len(self._shape_) + a1

    # Roll this axis to the beginning and slice it out
    new_values = np.rollaxis(self._values_, k1, 0)
    new_values = new_values[index]

    # Construct and cast
    obj = Qube(new_values, self._mask_, nrank=self._nrank_ - 1,
               example=self)
    obj = obj.cast(classes)
    obj._readonly_ = self._readonly_

    # Slice the derivatives if necessary
    if recursive:
        for (key, deriv) in self._derivs_.items():
            obj.insert_deriv(key, deriv.extract_numer(a1, index, classes,
                                                      False))

    return obj

#===============================================================================
def extract_denom(self, axis, index, classes=()):
    """Extract an object from one denominator axis.

    Parameters:
        axis (int): The item axis from which to extract a slice.
        index (int): The index value at which to extract the slice.
        classes (tuple, optional): A single class or list or tuple of classes.
            The class of the object returned will be the first suitable class
            in the list. If not provided and denominator rank is one, the
            object returned will have the same class as self. Otherwise,
            a generic Qube object will be returned. Defaults to empty tuple.

    Returns:
        Qube: An object extracted from the specified denominator axis.

    Raises:
        ValueError: If the axis is out of range.
    """

    # Position axis from left
    if axis >= 0:
        a1 = axis
    else:
        a1 = axis + self._drank_
    if a1 < 0 or a1 >= self._drank_:
        raise ValueError('axis is out of range (%d,%d): %d',
                         (-self._drank_, self._drank_, axis))
    k1 = len(self._shape_) + self._nrank_ + a1

    # Roll this axis to the beginning and slice it out
    new_values = np.rollaxis(self._values_, k1, 0)
    new_values = new_values[index]

    # Construct and cast
    obj = Qube(new_values, self._mask_, drank=self._drank_ - 1,
               example=self)
    obj = obj.cast((type(self),) + classes)
    obj._readonly_ = self._readonly_

    return obj

#===============================================================================
def extract_denoms(self):
    """Return a tuple of objects extracted from one object with a 1-D denominator.

    Returns a list of objects with the same class as self, but drank = 0.

    Returns:
        list: A list of objects with drank = 0.

    Raises:
        ValueError: If the object does not have a 1-D denominator.
    """

    if self._drank_ == 0:
        return [self]

    if self._drank_ != 1:
        raise ValueError('extract_denoms requires drank == 1')

    objects = []
    for k in range(self._denom_[0]):
        obj = Qube.__new__(type(self))
        obj.__init__(self._values_[...,k], self._mask_, drank=0, example=self)
        obj._readonly_ = self._readonly_
        objects.append(obj)

    return objects

#===============================================================================
def slice_numer(self, axis, index1, index2, classes=(), recursive=True):
    """Extract an object sliced from one numerator axis.

    Parameters:
        axis (int): The item axis from which to extract a slice.
        index1 (int): The starting index value at which to extract the slice.
        index2 (int): The ending index value at which to extract the slice.
        classes (tuple, optional): A single class or list or tuple of classes.
            The class of the object returned will be the first suitable class
            in the list. Otherwise, a generic Qube object will be returned.
            Defaults to empty tuple.
        recursive (bool, optional): True to include matching slices of the
            derivatives in the returned object; otherwise, the returned object
            will not contain derivatives. Defaults to True.

    Returns:
        Qube: An object sliced from the specified numerator axis.

    Raises:
        ValueError: If the axis is out of range.
    """

    # Position axis from left
    if axis >= 0:
        a1 = axis
    else:
        a1 = axis + self._nrank_
    if a1 < 0 or a1 >= self._nrank_:
        raise ValueError('axis is out of range (%d,%d): %d',
                         (-self._nrank_, self._nrank_, axis))
    k1 = len(self._shape_) + a1

    # Roll this axis to the beginning and slice it out
    new_values = np.rollaxis(self._values_, k1, 0)
    new_values = new_values[index1:index2]
    new_values = np.rollaxis(new_values, 0, k1+1)

    # Construct and cast
    obj = Qube(new_values, self._mask_, example=self)
    obj = obj.cast(classes)
    obj._readonly_ = self._readonly_

    # Slice the derivatives if necessary
    if recursive:
        for (key, deriv) in self._derivs_.items():
            obj.insert_deriv(key, deriv.slice_numer(a1, index1, index2,
                                                    classes, False))

    return obj

################################################################################
# Numerator shaping operations
################################################################################

def transpose_numer(self, axis1=0, axis2=1, recursive=True):
    """Return a copy of this object with two numerator axes transposed.

    Parameters:
        axis1 (int, optional): The first axis to transpose from among the
            numerator axes. Negative values count backward from the last
            numerator axis. Defaults to 0.
        axis2 (int, optional): The second axis to transpose. Defaults to 1.
        recursive (bool, optional): True to transpose the same axes of the
            derivatives; False to return an object without derivatives.
            Defaults to True.

    Returns:
        Qube: A copy with the specified numerator axes transposed.

    Raises:
        ValueError: If either axis is out of range.
    """

    len_shape = len(self._shape_)

    # Position axis1 from left
    if axis1 >= 0:
        a1 = axis1
    else:
        a1 = axis1 + self._nrank_
    if a1 < 0 or a1 >= self._nrank_:
        raise ValueError('first axis is out of range (%d,%d): %d',
                         (-self._nrank_, self._nrank_, axis1))
    k1 = len_shape + a1

    # Position axis2 from item left
    if axis2 >= 0:
        a2 = axis2
    else:
        a2 = axis2 + self._nrank_
    if a2 < 0 or a2 >= self._nrank_:
        raise ValueError('second axis out of range (%d,%d): %d',
                         (-self._nrank_, self._nrank_, axis2))
    k2 = len_shape + a2

    # Swap the axes
    new_values = np.swapaxes(self._values_, k1, k2)

    # Construct the result
    obj = Qube.__new__(type(self))
    obj.__init__(new_values, self._mask_, example=self)
    obj._readonly_ = self._readonly_

    if recursive:
        for (key, deriv) in self._derivs_.items():
            obj.insert_deriv(key, deriv.transpose_numer(a1, a2, False))

    return obj

#===============================================================================
def reshape_numer(self, shape, classes=(), recursive=True):
    """Return this object with a new shape for numerator items.

    Parameters:
        shape (tuple): The new shape for numerator items.
        classes (class or tuple, optional): A single class or list or tuple of
            classes. The class of the object returned will be the first suitable
            class in the list. Otherwise, a generic Qube object will be returned.
            Defaults to empty tuple.
        recursive (bool, optional): True to reshape the derivatives in the same
            way; otherwise, the returned object will not contain derivatives.
            Defaults to True.

    Returns:
        Qube: The reshaped object.

    Raises:
        ValueError: If the item size would be changed by the reshape operation.
    """

    # Validate the shape
    shape = tuple(shape)
    if self.nsize != int(np.prod(shape)):
        raise ValueError('item size must be unchanged: %s, %s' %
                         (str(self._numer_), str(shape)))

    # Reshape
    full_shape = self._shape_ + shape + self._denom_
    new_values = np.asarray(self._values_).reshape(full_shape)

    # Construct and cast
    obj = Qube(new_values, self._mask_, nrank=len(shape), example=self)
    obj = obj.cast(classes)
    obj._readonly_ = self._readonly_

    # Reshape the derivatives if necessary
    if recursive:
      for (key, deriv) in self._derivs_.items():
        obj.insert_deriv(key, deriv.reshape_numer(shape, classes, False))

    return obj

#===============================================================================
def flatten_numer(self, classes=(), recursive=True):
    """Return this object with a new numerator shape such that nrank == 1.

    Parameters:
        classes (class or tuple, optional): A single class or list or tuple of
            classes. The class of the object returned will be the first suitable
            class in the list. Otherwise, a generic Qube object will be returned.
            Defaults to empty tuple.
        recursive (bool, optional): True to include matching slices of the
            derivatives in the returned object; otherwise, the returned object
            will not contain derivatives. Defaults to True.

    Returns:
        Qube: The flattened object.
    """

    return self.reshape_numer((self.nsize,), classes, recursive)

################################################################################
# Denominator shaping operations
################################################################################

def transpose_denom(self, axis1=0, axis2=1):
    """Return a copy of this object with two denominator axes transposed.

    Parameters:
        axis1 (int, optional): The first axis to transpose from among the
            denominator axes. Negative values count backward from the last axis.
            Defaults to 0.
        axis2 (int, optional): The second axis to transpose. Defaults to 1.

    Returns:
        Qube: The transposed object.

    Raises:
        ValueError: If either axis is out of range.
    """

    len_shape = len(self._shape_)

    # Position axis1 from left
    if axis1 >= 0:
        a1 = axis1
    else:
        a1 = axis1 + self._drank_
    if a1 < 0 or a1 >= self._drank_:
        raise ValueError('first axis is out of range (%d,%d): %d',
                         (-self._drank_, self._drank_, axis1))
    k1 = len_shape + self._nrank_ + a1

    # Position axis2 from item left
    if axis2 >= 0:
        a2 = axis2
    else:
        a2 = axis2 + self._drank_
    if a2 < 0 or a2 >= self._drank_:
        raise ValueError('second axis out of range (%d,%d): %d',
                         (-self._drank_, self._drank_, axis2))
    k2 = len_shape + self._nrank_ + a2

    # Swap the axes
    new_values = np.swapaxes(self._values_, k1, k2)

    # Construct the result
    obj = Qube.__new__(type(self))
    obj.__init__(new_values, self._mask_, example=self)
    obj._readonly_ = self._readonly_

    return obj

#===============================================================================
def reshape_denom(self, shape):
    """Return this object with a new shape for denominator items.

    Parameters:
        shape (tuple): The new denominator shape.

    Returns:
        Qube: The reshaped object.

    Raises:
        ValueError: If the denominator size would be changed by the reshape
            operation.
    """

    # Validate the shape
    shape = tuple(shape)
    if self.dsize != int(np.prod(shape)):
        raise ValueError('denominator size must be unchanged: %s, %s' %
                         (str(self._denom_), str(shape)))

    # Reshape
    full_shape = self._shape_ + self._numer_ + shape
    new_values = np.asarray(self._values_).reshape(full_shape)

    # Construct and cast
    obj = Qube.__new__(type(self))
    obj.__init__(new_values, self._mask_, drank=len(shape), example=self)
    obj._readonly_ = self._readonly_

    return obj

#===============================================================================
def flatten_denom(self):
    """This object with a new denominator shape such that drank == 1.
    """

    return self.reshape_denom((self.dsize,))

################################################################################
# Numerator/denominator operations
################################################################################

def join_items(self, classes):
    """Return the object with denominator axes joined to the numerator.

    Derivatives are removed.

    Parameters:
        classes (class or tuple): Either a single subclass of Qube or a list or
            tuple of subclasses. The returned object will be an instance of the
            first suitable subclass in the list.

    Returns:
        Qube: The object with joined items.
    """

    if not self._drank_:
        return self.wod

    obj = Qube(self._values_, self._mask_,
               nrank=(self._nrank_ + self._drank_), drank=0,
               example=self)
    obj = obj.cast(classes)
    obj._readonly_ = self._readonly_

    return obj

#===============================================================================
def split_items(self, nrank, classes):
    """Return the object with numerator axes converted to denominator axes.

    Derivatives are removed.

    Parameters:
        nrank (int): Number of numerator axes to retain.
        classes (class or tuple): Either a single subclass of Qube or a list or
            tuple of subclasses. The returned object will be an instance of the
            first suitable subclass in the list.

    Returns:
        Qube: The object with split items.
    """

    obj = Qube(self._values_, self._mask_,
               nrank=nrank, drank=(self._rank_ - nrank),
               example=self)
    obj = obj.cast(classes)
    obj._readonly_ = self._readonly_

    return obj

#===============================================================================
def swap_items(self, classes):
    """Return a new object with the numerator and denominator axes exchanged.

    Derivatives are removed.

    Parameters:
        classes (class or tuple): Either a single subclass of Qube or a list or
            tuple of subclasses. The returned object will be an instance of the
            first suitable subclass in the list.

    Returns:
        Qube: The object with swapped items.
    """

    new_values = self._values_
    len_shape = new_values.ndim

    for r in range(self._nrank_):
        new_values = np.rollaxis(new_values, -self._drank_-1, len_shape)

    obj = Qube(new_values, self._mask_,
               nrank=self._drank_, drank=self._nrank_, example=self)
    obj = obj.cast(classes)
    obj._readonly_ = self._readonly_

    return obj

#===============================================================================
def chain(self, arg):
    """Return the chain multiplication of this derivative by another.

    Returns the denominator of the first object times the numerator of the
    second argument. The result will be an instance of the same class. This
    operation is never recursive.

    Parameters:
        arg (Qube): The right-hand term in the chain multiplication.

    Returns:
        Qube: The result of the chain multiplication.
    """

    left = self.flatten_denom().join_items(Qube)
    right = arg.flatten_numer(Qube)

    return Qube.dot(left, right, -1, 0, type(self), False)

################################################################################
