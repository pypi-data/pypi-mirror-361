################################################################################
# polymath/extensions/mask_ops.py: masking operations
################################################################################

import numpy as np
from polymath.qube import Qube

def mask_where(self, mask, replace=None, remask=True, recursive=True):
    """Return a copy of this object after a mask has been applied.

    If the mask is empty, this object is returned unchanged.

    Parameters:
        mask (array-like): The mask to apply as a boolean array.
        replace (object, optional): A single replacement value or an object of
            the same shape and class as this object, containing replacement
            values. These are inserted into returned object at every masked
            location. Use None (the default) to leave values unchanged.
        remask (bool, optional): True to leave the new values masked; False to
            replace the values but leave them unmasked. Defaults to True.
        recursive (bool, optional): True to mask the derivatives as well;
            False to leave them unmasked. Defaults to True.

    Returns:
        Qube: A copy of this object with the mask applied.

    Raises:
        ValueError: If the replacement shape is incompatible with the object shape.
    """

    if replace is None and not remask:      # nothing to do
        return self

    # Convert to boolean array if necessary
    mask = Qube._suitable_mask(mask, self._shape_)

    # If the mask is empty, return the object as is
    if not np.any(mask):
        return self

    # Get the replacement value as this type
    if replace is not None:
        replace = self.as_this_type(replace, recursive=True)
        if replace._shape_ not in ((), self._shape_):
            raise ValueError('shape of replacement is incompatible with '
                             'shape of object being masked: %s, %s'
                             % (replace._shape_, self._shape_))

    # Shapeless case
    if np.isscalar(self._values_):
        if replace is None:
            obj = self.copy(recursive=True)
        else:
            obj = replace.copy(recursive=True)

        if remask:
            obj = obj.remask(True, recursive=recursive)

        return obj

    # Case with no replacement
    if replace is None:
        # Note that the new mask must be a copy
        obj = self.remask_or(mask, recursive=True)
        return obj

    # If replacement is an array or single Qube...

    # We need a mask to apply to the given replacement value.
    # If the replacement value has shape, use the existing mask; otherwise,
    # use True, which will allow the replacement to broadcast as needed.
    rep_mask = mask if replace._shape_ else True

    obj = self.copy()
    obj[mask] = replace[rep_mask]   # handles derivatives too!

    if remask:
        obj = obj.remask_or(mask, recursive=recursive)

    return obj

#===============================================================================
def mask_where_eq(self, match, replace=None, remask=True):
    """Return a copy of this object with items equal to a value masked.

    Instead of or in addition to masking the items, the values can be
    replaced. If no items need to be masked, this object is returned
    unchanged.

    Parameters:
        match (object): The item value to match.
        replace (object, optional): A single replacement value or an object of
            the same shape and class as this object, containing replacement
            values. These are inserted into returned object at every masked
            location. Use None (the default) to leave values unchanged.
        remask (bool, optional): True to include the new mask into the object's
            mask; False to replace the values but leave them unmasked.
            Defaults to True.

    Returns:
        Qube: A copy of this object with matching items masked.
    """

    match = self.as_this_type(match, recursive=False)

    axes = tuple(range(-self._rank_, 0))
    mask = np.all(self._values_ == match._values_, axis=axes)

    return self.mask_where(mask, replace=replace, remask=remask)

#===============================================================================
def mask_where_ne(self, match, replace=None, remask=True):
    """Return a copy of this object with items not equal to a value masked.

    Instead of or in addition to masking the items, the values can be replaced.
    If no items need to be masked, this object is returned unchanged.

    Parameters:
        match (object): The item value to match.
        replace (object, optional): A single replacement value or an object of
            the same shape and class as this object, containing replacement
            values. These are inserted into returned object at every masked
            location. Use None (the default) to leave values unchanged.
        remask (bool, optional): True to include the new mask into the object's
            mask; False to replace the values but leave them unmasked.
            Defaults to True.

    Returns:
        Qube: A copy of this object with non-matching items masked.
    """

    match = self.as_this_type(match, recursive=False)

    axes = tuple(range(-self._rank_, 0))
    mask = np.all(self._values_ != match._values_, axis=axes)

    return self.mask_where(mask, replace=replace, remask=remask)

