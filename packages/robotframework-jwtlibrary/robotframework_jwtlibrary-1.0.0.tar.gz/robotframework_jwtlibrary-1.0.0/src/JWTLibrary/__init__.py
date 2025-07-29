"""
JWT Library for Robot Framework

This library provides keywords for JSON Web Token (JWT) operations in Robot Framework tests.

Author: JWT Robot Framework Library
Version: 1.0.0
License: Apache 2.0
"""

from .jwt_library import JWTLibrary
from .version import __version__

__all__ = ["JWTLibrary", "__version__"]

# Make the library class available at package level
JWTLibrary = JWTLibrary
