################################################################################
# polymath/__init__.py
################################################################################

from polymath.boolean    import Boolean
from polymath.matrix     import Matrix
from polymath.matrix3    import Matrix3
from polymath.pair       import Pair
from polymath.polynomial import Polynomial
from polymath.quaternion import Quaternion
from polymath.qube       import Qube
from polymath.scalar     import Scalar
from polymath.units      import Units
from polymath.vector     import Vector
from polymath.vector3    import Vector3

import polymath.extensions

try:
    from ._version import __version__
except ImportError as err:
    __version__ = 'Version unspecified'

__all__ = [
    'Boolean',
    'Matrix',
    'Matrix3',
    'Pair',
    'Polynomial',
    'Quaternion',
    'Qube',
    'Scalar',
    'Units',
    'Vector',
    'Vector3',
]

################################################################################
