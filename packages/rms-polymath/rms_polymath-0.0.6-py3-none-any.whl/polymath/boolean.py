################################################################################
# polymath/boolean.py: Boolean subclass of PolyMath base class
################################################################################

from __future__ import division
import numpy as np

from polymath.qube   import Qube
from polymath.scalar import Scalar

class Boolean(Scalar):
    """Represent boolean values in the PolyMath framework.

    This class handles boolean values with masking support. Masked values are
    considered unknown, neither True nor False.
    """

    NRANK = 0           # the number of numerator axes.
    NUMER = ()          # shape of the numerator.

    FLOATS_OK = False   # True to allow floating-point numbers.
    INTS_OK = False     # True to allow integers.
    BOOLS_OK = True     # True to allow booleans.

    UNITS_OK = False    # True to allow units; False to disallow them.
    DERIVS_OK = False   # True to allow derivatives and to allow this class to
                        # have a denominator; False to disallow them.

    DEFAULT_VALUE = False

    #===========================================================================
    @staticmethod
    def as_boolean(arg, recursive=True):
        """Convert the argument to Boolean if possible.

        Parameters:
            arg (object): The object to convert to Boolean.
            recursive (bool, optional): This parameter is ignored for Boolean
                class but included for compatibility. Default is True.

        Returns:
            Boolean: The converted Boolean object.
        """

        if isinstance(arg, Boolean):
            return arg

        if isinstance(arg, np.bool_):   # np.bool_ is not a subclass of bool
            arg = bool(arg)

        return Boolean(arg, units=False, derivs={})

    #===========================================================================
    def as_int(self):
        """Return a Scalar of integers equal to one where True, zero where False.

        This method overrides the default behavior defined in the base class to
        return a Scalar of ints instead of a Boolean. True become one; False
        becomes zero.

        Returns:
            Scalar: An integer Scalar with ones where this object is True, zeros
            where False.
        """

        if np.isscalar(self._values_):
            result = Scalar(int(self._values_))
        else:
            result = Scalar(self._values_.astype('int'))

        return result

    #===========================================================================
    def as_float(self):
        """Return a floating-point numeric version of this object.

        This method overrides the default behavior defined in the base class to
        return a Scalar of floats instead of a Boolean. True become one; False
        becomes zero.

        Returns:
            Scalar: A float Scalar with ones where this object is True, zeros
            where False.
        """

        if np.isscalar(self._values_):
            result = Scalar(float(self._values_))
        else:
            result = Scalar(self._values_.astype('float'))

        return result

    #===========================================================================
    def as_numeric(self):
        """Return a numeric version of this object.

        This method overrides the default behavior defined in the base class to
        return a Scalar of ints instead of a Boolean.

        Returns:
            Scalar: An integer Scalar with ones where this object is True, zeros
            where False.
        """

        return self.as_int()

    #===========================================================================
    def as_index(self):
        """Return an object suitable for indexing a NumPy ndarray.

        Returns:
            ndarray: A boolean array with False values where masked.
        """

        return (self._values_ & self.antimask)

    #===========================================================================
    def is_numeric(self):
        """Return True if this object is numeric; False otherwise.

        This method overrides the default behavior in the base class to return
        return False. Every other subclass is numeric.

        Returns:
            bool: Always False for Boolean objects.
        """

        return False

    #===========================================================================
    def sum(self, axis=None, value=True, builtins=None,
                  recursive=True, out=None):
        """Return the sum of the unmasked values along the specified axis.

        Parameters:
            axis (int or tuple, optional): An integer axis or a tuple of axes. The
                sum is determined across these axes, leaving any remaining axes in
                the returned value. If None (the default), then the sum is
                performed across all axes of the object.
            value (bool, optional): Value to match. Default is True.
            builtins (bool, optional): If True and the result is a single unmasked
                scalar, the result is returned as a Python int or float instead of
                as an instance of Qube. Default is that specified by
                Qube.PREFER_BUILTIN_TYPES.
            recursive (bool, optional): Ignored for class Boolean. Default is True.
            out (object, optional): Ignored. Enables "np.sum(Qube)" to work.
                Default is None.

        Returns:
            Scalar: The sum of matched values (True or False) along the specified
            axis.
        """

        if value:
            return self.as_int().sum(axis=axis, builtins=builtins)
        else:
            return (Scalar.ONE - self.as_int()).sum(axis=axis,
                                                    builtins=builtins)

    #===========================================================================
    def identity(self):
        """Return an object of this subclass equivalent to the identity.

        Returns:
            Boolean: A read-only Boolean with value True.
        """

        return Boolean(True).as_readonly()

    ############################################################################
    # Arithmetic operators
    ############################################################################

    def __pos__(self, recursive=True):
        """Return the integer equivalent of this Boolean.

        Parameters:
            recursive (bool, optional): Ignored for Boolean. Default is True.

        Returns:
            Scalar: An integer Scalar with ones where this object is True, zeros
            where False.
        """
        return self.as_int()

    def __neg__(self, recursive=True):
        """Return the negated integer equivalent of this Boolean.

        Parameters:
            recursive (bool, optional): Ignored for Boolean. Default is True.

        Returns:
            Scalar: A negated integer Scalar (-1 where True, 0 where False).
        """
        return -self.as_int()

    def __abs__(self, recursive=True):
        """Return the absolute value of this Boolean as an integer.

        Parameters:
            recursive (bool, optional): Ignored for Boolean. Default is True.

        Returns:
            Scalar: An integer Scalar with ones where this object is True, zeros
            where False.
        """
        return self.as_int()

    def __add__(self, arg, recursive=True):
        """Return the sum of this Boolean (as integer) and the argument.

        Parameters:
            arg: The value to add to this Boolean (treated as integer).
            recursive (bool, optional): Ignored for Boolean. Default is True.

        Returns:
            Scalar: The sum of this Boolean (as integer) and the argument.
        """
        return self.as_int() + arg

    def __radd__(self, arg, recursive=True):
        """Return the sum of the argument and this Boolean (as integer).

        Parameters:
            arg: The value to which this Boolean (treated as integer) is added.
            recursive (bool, optional): Ignored for Boolean. Default is True.

        Returns:
            Scalar: The sum of the argument and this Boolean (as integer).
        """
        return self.as_int() + arg

    def __iadd__(self, arg):
        """Raise exception as in-place addition is not supported for Boolean.

        Parameters:
            arg: The value to add to this Boolean.

        Raises:
            ValueError: Always, as in-place addition is not supported for Boolean.
        """
        Qube._raise_unsupported_op('+=', self)

    def __sub__(self, arg, recursive=True):
        """Return the difference between this Boolean (as integer) and the argument.

        Parameters:
            arg: The value to subtract from this Boolean (treated as integer).
            recursive (bool, optional): Ignored for Boolean. Default is True.

        Returns:
            Scalar: The difference between this Boolean (as integer) and the argument.
        """
        return self.as_int() - arg

    def __rsub__(self, arg, recursive=True):
        """Return the difference between the argument and this Boolean (as integer).

        Parameters:
            arg: The value from which this Boolean (treated as integer) is subtracted.
            recursive (bool, optional): Ignored for Boolean. Default is True.

        Returns:
            Scalar: The difference between the argument and this Boolean (as integer).
        """
        return -self.as_int() + arg

    def __isub__(self, arg):
        """Raise exception as in-place subtraction is not supported for Boolean.

        Parameters:
            arg: The value to subtract from this Boolean.

        Raises:
            ValueError: Always, as in-place subtraction is not supported for Boolean.
        """
        Qube._raise_unsupported_op('-=', self)

    def __mul__(self, arg, recursive=True):
        """Return the product of this Boolean (as integer) and the argument.

        Parameters:
            arg: The value to multiply with this Boolean (treated as integer).
            recursive (bool, optional): Ignored for Boolean. Default is True.

        Returns:
            Scalar: The product of this Boolean (as integer) and the argument.
        """
        return self.as_int() * arg

    def __rmul__(self, arg, recursive=True):
        """Return the product of the argument and this Boolean (as integer).

        Parameters:
            arg: The value by which this Boolean (treated as integer) is multiplied.
            recursive (bool, optional): Ignored for Boolean. Default is True.

        Returns:
            Scalar: The product of the argument and this Boolean (as integer).
        """
        return self.as_int() * arg

    def __imul__(self, arg):
        """Raise exception as in-place multiplication is not supported for Boolean.

        Parameters:
            arg: The value to multiply with this Boolean.

        Raises:
            ValueError: Always, as in-place multiplication is not supported for Boolean.
        """
        Qube._raise_unsupported_op('*=', self)

    def __truediv__(self, arg, recursive=True):
        """Return the division of this Boolean (as integer) by the argument.

        Parameters:
            arg: The value by which this Boolean (treated as integer) is divided.
            recursive (bool, optional): Ignored for Boolean. Default is True.

        Returns:
            Scalar: The result of dividing this Boolean (as integer) by the argument.
        """
        return self.as_int() / arg

    def __rtruediv__(self, arg, recursive=True):
        """Return the division of the argument by this Boolean (as integer).

        Parameters:
            arg: The value to be divided by this Boolean (treated as integer).
            recursive (bool, optional): Ignored for Boolean. Default is True.

        Returns:
            Scalar: The result of dividing the argument by this Boolean (as integer).
        """
        if not isinstance(arg, Qube):
            arg = Scalar(arg)
        return arg / self.as_int()

    def __itruediv__(self, arg):
        """Raise exception as in-place division is not supported for Boolean.

        Parameters:
            arg: The value by which this Boolean should be divided.

        Raises:
            ValueError: Always, as in-place division is not supported for Boolean.
        """
        Qube._raise_unsupported_op('/=', self)

    def __floordiv__(self, arg):
        """Return the floor division of this Boolean (as integer) by the argument.

        Parameters:
            arg: The value by which this Boolean (treated as integer) is floor-divided.

        Returns:
            Scalar: The result of floor division of this Boolean (as integer) by the
            argument.
        """
        return self.as_int() // arg

    def __rfloordiv__(self, arg):
        """Return the floor division of the argument by this Boolean (as integer).

        Parameters:
            arg: The value to be floor-divided by this Boolean (treated as integer).

        Returns:
            Scalar: The result of floor division of the argument by this Boolean
            (as integer).
        """
        if not isinstance(arg, Qube):
            arg = Scalar(arg)
        return arg // self.as_int()

    def __ifloordiv__(self, arg):
        """Raise exception as in-place floor division is not supported for Boolean.

        Parameters:
            arg: The value by which this Boolean should be floor-divided.

        Raises:
            ValueError: Always, as in-place floor division is not supported for Boolean.
        """
        Qube._raise_unsupported_op('//=', self)

    def __mod__(self, arg):
        """Return the modulo of this Boolean (as integer) and the argument.

        Parameters:
            arg: The value by which this Boolean (treated as integer) is modulo-divided.

        Returns:
            Scalar: The remainder after dividing this Boolean (as integer) by the
            argument.
        """
        return self.as_int() % arg

    def __rmod__(self, arg):
        """Return the modulo of the argument and this Boolean (as integer).

        Parameters:
            arg: The value to be modulo-divided by this Boolean (treated as integer).

        Returns:
            Scalar: The remainder after dividing the argument by this Boolean
            (as integer).
        """
        if not isinstance(arg, Qube):
            arg = Scalar(arg)
        return arg % self.as_int()

    def __imod__(self, arg):
        """Raise exception as in-place modulo is not supported for Boolean.

        Parameters:
            arg: The value by which this Boolean should be modulo-divided.

        Raises:
            ValueError: Always, as in-place modulo is not supported for Boolean.
        """
        Qube._raise_unsupported_op('%=', self)

    def __pow__(self, arg):
        """Return this Boolean (as integer) raised to the power of the argument.

        Parameters:
            arg: The power to which this Boolean (treated as integer) is raised.

        Returns:
            Scalar: This Boolean (as integer) raised to the power of the argument.
        """
        return self.as_int()**arg

################################################################################
# Useful class constants
################################################################################

Boolean.TRUE = Boolean(True).as_readonly()
Boolean.FALSE = Boolean(False).as_readonly()
Boolean.MASKED = Boolean(False,True).as_readonly()

################################################################################
# Once the load is complete, we can fill in a reference to the Boolean class
# inside the Qube object.
################################################################################

Qube.BOOLEAN_CLASS = Boolean

################################################################################
