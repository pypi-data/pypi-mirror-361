################################################################################
# polymath/extensions/math_ops.py: general math operations
################################################################################

import numpy as np
import numbers
import sys
from polymath.qube import Qube
from polymath.units import Units

PYTHON2 = (sys.version_info[0] < 3)

#===============================================================================
def _mean_or_sum(arg, axis=None, recursive=True, _combine_as_mean=False):
    """Calculate the mean or sum of the unmasked values.

    Internal method for computing mean or sum operations.

    Parameters:
        arg: The object for which to calculate the mean or sum.
        axis (int or tuple, optional): An integer axis or a tuple of axes. The
            mean is determined across these axes, leaving any remaining axes in
            the returned value. If None (the default), then the mean is
            performed across all axes of the object.
        recursive (bool, optional): True to construct the mean of the
            derivatives. Defaults to True.
        _combine_as_mean (bool, optional): True to combine as a mean; False to
            combine as a sum. Defaults to False.

    Returns:
        Qube: The mean or sum of the unmasked values.
    """

    arg._check_axis(axis, 'mean()' if _combine_as_mean else 'sum()')

    if arg._size_ == 0:
        return arg._zero_sized_result(axis=axis)

    # Select the NumPy function
    if _combine_as_mean:
        func = np.mean
    else:
        func = np.sum

    # Create the new axis, which is valid regardless of items
    rank = len(arg._shape_)
    if isinstance(axis, numbers.Integral):
        new_axis = axis % rank
    elif axis is None:
        new_axis = tuple(range(rank))
    else:
        new_axis = tuple(a % rank for a in axis)

    # If there's no mask, this is easy
    if not np.any(arg._mask_):
        obj = Qube(func(arg._values_, axis=new_axis), False, example=arg)

    # Handle a fully masked object
    elif np.all(arg._mask_):
        obj = Qube(func(arg._values_, axis=new_axis), True, example=arg)

    # If we are averaging over all axes, this is fairly easy
    elif axis is None:
        if arg._shape_ == ():
            obj = arg
        else:
            obj = Qube(func(arg._values_[arg.antimask], axis=0), False,
                       example=arg)

    # At this point, we have handled the cases mask==True and mask==False,
    # so the mask must be an array. Also, there must be at least one
    # unmasked value.

    else:
        # Set masked items to zero, then sum across axes
        new_values = arg._values_.copy()
        new_values[arg._mask_] = 0
        new_values = np.sum(new_values, axis=new_axis)

        # Count the numbers of unmasked items, summed across axes
        count = np.sum(arg.antimask, axis=new_axis)

        # Convert to a mask and a mean
        new_mask = (count == 0)
        if _combine_as_mean:
            count_reshaped = count.reshape(count.shape + arg._rank_ * (1,))
            denom = np.maximum(count_reshaped, 1)
            if PYTHON2:
                if np.shape(denom):
                    denom = denom.astype('float')
                else:
                    denom = float(denom)
            new_values = new_values / denom

        # Fill in masked values with the default
        if np.any(new_mask):
            new_values[(new_mask,) +
                       arg._rank_ * (slice(None),)] = arg._default_
        else:
            new_mask = False

        obj = Qube(new_values, new_mask, example=arg)

    # Cast to the proper class
    obj = obj.cast(type(arg))

    # Handle derivatives
    if recursive and arg._derivs_:
        new_derivs = {}
        for (key, deriv) in arg._derivs_.items():
            new_derivs[key] = _mean_or_sum(deriv, axis, recursive=False,
                                           _combine_as_mean=_combine_as_mean)

        obj.insert_derivs(new_derivs)

    return obj

#===============================================================================
def _check_axis(arg, axis, op):
    """Validate the axis as None, an int, or a tuple of ints.

    Parameters:
        arg: The object to check the axis for.
        axis: The axis to validate.
        op (str): The operation name for error messages.

    Raises:
        IndexError: If the axis is out of range or duplicated.
    """

    if axis is None:    # can't be a problem
        return

    # Fix up the axis argument
    if isinstance(axis, tuple):
        axis_for_show = axis
    elif isinstance(axis, list):
        axis_for_show = tuple(axis)
    else:
        axis_for_show = axis
        axis = (axis,)

    # Check for duplicates
    # Check for in-range values
    selections = len(arg._shape_) * [False]
    for i in axis:
        try:
            _ = selections[i]
        except IndexError:
            raise IndexError('axis is out of range (%d,%d) in %s.%s: %d'
                             % (-len(arg._shape_), -len(arg._shape_),
                                type(arg).__name__, op, i))

        if selections[i]:
            raise IndexError('duplicated axis in %s.%s: %s'
                             % (type(arg).__name__, op, axis_for_show))

        selections[i] = True