#===============================================================================
def mask_where_le(self, limit, replace=None, remask=True):
    """Return a copy of this object with items <= a limit value masked.

    Instead of or in addition to masking the items, the values can be replaced.
    If no items need to be masked, this object is returned unchanged.

    Parameters:
        limit (object): The limiting value.
        replace (object, optional): A single replacement value or an object of
            the same shape and class as this object, containing replacement
            values. These are inserted into returned object at every masked
            location. Use None (the default) to leave values unchanged.
        remask (bool, optional): True to include the new mask into the object's
            mask; False to replace the values but leave them unmasked.
            Defaults to True.

    Returns:
        Qube: A copy of this object with items <= limit masked.

    Raises:
        ValueError: If this object has denominators or item rank > 0.
    """

    if self._denom_:
        raise ValueError('%s.mask_where_le() does not support denominators'
                         % type(self).__name__)
    if self._numer_:
        raise ValueError('mask_where_le() does not support item rank > 0')

    if isinstance(limit, Qube):
        limit = limit._values_

    return self.mask_where(self._values_ <= limit, replace=replace,
                                                   remask=remask)

#===============================================================================
def mask_where_ge(self, limit, replace=None, remask=True):
    """Return a copy of this object with items >= a limit value masked.

    Instead of or in addition to masking the items, the values can be replaced.
    If no items need to be masked, this object is returned unchanged.

    Parameters:
        limit (object): The limiting value.
        replace (object, optional): A single replacement value or an object of
            the same shape and class as this object, containing replacement
            values. These are inserted into returned object at every masked
            location. Use None (the default) to leave values unchanged.
        remask (bool, optional): True to include the new mask into the object's
            mask; False to replace the values but leave them unmasked.
            Defaults to True.

    Returns:
        Qube: A copy of this object with items >= limit masked.

    Raises:
        ValueError: If this object has denominators or item rank > 0.
    """

    if self._denom_:
        raise ValueError('%s.mask_where_ge() does not support denominators'
                         % type(self).__name__)
    if self._numer_:
        raise ValueError('mask_where_ge() does not support item rank > 0')

    if isinstance(limit, Qube):
        limit = limit._values_

    return self.mask_where(self._values_ >= limit, replace=replace,
                                                   remask=remask)

#===============================================================================
def mask_where_lt(self, limit, replace=None, remask=True):
    """Return a copy with items less than a limit value masked.

    Instead of or in addition to masking the items, the values can be
    replaced. If no items need to be masked, this object is returned
    unchanged.

    Parameters:
        limit (object): The limiting value.
        replace (object, optional): A single replacement value or an object of
            the same shape and class as this object, containing replacement
            values. These are inserted into returned object at every masked
            location. Use None (the default) to leave values unchanged.
        remask (bool, optional): True to include the new mask into the object's
            mask; False to replace the values but leave them unmasked.
            Defaults to True.

    Returns:
        Qube: A copy of this object with items < limit masked.

    Raises:
        ValueError: If this object has denominators or item rank > 0.
    """

    if self._denom_:
        raise ValueError('%s.mask_where_lt() does not support denominators'
                         % type(self).__name__)
    if self._numer_:
        raise ValueError('mask_where_lt() does not support item rank > 0')

    if isinstance(limit, Qube):
        limit = limit._values_

    return self.mask_where(self._values_ < limit, replace=replace,
                                                  remask=remask)

#===============================================================================
def mask_where_gt(self, limit, replace=None, remask=True):
    """Return a copy with items greater than a limit value masked.

    Instead of or in addition to masking the items, the values can be replaced.
    If no items need to be masked, this object is returned unchanged.

    Parameters:
        limit (object): The limiting value.
        replace (object, optional): A single replacement value or an object of
            the same shape and class as this object, containing replacement
            values. These are inserted into returned object at every masked
            location. Use None (the default) to leave values unchanged.
        remask (bool, optional): True to include the new mask into the object's
            mask; False to replace the values but leave them unmasked.
            Defaults to True.

    Returns:
        Qube: A copy of this object with items > limit masked.

    Raises:
        ValueError: If this object has denominators or item rank > 0.
    """

    if self._denom_:
        raise ValueError('%s.mask_where_gt() does not support denominators'
                         % type(self).__name__)
    if self._numer_:
        raise ValueError('mask_where_gt() does not support item rank > 0')

    if isinstance(limit, Qube):
        limit = limit._values_

    return self.mask_where(self._values_ > limit, replace=replace,
                                                  remask=remask)

