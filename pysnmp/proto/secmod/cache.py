#
# This file is part of pysnmp software.
#
# Copyright (c) 2005-2020, Ilya Etingof <etingof@gmail.com>
# License: https://www.pysnmp.com/pysnmp/license.html
#
from typing import Any, Dict


from pysnmp import nextid
from pysnmp.proto import error


class Cache:
    """SNMP securityData cache."""

    __stateReference = nextid.Integer(0xFFFFFF)
    __cacheEntries: Dict[int, Any]

    def __init__(self):
        """Create a cache object."""
        self.__cacheEntries = {}

    def push(self, **securityData):
        """Push securityData into cache."""
        stateReference = self.__stateReference()
        self.__cacheEntries[stateReference] = securityData
        return stateReference

    def pop(self, stateReference):
        """Pop securityData from cache."""
        if stateReference in self.__cacheEntries:
            securityData = self.__cacheEntries[stateReference]
        else:
            raise error.ProtocolError(
                f"Cache miss for stateReference={stateReference} at {self}"
            )
        del self.__cacheEntries[stateReference]
        return securityData

    def isEmpty(self):
        """Return True if cache is empty."""
        return not bool(self.__cacheEntries)