#===============================================================================
def _zero_sized_result(self, axis):
    """Return a zero-sized result obtained by collapsing one or more axes.

    Parameters:
        axis (int or tuple, optional): The axis or axes to collapse.

    Returns:
        Qube: A zero-sized result with the specified axes collapsed.
    """

    if axis is None:
        return self.flatten().as_size_zero()

    # Construct an index to obtain the correct shape
    indx = len(self.shape) * [slice(None)]
    if isinstance(axis, (list, tuple)):
        for i in axis:
            indx[i] = 0
        else:
            indx[i] = 0

    return self[tuple(indx)]

#===============================================================================
@staticmethod
def dot(arg1, arg2, axis1=-1, axis2=0, classes=(), recursive=True):
    """Calculate the dot product of two objects.

    The axes must be in the numerator, and only one of the objects can have a
    denominator (which makes this suitable for first derivatives but not second
    derivatives).

    Parameters:
        arg1: The first operand as a subclass of Qube.
        arg2: The second operand as a subclass of Qube.
        axis1 (int, optional): The item axis of this object for the dot product.
            Defaults to -1.
        axis2 (int, optional): The item axis of the arg2 object for the dot
            product. Defaults to 0.
        classes (tuple, optional): A single class or list or tuple of classes.
            The class of the object returned will be the first suitable class
            in the list. Otherwise, a generic Qube object will be returned.
            Defaults to empty tuple.
        recursive (bool, optional): True to construct the derivatives of the
            dot product. Defaults to True.

    Returns:
        Qube: The dot product of the two objects.

    Raises:
        ValueError: If both objects have denominators or if axes are out of
            range.
    """

    # At most one object can have a denominator.
    if arg1._drank_ and arg2._drank_:
        Qube._raise_dual_denoms('dot()', arg1, arg2)

    # Position axis1 from left
    if axis1 >= 0:
        a1 = axis1
    else:
        a1 = axis1 + arg1._nrank_
    if a1 < 0 or a1 >= arg1._nrank_:
        raise ValueError('first axis is out of range (%d,%d) in %s.dot(): %d'
                         % (-arg1._nrank_, arg1._nrank_, type(arg1).__name__,
                            axis1))
    k1 = a1 + len(arg1._shape_)

    # Position axis2 from item left
    if axis2 >= 0:
        a2 = axis2
    else:
        a2 = axis2 + arg2._nrank_
    if a2 < 0 or a2 >= arg2._nrank_:
        raise ValueError('second axis is out of range (%d,%d) in %s.dot(): %d'
                         % (-arg2._nrank_, arg2._nrank_, type(arg2).__name__,
                            axis2))
    k2 = a2 + len(arg2._shape_)

    # Confirm that the axis lengths are compatible
    if arg1._numer_[a1] != arg2._numer_[a2]:
        raise ValueError('%s.dot() axes have different lengths: %d, %d' %
                         (type(arg1).__name__, arg1._numer_[a1],
                          arg2._numer_[a2]))

    # Re-shape the value arrays (shape, numer1, numer2, denom1, denom2)
    shape1 = (arg1._shape_ + arg1._numer_ + (arg2._nrank_ - 1) * (1,) +
              arg1._denom_ + arg2._drank_ * (1,))
    array1 = arg1._values_.reshape(shape1)

    shape2 = (arg2._shape_ + (arg1._nrank_ - 1) * (1,) + arg2._numer_ +
              arg1._drank_ * (1,) + arg2._denom_)
    array2 = arg2._values_.reshape(shape2)
    k2 += arg1._nrank_ - 1

    # Roll both array axes to the right
    array1 = np.rollaxis(array1, k1, array1.ndim)
    array2 = np.rollaxis(array2, k2, array2.ndim)

    # Make arrays contiguous so sum will run faster
    array1 = np.ascontiguousarray(array1)
    array2 = np.ascontiguousarray(array2)

    # Construct the dot product
    new_values = np.sum(array1 * array2, axis=-1)

    # Construct the object and cast
    new_nrank = arg1._nrank_ + arg2._nrank_ - 2
    new_drank = arg1._drank_ + arg2._drank_

    obj = Qube(new_values,
               Qube.or_(arg1._mask_, arg2._mask_),
               units=Units.mul_units(arg1._units_, arg2._units_),
               nrank=new_nrank, drank=new_drank, example=arg1)
    obj = obj.cast(classes)

    # Insert derivatives if necessary
    if recursive and (arg1._derivs_ or arg2._derivs_):
        new_derivs = {}

        if arg1._derivs_:
            arg2_wod = arg2.wod
            for (key, arg1_deriv) in arg1._derivs_.items():
                new_derivs[key] = Qube.dot(arg1_deriv, arg2_wod, a1, a2,
                                           classes, recursive=False)

        if arg2._derivs_:
            arg1_wod = arg1.wod
            for (key, arg2_deriv) in arg2._derivs_.items():
                term = Qube.dot(arg1_wod, arg2_deriv, a1, a2,
                                classes, recursive=False)
                if key in new_derivs:
                    new_derivs[key] += term
                else:
                    new_derivs[key] = term

        obj.insert_derivs(new_derivs)

    return obj