#===============================================================================
def mask_where_between(self, lower, upper, mask_endpoints=False,
                             replace=None, remask=True):
    """Return a copy with values between two limits masked.

    Instead of or in addition to masking the items, the values can be replaced.
    If no items need to be masked, this object is returned unchanged.

    Parameters:
        lower (object): The lower limit.
        upper (object): The upper limit.
        mask_endpoints (bool or tuple, optional): True to mask the endpoints,
            where values are equal to the lower or upper limits; False to
            exclude the endpoints. Use a tuple of two values to handle the
            endpoints differently. Defaults to False.
        replace (object, optional): A single replacement value or an object of
            the same shape and class as this object, containing replacement
            values. These are inserted into returned object at every masked
            location. Use None (the default) to leave values unchanged.
        remask (bool, optional): True to include the new mask into the object's
            mask; False to replace the values but leave them unmasked.
            Defaults to True.

    Returns:
        Qube: A copy with values between the specified limits masked.

    Raises:
        ValueError: If this object has denominators or item rank > 0.
    """

    if self._denom_:
        raise ValueError('%s.mask_where_between() does not support denominators'
                         % type(self).__name__)
    if self._numer_:
        raise ValueError('mask_where_between() does not support item rank > 0')

    if isinstance(lower, Qube):
        lower = lower._values_

    if isinstance(upper, Qube):
        upper = upper._values_

    # To minimize the number of array operations, identify the options first
    if not isinstance(mask_endpoints, (tuple, list)):
        mask_endpoints = (mask_endpoints, mask_endpoints)

    if mask_endpoints[0]:               # lower point included in the mask
        op0 = self._values_.__ge__
    else:                               # lower point excluded from the mask
        op0 = self._values_.__gt__

    if mask_endpoints[1]:               # upper point included in the mask
        op1 = self._values_.__le__
    else:                               # upper point excluded from the mask
        op1 = self._values_.__lt__

    mask = op0(lower) & op1(upper)

    return self.mask_where(mask, replace=replace, remask=remask)

#===============================================================================
def mask_where_outside(self, lower, upper, mask_endpoints=False, replace=None,
                             remask=True):
    """Return a copy with values outside two limits masked.

    Instead of or in addition to masking the items, the values can be replaced.
    If no items need to be masked, this object is returned unchanged.

    Parameters:
        lower (object): The lower limit.
        upper (object): The upper limit.
        mask_endpoints (bool or tuple, optional): True to mask the endpoints,
            where values are equal to the lower or upper limits; False to
            exclude the endpoints. Use a tuple of two values to handle the
            endpoints differently. Defaults to False.
        replace (object, optional): A single replacement value or an object of
            the same shape and class as this object, containing replacement
            values. These are inserted into returned object at every masked
            location. Use None (the default) to leave values unchanged.
        remask (bool, optional): True to include the new mask into the object's
            mask; False to replace the values but leave them unmasked.
            Defaults to True.

    Returns:
        Qube: A copy with values outside the specified limits masked.

    Raises:
        ValueError: If this object has denominators or item rank > 0.
    """

    if self._denom_:
        raise ValueError('%s.mask_where_outside() does not support denominators'
                         % type(self).__name__)
    if self._numer_:
        raise ValueError('mask_where_outside() does not support item rank > 0')

    if isinstance(lower, Qube):
        lower = lower._values_

    if isinstance(upper, Qube):
        upper = upper._values_

    # To minimize the number of array operations, identify the options first
    if not isinstance(mask_endpoints, (tuple, list)):
        mask_endpoints = (mask_endpoints, mask_endpoints)

    if mask_endpoints[0]:               # end points are included in the mask
        op0 = self._values_.__le__
    else:                               # end points are excluded from the mask
        op0 = self._values_.__lt__

    if mask_endpoints[1]:               # end points are included in the mask
        op1 = self._values_.__ge__
    else:                               # end points are excluded from the mask
        op1 = self._values_.__gt__

    mask = op0(lower) | op1(upper)

    return self.mask_where(mask, replace=replace, remask=remask)

