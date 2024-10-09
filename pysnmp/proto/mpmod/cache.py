#
# This file is part of pysnmp software.
#
# Copyright (c) 2005-2020, Ilya Etingof <etingof@gmail.com>
# License: https://www.pysnmp.com/pysnmp/license.html
#
from pysnmp import nextid
from pysnmp.proto import error


class Cache:
    """SNMP message cache."""

    __stateReference = nextid.Integer(0xFFFFFF)
    __msgID = nextid.Integer(0xFFFFFF)

    def __init__(self):
        """Create a cache object."""
        self.__msgIdIndex = {}
        self.__stateReferenceIndex = {}
        self.__sendPduHandleIdx = {}
        # Message expiration mechanics
        self.__expirationQueue = {}
        self.__expirationTimer = 0

    # Server mode cache handling

    def newStateReference(self):
        """Generate a new state reference."""
        return self.__stateReference()

    def pushByStateRef(self, stateReference, **msgInfo):
        """Push state information."""
        if stateReference in self.__stateReferenceIndex:
            raise error.ProtocolError(
                f"Cache dup for stateReference={stateReference} at {self}"
            )
        expireAt = self.__expirationTimer + 600
        self.__stateReferenceIndex[stateReference] = msgInfo, expireAt

        # Schedule to expire
        if expireAt not in self.__expirationQueue:
            self.__expirationQueue[expireAt] = {}
        if "stateReference" not in self.__expirationQueue[expireAt]:
            self.__expirationQueue[expireAt]["stateReference"] = {}
        self.__expirationQueue[expireAt]["stateReference"][stateReference] = 1

    def popByStateRef(self, stateReference):
        """Release state information."""
        if stateReference in self.__stateReferenceIndex:
            cacheInfo = self.__stateReferenceIndex[stateReference]
        else:
            raise error.ProtocolError(
                f"Cache miss for stateReference={stateReference} at {self}"
            )
        del self.__stateReferenceIndex[stateReference]
        cacheEntry, expireAt = cacheInfo
        del self.__expirationQueue[expireAt]["stateReference"][stateReference]
        return cacheEntry

    # Client mode cache handling

    def newMsgID(self):
        """Generate a new message ID."""
        return self.__msgID()

    def pushByMsgId(self, msgId, **msgInfo):
        """Cache state information."""
        if msgId in self.__msgIdIndex:
            raise error.ProtocolError(f"Cache dup for msgId={msgId} at {self}")
        expireAt = self.__expirationTimer + 600
        self.__msgIdIndex[msgId] = msgInfo, expireAt

        self.__sendPduHandleIdx[msgInfo["sendPduHandle"]] = msgId

        # Schedule to expire
        if expireAt not in self.__expirationQueue:
            self.__expirationQueue[expireAt] = {}
        if "msgId" not in self.__expirationQueue[expireAt]:
            self.__expirationQueue[expireAt]["msgId"] = {}
        self.__expirationQueue[expireAt]["msgId"][msgId] = 1

    def popByMsgId(self, msgId):
        """Release state information."""
        if msgId in self.__msgIdIndex:
            cacheInfo = self.__msgIdIndex[msgId]
        else:
            raise error.ProtocolError(f"Cache miss for msgId={msgId} at {self}")
        msgInfo, expireAt = cacheInfo
        del self.__sendPduHandleIdx[msgInfo["sendPduHandle"]]
        del self.__msgIdIndex[msgId]
        cacheEntry, expireAt = cacheInfo
        del self.__expirationQueue[expireAt]["msgId"][msgId]
        return cacheEntry

    def popBySendPduHandle(self, sendPduHandle):
        """Release state information."""
        if sendPduHandle in self.__sendPduHandleIdx:
            self.popByMsgId(self.__sendPduHandleIdx[sendPduHandle])

    def expireCaches(self):
        """Expire pending messages."""
        # Uses internal clock to expire pending messages
        if self.__expirationTimer in self.__expirationQueue:
            cacheInfo = self.__expirationQueue[self.__expirationTimer]
            if "stateReference" in cacheInfo:
                for stateReference in cacheInfo["stateReference"]:
                    del self.__stateReferenceIndex[stateReference]
            if "msgId" in cacheInfo:
                for msgId in cacheInfo["msgId"]:
                    del self.__msgIdIndex[msgId]
            del self.__expirationQueue[self.__expirationTimer]
        self.__expirationTimer += 1