#===============================================================================
@staticmethod
def norm(arg, axis=-1, classes=(), recursive=True):
    """Calculate the norm of an object along one axis.

    The axes must be in the numerator. The denominator must have zero rank.

    Parameters:
        arg: The object for which to calculate the norm.
        axis (int, optional): The numerator axis for the norm. Defaults to -1.
        classes (tuple, optional): A single class or list or tuple of classes.
            The class of the object returned will be the first suitable class
            in the list. Otherwise, a generic Qube object will be returned.
            Defaults to empty tuple.
        recursive (bool, optional): True to construct the derivatives of the
            norm. Defaults to True.

    Returns:
        Qube: The norm of the object along the specified axis.

    Raises:
        ValueError: If the object has denominators or if the axis is out of
            range.
    """

    if arg._drank_ != 0:
        raise ValueError('%s.norm() does not support denominators'
                         % type(arg).__name__)

    # Position axis from left
    if axis >= 0:
        a1 = axis
    else:
        a1 = axis + arg._nrank_
    if a1 < 0 or a1 >= arg._nrank_:
        raise ValueError('axis is out of range (%d,%d) in %s.norm(): %d'
                         % (-arg._nrank_, arg._nrank_, type(arg).__name__,
                            axis))
    k1 = a1 + len(arg._shape_)

    # Evaluate the norm
    new_values = np.sqrt(np.sum(arg._values_**2, axis=k1))

    # Construct the object and cast
    obj = Qube(new_values,
               arg._mask_,
               nrank=arg._nrank_-1, example=arg)
    obj = obj.cast(classes)

    # Insert derivatives if necessary
    if recursive and arg._derivs_:
        factor = arg.wod / obj
        for (key, arg_deriv) in arg._derivs_.items():
            obj.insert_deriv(key, Qube.dot(factor, arg_deriv, a1, a1,
                                           classes, recursive=False))

    return obj