#===============================================================================
def clip(self, lower, upper, remask=True, inclusive=True):
    """Return a copy with values clipped to fall within a pair of limits.

    Values below the lower limit become equal to the lower limit; values above
    the upper limit become equal to the upper limit.

    Parameters:
        lower (object, optional): The lower limit or an object of the same
            shape and type as this, containing lower limits. None or masked
            values to ignore.
        upper (object, optional): The upper limit or an object of the same
            shape and type as this, containing upper limits. None or masked
            values to ignore.
        remask (bool, optional): True to include the new mask into the object's
            mask; False to replace the values but leave them unmasked.
            Defaults to True.
        inclusive (bool, optional): True to leave values that exactly match
            the upper limit unmasked; False to mask them. Defaults to True.

    Returns:
        Qube: A copy with values clipped to the specified limits.

    Raises:
        ValueError: If this object has denominators or item rank > 0.
    """

    if self._denom_:
        raise ValueError('%s.clip() does not support denominators'
                         % type(self).__name__)
    if self._numer_:
        raise ValueError('clip() does not support item rank > 0')

    # Easy case...
    if np.isscalar(lower) and np.isscalar(upper):
        new_values = np.clip(self._values_, lower, upper)
        if remask:
            outside = Qube.is_outside(self._values_, lower, upper, inclusive)
            mask = Qube.or_(self._mask_, outside)
        else:
            mask = self._mask_

        # Without remasking, derivatives out of range are now all zero
        if self._derivs_ and not remask:
            new_derivs = {}
            outside = Qube.is_outside(self._values_, lower, upper, inclusive)
            for key, deriv in self._derivs_.items():
                new_deriv = deriv.copy()
                new_deriv[outside] = deriv.zero()
                new_derivs[key] = new_deriv
        else:
            new_derivs = self._derivs_

        result = Qube.__new__(type(self))
        result.__init__(new_values, mask, derivs=new_derivs, example=self)
        return result

    result = self

    if lower is not None:
        result = result.mask_where(result._values_ < lower, replace=lower,
                                                            remask=remask)

    if upper is not None:
        if inclusive:
            result = result.mask_where(result._values_ > upper, replace=upper,
                                                                remask=remask)
        else:
            result = result.mask_where(result._values_ >= upper, replace=upper,
                                                                 remask=remask)

    return result

################################################################################
# Convenience methods for range masks and clipping
################################################################################

@staticmethod
def is_below(arg, high, inclusive=True):
    """Check if arg is inside a range with upper end at high.

    Parameters:
        arg (object): The value to check.
        high (object): The upper limit of the range.
        inclusive (bool, optional): True to include the upper limit in the
            range; False to exclude it. Defaults to True.

    Returns:
        bool: True if arg is inside the range with upper end at high.
    """

    if inclusive:
        return arg <= high
    else:
        return arg < high

@staticmethod
def is_above(arg, high, inclusive=True):
    """Check if arg is outside a range with upper end at high.

    Parameters:
        arg (object): The value to check.
        high (object): The upper limit of the range.
        inclusive (bool, optional): True to include the upper limit in the
            range; False to exclude it. Defaults to True.

    Returns:
        bool: True if arg is outside the range with upper end at high.
    """

    if inclusive:
        return arg > high
    else:
        return arg >= high

@staticmethod
def is_outside(arg, low, high, inclusive=True):
    """Check if arg is outside the range low to high.

    Parameters:
        arg (object): The value to check.
        low (object): The lower limit of the range.
        high (object): The upper limit of the range.
        inclusive (bool, optional): True to include the upper limit in the
            range; False to exclude it. Defaults to True.

    Returns:
        bool: True if arg is outside the range low to high.
    """

    if inclusive:
        return (arg < low) | (arg > high)
    else:
        return (arg < low) | (arg >= high)

@staticmethod
def is_inside(arg, low, high, inclusive=True):
    """Check if arg is inside the range low to high.

    Parameters:
        arg (object): The value to check.
        low (object): The lower limit of the range.
        high (object): The upper limit of the range.
        inclusive (bool, optional): True to include the upper limit in the
            range; False to exclude it. Defaults to True.

    Returns:
        bool: True if arg is inside the range low to high.
    """

    if inclusive:
        return (arg >= low) & (arg <= high)
    else:
        return (arg >= low) & (arg < high)

################################################################################
