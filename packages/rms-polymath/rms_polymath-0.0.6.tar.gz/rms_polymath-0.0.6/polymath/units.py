################################################################################
# polymath/units.py: Units class
################################################################################

from __future__ import division

import numpy as np
import numbers

#===============================================================================
# Definition of the gcd function is under the fractions module in Python 2 but
# under the math module in Python 3. Rather than deal with the inconsistency,
# we simply define it again here.

def _gcd(a, b):
    """Calculate the Greatest Common Divisor of a and b.

    Unless b==0, the result will have the same sign as b (so that when
    b is divided by it, the result comes out positive).
    """

    while b:
        a, b = b, a%b
    return a

#===============================================================================
class Units(object):
    """Represent units and provide conversion methods.

    This class defines unit names and methods for converting between values
    that include units. Units are represented by exponents on distance, time,
    and angle dimensions.
    """

    def __init__(self, exponents, triple, name=None):
        """Initialize a Units object.

        Parameters:
            exponents (tuple): A tuple of integers defining the exponents on
                distance, time and angle that are used for this set of units.
            triple (tuple): A tuple containing:
                [0] The numerator of a factor that converts from a value in
                these units to a value in standard units of km, seconds
                and/or radians.
                [1] The denominator of this same factor.
                [2] The exponent on pi that should multiply the numerator of
                this factor.
            name (str or dict, optional): The name of the units. It is
                represented by a string or by a dictionary of unit exponents
                keyed by the unit names. Defaults to None.

        Note:
            For example, units of degrees would have a triple (1,180,1). This
            defines a factor pi/180, which converts from degrees to radians.
        """

        self.exponents = tuple(exponents)

        # Convert to coefficients to ints with lowest common denominator
        # if possible
        (numer, denom) = triple[:2]

        # Scale by 256 to compensate for possible floats that can be represented
        # exactly
        numer = int(triple[0] * 256)
        denom = int(triple[1] * 256)

        gcd_value = _gcd(numer, denom)
        numer //= gcd_value
        denom //= gcd_value

        if numer * triple[1] != denom * triple[0]:
            numer = triple[0]
            denom = triple[1]

        pi_expo = triple[2]

        self.triple = (numer, denom, pi_expo)

        # Factor to convert from these units to standard units
        self.factor = (numer / denom) * np.pi**pi_expo

        # Factor to convert from standard units to these units
        self.factor_inv = (denom / numer) / np.pi**pi_expo

        # Fill in the name
        self.name = name

    @property
    def from_units_factor(self):
        return self.factor

    @property
    def into_units_factor(self):
        return self.factor_inv

    @staticmethod
    def as_units(arg):
        """Convert the given argument to a Unit object.

        Parameters:
            arg: The argument to convert. Can be an object of class Unit, one
                of the standard unit names, or None.

        Returns:
            Units or None: The converted Units object, or None if arg is None.

        Raises:
            ValueError: If the argument is not a recognized unit.
        """

        if arg is None:
            return None
        elif isinstance(arg, str):
            return Units.NAME_TO_UNIT[arg]
        elif isinstance(arg, Units):
            return arg
        else:
            raise ValueError("not a recognized unit: " + str(arg))

    @staticmethod
    def can_match(first, second):
        """Check if the units can match.

        Parameters:
            first (Units or None): The first units object.
            second (Units or None): The second units object.

        Returns:
            bool: True if the units can match, meaning that either they have
                the same exponents or one or both are None.
        """

        if first is None or second is None:
            return True

        return first.exponents == second.exponents

    @staticmethod
    def require_compatible(first, second):
        """Raise a ValueError if the arguments are not compatible units.

        Parameters:
            first (Units or None): The first units object.
            second (Units or None): The second units object.

        Raises:
            ValueError: If the units are not compatible.
        """

        if not Units.can_match(first, second):
            raise ValueError('units are not compatible')

    @staticmethod
    def do_match(first, second):
        """Check if the units match.

        Parameters:
            first (Units or None): The first units object.
            second (Units or None): The second units object.

        Returns:
            bool: True if the units match, meaning that they have the same
                exponents. Values of None are treated as equivalent to unitless.
        """

        if first is None:
            first = Units.UNITLESS
        if second is None:
            second = Units.UNITLESS

        return first.exponents == second.exponents

    @staticmethod
    def require_match(first, second):
        """Raise a ValueError if the units are not the same.

        Parameters:
            first (Units or None): The first units object.
            second (Units or None): The second units object.

        Raises:
            ValueError: If the units are not compatible.
        """

        if not Units.do_match(first, second):
            raise ValueError('units are not compatible')

    @staticmethod
    def is_angle(arg):
        """Check if the argument could be used as an angle.

        Parameters:
            arg (Units or None): The units object to check.

        Returns:
            bool: True if the argument could be used as an angle.
        """

        if arg is None:
            return True
        return (arg.exponents in ((0,0,0), (0,0,1)))

    @staticmethod
    def require_angle(arg):
        """Raise a ValueError if the argument could not be used as an angle.

        Parameters:
            arg (Units or None): The units object to check.

        Raises:
            ValueError: If the units are incompatible with an angle.
        """

        if not Units.is_angle(arg):
            raise ValueError('units are incompatible with an angle')

    @staticmethod
    def is_unitless(arg):
        """Check if the argument is unitless.

        Parameters:
            arg (Units or None): The units object to check.

        Returns:
            bool: True if the argument is unitless.
        """

        if arg is None:
            return True
        return (arg.exponents == (0,0,0))

    @staticmethod
    def require_unitless(arg):
        """Raise a ValueError if the argument is not unitless.

        Parameters:
            arg (Units or None): The units object to check.

        Raises:
            ValueError: If units are not permitted.
        """

        if not Units.is_unitless(arg):
            raise ValueError('units are not permitted')

    def from_this(self, value):
        """Convert a scalar or numpy array in these units to standard units.

        Parameters:
            value (scalar or ndarray): The value to convert from these units
                to standard units of km, seconds and radians.

        Returns:
            scalar or ndarray: The converted value in standard units.
        """

        return self.factor * value

    def into_this(self, value):
        """Convert a scalar or numpy array from standard units to these units.

        Parameters:
            value (scalar or ndarray): The value to convert from standard units
                to these units.

        Returns:
            scalar or ndarray: The converted value in these units.
        """

        return self.factor_inv * value

    @staticmethod
    def from_units(units, value):
        """Convert a scalar or numpy array in the given units to standard units.

        Parameters:
            units (Units or None): The units to convert from.
            value (scalar or ndarray): The value to convert.

        Returns:
            scalar or ndarray: The converted value in standard units of km,
                seconds and radians.
        """

        if units is None:
            return value

        return units.factor * value

    @staticmethod
    def into_units(units, value):
        """Convert a scalar or numpy array from standard units to given units.

        Parameters:
            units (Units or None): The units to convert to.
            value (scalar or ndarray): The value to convert.

        Returns:
            scalar or ndarray: The converted value in the given units.
        """

        if units is None:
            return value

        return units.factor_inv * value

    def convert(self, value, units):
        """Convert the units of a scalar or NumPy array.

        The value is assumed to be in these units, and it is returned in the
        new units specified. Conversions are exact whenever possible.

        Parameters:
            value (scalar or ndarray): The value to convert.
            units (Units or None): The target units. If None, converts to
                unitless.

        Returns:
            scalar or ndarray: The converted value in the target units.

        Raises:
            ValueError: If the units are incompatible for conversion.
        """

        if units is None:
            units = Units.UNITLESS

        if self.exponents != units.exponents:
            raise ValueError("cannot convert units " + self.get_name() +
                             " to " + units.get_name())

        # If the factor is unity, return the value without modification
        if (self.triple[2] == units.triple[2] and
            self.triple[0]*units.triple[1] == self.triple[1]*units.triple[0]):
                return value

        return ((self.triple[0] * units.triple[1]) * value /
                (self.triple[1] * units.triple[0]) *
                np.pi**(self.triple[2] - units.triple[2]))

    ############################################################################
    # Arithmetic operators
    ############################################################################

    def __mul__(self, arg):
        """Multiply this Units object by another Units object or scalar.

        Parameters:
            arg (Units, None, or numbers.Real): The object to multiply by.

        Returns:
            Units: The product of the units multiplication.

        Raises:
            NotImplementedError: If the argument type is not supported.
        """

        if isinstance(arg, Units):
            return Units((self.exponents[0] + arg.exponents[0],
                          self.exponents[1] + arg.exponents[1],
                          self.exponents[2] + arg.exponents[2]),
                         (self.triple[0] * arg.triple[0],
                          self.triple[1] * arg.triple[1],
                          self.triple[2] + arg.triple[2]),
                         Units.mul_names(self.name, arg.name))

        if arg is None:
            return self

        if isinstance(arg, numbers.Real):
            return self * (Units((0,0,0), (arg,1,0)))

        return NotImplemented

    def __rmul__(self, arg):
        return self.__mul__(arg)

    def __div__(self, arg):
        return self.__truediv__(arg)

    def __rdiv__(self, arg):
        return self.__rtruediv__(arg)

    def __truediv__(self, arg):
        """Divide this Units object by another Units object or scalar.

        Parameters:
            arg (Units, None, or numbers.Real): The object to divide by.

        Returns:
            Units: The quotient of the units division.

        Raises:
            NotImplementedError: If the argument type is not supported.
        """

        if isinstance(arg, Units):
            return Units((self.exponents[0] - arg.exponents[0],
                          self.exponents[1] - arg.exponents[1],
                          self.exponents[2] - arg.exponents[2]),
                         (self.triple[0] * arg.triple[1],
                          self.triple[1] * arg.triple[0],
                          self.triple[2] - arg.triple[2]),
                         Units.div_names(self.name, arg.name))

        if arg is None:
            return self

        if isinstance(arg, numbers.Real):
            return self * (Units((0,0,0), (1,arg,0)))

        return NotImplemented

    def __rtruediv__(self, arg):
        """Divide a scalar by this Units object.

        Parameters:
            arg (None or numbers.Real): The scalar to divide.

        Returns:
            Units: The reciprocal of this Units object multiplied by arg.

        Raises:
            NotImplementedError: If the argument type is not supported.
        """

        if arg is None:
            arg = 1.

        if isinstance(arg, numbers.Real):
            return (self / arg)**(-1)

        return NotImplemented

    def __pow__(self, power):
        """Raise this Units object to the specified power.

        Parameters:
            power (int or float): The exponent. Must be an integer or
                half-integer.

        Returns:
            Units: This Units object raised to the specified power.

        Raises:
            ValueError: If the power is not an integer or half-integer.
        """

        ipower = int(power)
        if power != ipower:
            if 2*power == int(2*power):
                return self.sqrt()**(int(2*power))
            else:
                raise ValueError("units can only be raised to integer or " +
                                 "half-integer powers: " + str(power))
        else:
            power = ipower

        if power > 0:
            return Units((power * self.exponents[0],
                          power * self.exponents[1],
                          power * self.exponents[2]),
                         (self.triple[0]**power,
                          self.triple[1]**power,
                          power * self.triple[2]),
                         Units.name_power(self.name, power))
        else:
            return Units((power * self.exponents[0],
                          power * self.exponents[1],
                          power * self.exponents[2]),
                         (self.triple[1]**(-power),
                          self.triple[0]**(-power),
                          power * self.triple[2]),
                         Units.name_power(self.name, power))

    def sqrt(self, name=None):
        """Return the square root of this Units object.

        Parameters:
            name (str or dict, optional): The name for the resulting units.
                Defaults to None.

        Returns:
            Units: The square root of this Units object.

        Raises:
            ValueError: If the exponents are not even numbers.
        """

        if (self.exponents[0] % 2 != 0 or
            self.exponents[1] % 2 != 0 or
            self.exponents[2] % 2 != 0):
                raise ValueError("illegal units for sqrt(): " + self.get_name())

        exponents = (self.exponents[0]//2, self.exponents[1]//2,
                                           self.exponents[2]//2)

        numer = np.sqrt(self.triple[0])
        denom = np.sqrt(self.triple[1])
        if numer == int(numer):
            numer = int(numer)
        if denom == int(denom):
            denom = int(denom)

        pi_expo = self.triple[2] // 2
        if self.triple[2] != 2*pi_expo:
            numer *= np.pi**(self.triple[2] / 2.)
            pi_expo = 0

        if name is None:
            name = Units.name_power(self.name, 0.5)

        return Units(exponents, (numer, denom, pi_expo), name)

    #####################################################
    # Static versions of arithmetic operations
    #####################################################

    @staticmethod
    def mul_units(arg1, arg2, name=None):
        """Multiply two Units objects.

        Parameters:
            arg1 (Units or None): The first Units object.
            arg2 (Units or None): The second Units object.
            name (str or dict, optional): The name for the resulting units.
                Defaults to None.

        Returns:
            Units or None: The product of the two Units objects, or None if
                both arguments are None.
        """

        if arg2 is None:
            result = arg1
        elif arg1 is None:
            result = arg2
        else:
            result = arg1 * arg2

        if result is not None:
            result.name = name

        return result

    @staticmethod
    def div_units(arg1, arg2, name=None):
        """Divide two Units objects.

        Parameters:
            arg1 (Units or None): The numerator Units object.
            arg2 (Units or None): The denominator Units object.
            name (str or dict, optional): The name for the resulting units.
                Defaults to None.

        Returns:
            Units or None: The quotient of the two Units objects, or None if
                both arguments are None.
        """

        if arg2 is None:
            result = arg1
        elif arg1 is None:
            result = arg2**(-1)
        else:
            result = arg1 / arg2

        if result is not None:
            result.name = name

        return result

    @staticmethod
    def sqrt_units(units, name=None):
        """Return the square root of a Units object.

        Parameters:
            units (Units or None): The Units object to take the square root of.
            name (str or dict, optional): The name for the resulting units.
                Defaults to None.

        Returns:
            Units or None: The square root of the Units object, or None if
                units is None.

        Raises:
            ValueError: If the exponents are not even numbers.
        """

        if units is None:
            return None

        return units.sqrt(name)

    @staticmethod
    def units_power(units, power, name=None):
        """Raise a Units object to the specified power.

        Parameters:
            units (Units or None): The Units object to raise to a power.
            power (int or float): The exponent. Must be an integer or
                half-integer.
            name (str or dict, optional): The name for the resulting units.
                Defaults to None.

        Returns:
            Units or None: The Units object raised to the specified power, or
                None if units is None.

        Raises:
            ValueError: If the power is not an integer or half-integer.
        """

        if units is None:
            return None

        result = units**power
        result.set_name(name)
        return result

    ############################################################################
    # Comparison operators
    ############################################################################

    def __eq__(self, arg):
        """Check if this Units object equals another.

        Parameters:
            arg (Units or None): The Units object to compare with.

        Returns:
            bool: True if the Units objects are equal, False otherwise.
        """

        if not isinstance(arg, Units):
            return False

        return (self.exponents == arg.exponents and self.factor == arg.factor)

    def __ne__(self, arg):
        """Check if this Units object does not equal another.

        Parameters:
            arg (Units or None): The Units object to compare with.

        Returns:
            bool: True if the Units objects are not equal, False otherwise.
        """

        if not isinstance(arg, Units):
            return True

        return (self.exponents != arg.exponents or self.factor != arg.factor)

    ############################################################################
    # Copy operations
    ############################################################################

    def __copy__(self):
        return Units(self.exponents, self.triple, self.name)

    def copy(self):
        """Return a copy of this Units object.

        Returns:
            Units: A copy of this Units object.
        """

        return self.__copy__()

    ############################################################################
    # String operations
    ############################################################################

    def __str__(self):
        """Return a string representation of this Units object.

        Returns:
            str: A string representation of the units.
        """

        return "Units(" + self.get_name() + ")"

    def __repr__(self):
        """Return a detailed string representation of this Units object.

        Returns:
            str: A detailed string representation of the units.
        """

        return str(self)

    @staticmethod
    def mul_names(name1, name2):
        """Multiply two unit names.

        Parameters:
            name1 (str, dict, or None): The first unit name.
            name2 (str, dict, or None): The second unit name.

        Returns:
            str or dict or None: The product of the two unit names, or None if
                both arguments are None.
        """

        if name1 is None or name2 is None:
            return None

        name1 = Units.name_to_dict(name1)
        name2 = Units.name_to_dict(name2)

        new_name = name1.copy()
        for (key,expo) in name2.items():
            if key in new_name:
                expo += new_name[key]

            if expo == 0:
                del new_name[key]
            else:
                new_name[key] = expo

        return new_name

    @staticmethod
    def div_names(name1, name2):
        """Divide two unit names.

        Parameters:
            name1 (str, dict, or None): The numerator unit name.
            name2 (str, dict, or None): The denominator unit name.

        Returns:
            str or dict or None: The quotient of the two unit names, or None if
                both arguments are None.
        """

        if name1 is None or name2 is None:
            return None

        name1 = Units.name_to_dict(name1)
        name2 = Units.name_to_dict(name2)

        new_name = name1.copy()
        for (key,expo) in name2.items():
            if key in new_name:
                expo -= new_name[key]

            if expo == 0:
                del new_name[key]
            else:
                new_name[key] = -expo

        return new_name

    @staticmethod
    def name_power(name, power):
        """Raise a unit name to the specified power.

        Parameters:
            name (str, dict, or None): The unit name to raise to a power.
            power (int or float): The exponent.

        Returns:
            str or dict or None: The unit name raised to the specified power,
                or None if name is None.
        """

        if name is None:
            return None

        name = Units.name_to_dict(name)

        if isinstance(power, str):
            old_power = power
            power = Units.name_to_dict(power)

            if not isinstance(power, int):
                raise ValueError("non-integer power on unit '%s'", old_power)

        new_name = {}

        for (key,expo) in name.items():
            new_power = expo * power
            int_power = int(new_power)
            if new_power != int_power:
                raise ValueError("non-integer power %f on unit '%s'" %
                                 (new_power, key))

            new_name[key] = int_power

        return new_name

    @staticmethod
    def name_to_dict(name):
        """Convert a unit name string to a dictionary.

        Parameters:
            name (str or dict): The unit name to convert.

        Returns:
            dict: A dictionary representation of the unit name.

        Raises:
            ValueError: If the name format is invalid.
        """

        BIGNUM = 99999

        if isinstance(name, dict):
            return name

        if not isinstance(name, str):
            raise ValueError("unit is not a string: '%s'" % str(name))

        name = name.strip()
        if name == '':
            return {}

        # Return a named unit
        if name.isalpha():
            return {name: 1}

        # Return an integer exponent
        try:
            return int(name)
        except ValueError:
            pass

        # If the name starts with a left parenthensis, find the end of the
        # expression and process the interior
        if name[0] == '(':
            depth = 0
            for (i,c) in enumerate(name):
                if c == '(':
                    depth += 1
                if c == ')':
                    depth -= 1
                if depth == 0:
                    break

            left = name[1:i]
            right = name[i+1:].lstrip()

        # Otherwise, jump to the first operator
        else:
            imul = name.find('*') % BIGNUM
            idiv = name.find('/') % BIGNUM
            first = min(imul, idiv)
            if first >= BIGNUM - 1:
                raise ValueError("illegal unit syntax: '%s'" % name)

            left = name[:first]
            right = name[first:].lstrip()

        # Handle the operator if it is an exponent
        if right.startswith('**'):
            right = right[2:].lstrip()

            imul = right.find('*') % BIGNUM
            idiv = right.find('/') % BIGNUM
            first = min(imul, idiv)
            if first >= BIGNUM - 1:
                return Units.name_power(left, right)

            power = right[:first].lstrip()
            left = Units.name_power(left, power)
            right = right[first:].lstrip()

        if right == '':
            if left == name.strip():    # if no progress was made...
                raise ValueError("illegal unit syntax: '%s'" % name)

            return Units.name_to_dict(left)

        if right.startswith('**'):
            raise ValueError("illegal unit syntax: '%s'" % name)

        op = right[0]
        right = right[1:].lstrip()
        if op == '*':
            return Units.mul_names(left, right)
        else:
            return Units.div_names(left, right)

    @staticmethod
    def name_to_str(namedict):
        """Convert a unit name dictionary to a string.

        Parameters:
            namedict (dict or None): The unit name dictionary to convert.

        Returns:
            str: A string representation of the unit name, or empty string if
                namedict is None.

        Note:
            This method contains nested helper functions for ordering keys and
            concatenating units.
        """

        def order_keys(namelist):
            """Internal method to order the units sensibly."""

            sorted = []

            # Coefficient first
            if '' in namelist:
                sorted.append('')

            # Distances first
            templist = []
            for key in namelist:
                if key in Units.NAME_TO_UNIT:
                    expo = Units.NAME_TO_UNIT[key].exponents
                    if expo[0]:
                        templist.append(key)
            templist.sort()
            sorted += templist

            # Angles second
            templist = []
            for key in namelist:
                if key in Units.NAME_TO_UNIT:
                    expo = Units.NAME_TO_UNIT[key].exponents
                    if expo[2] and key not in sorted:
                        templist.append(key)
            templist.sort()
            sorted += templist

            # Time units next
            templist = []
            for key in namelist:
                if key in Units.NAME_TO_UNIT:
                    expo = Units.NAME_TO_UNIT[key].exponents
                    if expo[1] and key not in sorted:
                        templist.append(key)
            templist.sort()
            sorted += templist

            # Unrecognized units last
            templist = []
            for key in namelist:
                if key not in sorted:
                    templist.append(key)
            templist.sort()
            sorted += templist

            return sorted

        def cat_units(namelist, negate=False):
            """A string of names and exponents."""

            unitlist = []
            for key in namelist:
                expo = namedict[key]
                if key == '':
                    if expo != 1:
                        unitlist.append(str(expo))
                    continue

                if negate:
                    expo = -expo
                if expo == 1:
                    unitlist.append(key)
                elif expo > 1:
                    unitlist.append(key + '**' + str(expo))
                else:
                    unitlist.append(key + '**(' + str(expo) + ')')

            return '*'.join(unitlist)

        # Return a string immediately
        if isinstance(namedict, str):
            return namedict

        # Make list of numerator and denominator units
        numers = []
        denoms = []
        for (key,expo) in namedict.items():
            if key == '':
                numers.append(key)
            elif expo > 0:
                numers.append(key)
            elif expo < 0:
                denoms.append(key)

        # Sort the units
        numers = order_keys(numers)
        denoms = order_keys(denoms)

        if numers:
            if denoms:
                return cat_units(numers) + '/' + cat_units(denoms, negate=True)
            else:
                return cat_units(numers)
        else:
            if denoms:
                return cat_units(denoms, negate=False)
            else:
                return ''

    def create_name(self):
        """Create a name for this Units object based on its exponents.

        Returns:
            str: A name for this Units object.
        """

        # Return the internal name, if defined
        if self.name is not None:
            return self.name

        # Return the name from the dictionary, if found
        try:
            name = Units.TUPLES_TO_UNIT[(self.exponents, self.triple)].name
            if name is not None:
                return name
        except KeyError:
            pass

        expo = self.exponents

        # Search for combinations that might work
        options = [[], [], []]
        for i in range(3):
            target_power = self.exponents[i]
            if target_power:
                for unit in Units.UNITS_BY_EXPO[i]:
                    actual_power = unit.exponents[i]
                    p = target_power // actual_power
                    if p * actual_power == target_power:
                        if p > 0:
                            new_triple = (unit.triple[0]**p,
                                          unit.triple[1]**p,
                                          unit.triple[2] * p)
                        else:
                            new_triple = (unit.triple[1]**(-p), # swapped!
                                          unit.triple[0]**(-p),
                                          unit.triple[2] * p)

                        options[i].append((unit, p, new_triple))
            else:
                options[i].append((Units.UNITS_BY_EXPO[i][0], 0, (1,1,0)))

        # Check every possible combination for the one that yields the correct
        # coefficient
        successes = []
        for (d, d_option) in enumerate(options[0]):
            (d_unit, d_power, d_triple) = d_option
            (d_numer, d_denom, d_expo) = d_triple

            for (t, t_option) in enumerate(options[1]):
                (t_unit, t_power, t_triple) = t_option
                (t_numer, t_denom, t_expo) = t_triple

                for (a, a_option) in enumerate(options[2]):
                    (a_unit, a_power, a_triple) = a_option
                    (a_numer, a_denom, a_expo) = a_triple

                    numer = d_numer * t_numer * a_numer
                    denom = d_denom * t_denom * a_denom
                    expo  = d_expo  + t_expo  + a_expo

                    gcd_value = _gcd(numer, denom)
                    numer //= gcd_value
                    denom //= gcd_value

                    if (numer, denom, expo) == self.triple:
                        successes.append({d_unit.name: d_power,
                                          t_unit.name: t_power,
                                          a_unit.name: a_power})

        # Return the success with the fewest keys
        if successes:
            lengths = [len(k) for k in successes]
            best = min(lengths)
            for (k,length) in enumerate(lengths):
                if length == best:
                    return successes[k]

        # Failing that, use standard units and define the coefficient too
        (numer, denom, pi_expo) = self.triple
        if denom == 1 and pi_expo == 0:
            coefft = numer
        else:
            coefft = numer / denom * np.pi**pi_expo

        new_dict = {   '': coefft,
                     'km': self.exponents[0],
                      's': self.exponents[1],
                    'rad': self.exponents[2]}

        return new_dict

    def get_name(self):
        """Get the name of this Units object.

        Returns:
            str or dict or None: The name of this Units object.
        """

        name = self.name or self.create_name()
        return Units.name_to_str(name)

    def set_name(self, name):
        """Set the name of this Units object.

        Parameters:
            name (str or dict): The new name for this Units object.
        """

        self.name = name

        return self

################################################################################
# Define the most common units and their names
################################################################################

Units.UNITLESS      = Units((0,0,0), (1, 1, 0), "")

Units.KM            = Units((1,0,0), (1,          1, 0), "km")
Units.KILOMETER     = Units((1,0,0), (1,          1, 0), "kilometer")
Units.KILOMETERS    = Units((1,0,0), (1,          1, 0), "kilometers")
Units.M             = Units((1,0,0), (1,       1000, 0), "m")
Units.METER         = Units((1,0,0), (1,       1000, 0), "meter")
Units.METERS        = Units((1,0,0), (1,       1000, 0), "meters")
Units.CM            = Units((1,0,0), (1,     100000, 0), "cm")
Units.CENTIMETER    = Units((1,0,0), (1,     100000, 0), "centimeter")
Units.CENTIMETERS   = Units((1,0,0), (1,     100000, 0), "centimeters")
Units.MM            = Units((1,0,0), (1,    1000000, 0), "mm")
Units.MILLIMETER    = Units((1,0,0), (1,    1000000, 0), "millimeter")
Units.MILLIMETERS   = Units((1,0,0), (1,    1000000, 0), "millimeters")
Units.MICRON        = Units((1,0,0), (1, 1000000000, 0), "micron")
Units.MICRONS       = Units((1,0,0), (1, 1000000000, 0), "microns")

Units.S             = Units((0,1,0), (    1,    1, 0), "s")
Units.SEC           = Units((0,1,0), (    1,    1, 0), "sec")
Units.SECOND        = Units((0,1,0), (    1,    1, 0), "second ")
Units.SECONDS       = Units((0,1,0), (    1,    1, 0), "seconds")
Units.MIN           = Units((0,1,0), (   60,    1, 0), "min")
Units.MINUTE        = Units((0,1,0), (   60,    1, 0), "minute")
Units.MINUTES       = Units((0,1,0), (   60,    1, 0), "minutes")
Units.H             = Units((0,1,0), ( 3600,    1, 0), "h")
Units.HOUR          = Units((0,1,0), ( 3600,    1, 0), "hour")
Units.HOURS         = Units((0,1,0), ( 3600,    1, 0), "hours")
Units.D             = Units((0,1,0), (86400,    1, 0), "d")
Units.DAY           = Units((0,1,0), (86400,    1, 0), "day")
Units.DAYS          = Units((0,1,0), (86400,    1, 0), "days")
Units.MS            = Units((0,1,0), (    1, 1000, 0), "ms")
Units.MSEC          = Units((0,1,0), (    1, 1000, 0), "msec")

Units.RAD           = Units((0,0,1), (1,        1, 0), "rad")
Units.RADIAN        = Units((0,0,1), (1,        1, 0), "radian")
Units.RADIANS       = Units((0,0,1), (1,        1, 0), "radians")
Units.MRAD          = Units((0,0,1), (1,     1000, 0), "mrad")
Units.MILLIRAD      = Units((0,0,1), (1,     1000, 0), "millirad")
Units.DEG           = Units((0,0,1), (1,      180, 1), "deg")
Units.DEGREE        = Units((0,0,1), (1,      180, 1), "degree")
Units.DEGREES       = Units((0,0,1), (1,      180, 1), "degrees")
Units.ARCHOUR       = Units((0,0,1), (1,       12, 1), "archour")
Units.ARCHOURS      = Units((0,0,1), (1,       12, 1), "archours")
Units.ARCMIN        = Units((0,0,1), (1,   180*60, 1), "arcmin")
Units.ARCMINUTE     = Units((0,0,1), (1,   180*60, 1), "arcminute")
Units.ARCMINUTES    = Units((0,0,1), (1,   180*60, 1), "arcminutes")
Units.ARCSEC        = Units((0,0,1), (1, 180*3600, 1), "arcsec")
Units.ARCSECOND     = Units((0,0,1), (1, 180*3600, 1), "arcsecond")
Units.ARCSECONDS    = Units((0,0,1), (1, 180*3600, 1), "arcseconds")
Units.REV           = Units((0,0,1), (2,        1, 1), "rev")
Units.REVS          = Units((0,0,1), (2,        1, 1), "revs")
Units.ROTATION      = Units((0,0,1), (2,        1, 1), "rotation")
Units.ROTATIONS     = Units((0,0,1), (2,        1, 1), "rotations")
Units.CYCLE         = Units((0,0,1), (2,        1, 1), "cycle")
Units.CYCLES        = Units((0,0,1), (2,        1, 1), "cycles")

Units.STER          = Units((0,0,2), (1,        1, 0), "ster")

# Create dictionaries to convert between name and units
Units.NAME_TO_UNIT = {}
Units.TUPLES_TO_UNIT = {}

# Assemble a list of all the recognized units
Units.DISTANCE_LIST = [ Units.KM, Units.M, Units.CM, Units.MM, Units.MICRON]
Units.TIME_LIST  = [Units.S, Units.D, Units.H, Units.MIN, Units.MSEC]
Units.ANGLE_LIST = [Units.RAD, Units.MRAD, Units.DEG, Units.ARCSEC,
                    Units.ARCMIN, Units.ARCHOUR, Units.CYCLES, Units.STER]

Units.UNITS_BY_EXPO = [Units.DISTANCE_LIST,     # index = 0
                       Units.TIME_LIST,         # index = 1
                       Units.ANGLE_LIST]        # index = 2

Units.STANDARD_LIST = [Units.UNITLESS] + \
                       Units.DISTANCE_LIST + \
                       Units.TIME_LIST + \
                       Units.ANGLE_LIST

# Fill in the dictionaries
for units in Units.STANDARD_LIST:
    Units.NAME_TO_UNIT[units.name] = units
    Units.TUPLES_TO_UNIT[(units.exponents, units.triple)] = units

################################################################################