#===============================================================================
@staticmethod
def norm_sq(arg, axis=-1, classes=(), recursive=True):
    """Calculate the square of the norm of an object along one axis.

    The axes must be in the numerator. The denominator must have zero rank.

    Parameters:
        arg: The object for which to calculate the norm-squared.
        axis (int, optional): The item axis for the norm. Defaults to -1.
        classes (tuple, optional): A single class or list or tuple of classes.
            The class of the object returned will be the first suitable class
            in the list. Otherwise, a generic Qube object will be returned.
            Defaults to empty tuple.
        recursive (bool, optional): True to construct the derivatives of the
            norm-squared. Defaults to True.

    Returns:
        Qube: The square of the norm of the object along the specified axis.

    Raises:
        ValueError: If the object has denominators or if the axis is out of
            range.
    """

    if arg._drank_ != 0:
        raise ValueError('%s.norm_sq() does not support denominators'
                         % type(arg).__name__)

    # Position axis from left
    if axis >= 0:
        a1 = axis
    else:
        a1 = axis + arg._nrank_
    if a1 < 0 or a1 >= arg._nrank_:
        raise ValueError('axis is out of range (%d,%d) in %s.norm_sq(): %d'
                         % (-arg._nrank_, arg._nrank_, type(arg).__name__,
                            axis))
    k1 = a1 + len(arg._shape_)

    # Evaluate the norm
    new_values = np.sum(arg._values_**2, axis=k1)

    # Construct the object and cast
    obj = Qube(new_values,
               arg._mask_,
               units=Units.mul_units(arg._units_, arg._units_),
               nrank=arg._nrank_-1, example=arg)
    obj = obj.cast(classes)

    # Insert derivatives if necessary
    if recursive and arg._derivs_:
        factor = 2.* arg.wod
        for (key, arg_deriv) in arg._derivs_.items():
            obj.insert_deriv(key, Qube.dot(factor, arg_deriv, a1, a1,
                                           classes, recursive=False))

    return obj

#===============================================================================
@staticmethod
def cross(arg1, arg2, axis1=-1, axis2=0, classes=(), recursive=True):
    """Calculate the cross product of two objects.

    Axis lengths must be either two or three, and must be equal. At least one of
    the objects must be lacking a denominator.

    Parameters:
        arg1: The first operand.
        arg2: The second operand.
        axis1 (int, optional): The item axis of the first object. Defaults to -1.
        axis2 (int, optional): The item axis of the second object. Defaults to 0.
        classes (tuple, optional): A single class or list or tuple of classes.
            The class of the object returned will be the first suitable class
            in the list. Otherwise, a generic Qube object will be returned.
            Defaults to empty tuple.
        recursive (bool, optional): True to construct the derivatives of the
            cross product. Defaults to True.

    Returns:
        Qube: The cross product of the two objects.

    Raises:
        ValueError: If both objects have denominators, if axes are out of range,
            or if axis lengths are incompatible.
    """

    # At most one object can have a denominator.
    if arg1._drank_ and arg2._drank_:
        Qube._raise_dual_denoms('cross()', arg1, arg2)

    # Position axis1 from left
    if axis1 >= 0:
        a1 = axis1
    else:
        a1 = axis1 + arg1._nrank_
    if a1 < 0 or a1 >= arg1._nrank_:
        raise ValueError('first axis is out of range (%d,%d) in %s.cross(): %d'
                         % (-arg1._nrank_, arg1._nrank_, type(arg1).__name__,
                            axis1))
    k1 = a1 + len(arg1._shape_)

    # Position axis2 from item left
    if axis2 >= 0:
        a2 = axis2
    else:
        a2 = axis2 + arg2._nrank_
    if a2 < 0 or a2 >= arg2._nrank_:
        raise ValueError('second axis is out of range (%d,%d) in %s.cross(): %d'
                         % (-arg2._nrank_, arg2._nrank_, type(arg2).__name__,
                            axis2))
    k2 = a2 + len(arg2._shape_)

    # Confirm that the axis lengths are compatible
    if ((arg1._numer_[a1] != arg2._numer_[a2]) or
        (arg1._numer_[a1] not in (2,3))):
        raise ValueError('invalid axis length for %s.cross(): %d, %d; '
                         'must be 2 or 3'
                         % (type(arg1).__name__, arg1._numer_[a1],
                            arg2._numer_[a2]))

    # Re-shape the value arrays (shape, numer1, numer2, denom1, denom2)
    shape1 = (arg1._shape_ + arg1._numer_ + (arg2._nrank_ - 1) * (1,) +
              arg1._denom_ + arg2._drank_ * (1,))
    array1 = arg1._values_.reshape(shape1)

    shape2 = (arg2._shape_ + (arg1._nrank_ - 1) * (1,) + arg2._numer_ +
              arg1._drank_ * (1,) + arg2._denom_)
    array2 = arg2._values_.reshape(shape2)
    k2 += arg1._nrank_ - 1

    # Roll both array axes to the right
    array1 = np.rollaxis(array1, k1, array1.ndim)
    array2 = np.rollaxis(array2, k2, array2.ndim)

    new_drank = arg1._drank_ + arg2._drank_

    # Construct the cross product values
    if arg1._numer_[a1] == 3:
        new_values = cross_3x3(array1, array2)

        # Roll the new axis back to its position in arg1
        new_nrank = arg1._nrank_ + arg2._nrank_ - 1
        new_k1 = new_values.ndim - new_drank - new_nrank + a1
        new_values = np.rollaxis(new_values, -1, new_k1)

    else:
        new_values = cross_2x2(array1, array2)
        new_nrank = arg1._nrank_ + arg2._nrank_ - 2

    # Construct the object and cast
    obj = Qube(new_values,
               Qube.or_(arg1._mask_, arg2._mask_),
               units=Units.mul_units(arg1._units_, arg2._units_),
               nrank=new_nrank, drank=new_drank, example=arg1)
    obj = obj.cast(classes)

    # Insert derivatives if necessary
    if recursive and (arg1._derivs_ or arg2._derivs_):
        new_derivs = {}

        if arg1._derivs_:
          arg2_wod = arg2.wod
          for (key, arg1_deriv) in arg1._derivs_.items():
            new_derivs[key] = Qube.cross(arg1_deriv, arg2_wod, a1, a2,
                                         classes, recursive=False)

        if arg2._derivs_:
          arg1_wod = arg1.wod
          for (key, arg2_deriv) in arg2._derivs_.items():
            term = Qube.cross(arg1_wod, arg2_deriv, a1, a2, classes, False)
            if key in new_derivs:
                new_derivs[key] += term
            else:
                new_derivs[key] = term

        obj.insert_derivs(new_derivs)

    return obj

def cross_3x3(a,b):
    """Calculate the cross product of two 3-vectors.

    Stand-alone method to return the cross product of two 3-vectors,
    represented as NumPy arrays.

    Parameters:
        a (ndarray): First 3-vector array.
        b (ndarray): Second 3-vector array.

    Returns:
        ndarray: The cross product of the two 3-vectors.

    Raises:
        ValueError: If the arrays are not 3-vectors.
    """

    (a,b) = np.broadcast_arrays(a,b)
    if not (a.shape[-1] == b.shape[-1] == 3):
        raise ValueError('cross_3x3 requires 3x3 arrays')

    new_values = np.empty(a.shape)
    new_values[...,0] = a[...,1] * b[...,2] - a[...,2] * b[...,1]
    new_values[...,1] = a[...,2] * b[...,0] - a[...,0] * b[...,2]
    new_values[...,2] = a[...,0] * b[...,1] - a[...,1] * b[...,0]

    return new_values

def cross_2x2(a, b):
    """Calculate the cross product of two 2-vectors.

    Stand-alone method to return the cross product of two 2-vectors,
    represented as NumPy arrays.

    Parameters:
        a (ndarray): First 2-vector array.
        b (ndarray): Second 2-vector array.

    Returns:
        ndarray: The cross product of the two 2-vectors.

    Raises:
        ValueError: If the arrays are not 2-vectors.
    """

    (a,b) = np.broadcast_arrays(a,b)
    if not (a.shape[-1] == b.shape[-1] == 2):
        raise ValueError('cross_2x2 requires 2x2 arrays')

    return a[...,0] * b[...,1] - a[...,1] * b[...,0]

#===============================================================================
@staticmethod
def outer(arg1, arg2, classes=(), recursive=True):
    """Calculate the outer product of two objects.

    The item shape of the returned object is obtained by concatenating the two
    numerators and then the two denominators, and each element is the product of
    the corresponding elements of the two objects.

    Parameters:
        arg1: The first operand.
        arg2: The second operand.
        classes (tuple, optional): A single class or list or tuple of classes.
            The class of the object returned will be the first suitable class
            in the list. Otherwise, a generic Qube object will be returned.
            Defaults to empty tuple.
        recursive (bool, optional): True to construct the derivatives of the
            outer product. Defaults to True.

    Returns:
        Qube: The outer product of the two objects.

    Raises:
        ValueError: If both objects have denominators.
    """

    # At most one object can have a denominator. This is sufficient
    # to track first derivatives
    if arg1._drank_ and arg2._drank_:
        Qube._raise_dual_denoms('outer()', arg1, arg2)

    # Re-shape the value arrays (shape, numer1, numer2, denom1, denom2)
    shape1 = (arg1._shape_ + arg1._numer_ + arg2._nrank_ * (1,) +
              arg1._denom_ + arg2._drank_ * (1,))
    array1 = arg1._values_.reshape(shape1)

    shape2 = (arg2._shape_ + arg1._nrank_ * (1,) + arg2._numer_ +
              arg1._drank_ * (1,) + arg2._denom_)
    array2 = arg2._values_.reshape(shape2)

    # Construct the outer product
    new_values = array1 * array2

    # Construct the object and cast
    new_nrank = arg1._nrank_ + arg2._nrank_
    new_drank = arg1._drank_ + arg2._drank_

    obj = Qube(new_values,
               Qube.or_(arg1._mask_, arg2._mask_),
               units=Units.mul_units(arg1._units_, arg2._units_),
               nrank=new_nrank, drank=new_drank, example=arg1)
    obj = obj.cast(classes)

    # Insert derivatives if necessary
    if recursive and (arg1._derivs_ or arg2._derivs_):
        new_derivs = {}

        if arg1._derivs_:
          arg_wod = arg2.wod
          for (key, self_deriv) in arg1._derivs_.items():
            new_derivs[key] = Qube.outer(self_deriv, arg_wod, classes,
                                         recursive=False)

        if arg2._derivs_:
          self_wod = arg1.wod
          for (key, arg_deriv) in arg2._derivs_.items():
            term = Qube.outer(self_wod, arg_deriv, classes, recursive=False)
            if key in new_derivs:
                new_derivs[key] += term
            else:
                new_derivs[key] = term

        obj.insert_derivs(new_derivs)

    return obj

#===============================================================================
@staticmethod
def as_diagonal(arg, axis, classes=(), recursive=True):
    """Return a copy with one axis converted to a diagonal across two.

    Parameters:
        arg: The object to convert.
        axis (int): The item axis to convert to two.
        classes (tuple, optional): A single class or list or tuple of classes.
            The class of the object returned will be the first suitable class
            in the list. Otherwise, a generic Qube object will be returned.
            Defaults to empty tuple.
        recursive (bool, optional): True to include matching slices of the
            derivatives in the returned object; otherwise, the returned object
            will not contain derivatives. Defaults to True.

    Returns:
        Qube: A copy with the specified axis converted to a diagonal.

    Raises:
        ValueError: If the axis is out of range.
    """

    # Position axis from left
    if axis >= 0:
        a1 = axis
    else:
        a1 = axis + arg._nrank_
    if a1 < 0 or a1 >= arg._nrank_:
        raise ValueError('axis is out of range (%d,%d) in %s.as_diagonal(): %d'
                         % (-arg._nrank_, arg._nrank_, type(arg).__name__,
                            axis))

    k1 = a1 + len(arg._shape_)

    # Roll this axis to the end
    rolled = np.rollaxis(arg._values_, k1, arg._values_.ndim)

    # Create the diagonal array
    new_values = np.zeros(rolled.shape + rolled.shape[-1:],
                          dtype=rolled.dtype)

    for i in range(rolled.shape[-1]):
        new_values[...,i,i] = rolled[...,i]

    # Roll the new axes back
    new_values = np.rollaxis(new_values, -1, k1)
    new_values = np.rollaxis(new_values, -1, k1)

    # Construct and cast
    obj = Qube(new_values, arg._mask_,
               nrank=arg._nrank_ + 1, example=arg)
    obj = obj.cast(classes)

    # Diagonalize the derivatives if necessary
    if recursive:
      for (key, deriv) in arg._derivs_.items():
        obj.insert_deriv(key, Qube.as_diagonal(deriv, axis, classes, False))

    return obj

#===============================================================================
def rms(self):
    """Calculate the root-mean-square values of all items as a Scalar.

    Useful for looking at the overall magnitude of the differences between two
    objects.

    Returns:
        Scalar: The root-mean-square values of all items.
    """

    # Evaluate the norm
    sum_sq = np.sum(self._values_**2, axis=tuple(range(-self._rank_,0)))

    return Qube.SCALAR_CLASS(np.sqrt(sum_sq/self.isize), self._mask_)

################################################################################
