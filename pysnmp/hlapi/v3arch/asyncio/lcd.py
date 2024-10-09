#
# This file is part of pysnmp software.
#
# Copyright (c) 2005-2020, Ilya Etingof <etingof@gmail.com>
# License: https://www.pysnmp.com/pysnmp/license.html
#
from pysnmp import error, nextid
from pysnmp.entity import config
from pysnmp.entity.engine import SnmpEngine
from pysnmp.hlapi.v3arch.asyncio.auth import CommunityData, UsmUserData
from pysnmp.hlapi.v3arch.asyncio.transport import AbstractTransportTarget

__all__ = ["CommandGeneratorLcdConfigurator", "NotificationOriginatorLcdConfigurator"]


class AbstractLcdConfigurator:
    nextID = nextid.Integer(0xFFFFFFFF)
    cacheKeys = []

    def _getCache(self, snmpEngine):
        cacheId = self.__class__.__name__
        cache = snmpEngine.getUserContext(cacheId)
        if cache is None:
            cache = {x: {} for x in self.cacheKeys}
            snmpEngine.setUserContext(**{cacheId: cache})
        return cache

    def configure(self, snmpEngine, *args, **kwargs):
        pass

    def unconfigure(self, snmpEngine, *args, **kwargs):
        pass


class CommandGeneratorLcdConfigurator(AbstractLcdConfigurator):
    """Local configuration data (LCD) for Command Generator."""

    cacheKeys = ["auth", "parm", "tran", "addr"]

    def configure(
        self, snmpEngine, authData, transportTarget, contextName=b"", **options
    ):
        """Configure command generator targets on the SNMP engine."""
        cache = self._getCache(snmpEngine)
        if isinstance(authData, CommunityData):
            if authData.communityIndex not in cache["auth"]:
                config.addV1System(
                    snmpEngine,
                    authData.communityIndex,
                    authData.communityName,
                    authData.contextEngineId,
                    authData.contextName,
                    authData.tag,
                    authData.securityName,
                )
                cache["auth"][authData.communityIndex] = authData
        elif isinstance(authData, UsmUserData):
            authDataKey = authData.userName, authData.securityEngineId
            if authDataKey not in cache["auth"]:
                add_user = True

            elif self._usm_auth_changed(cache["auth"][authDataKey], authData):
                config.delV3User(
                    snmpEngine, authData.userName, authData.securityEngineId
                )
                add_user = True

            else:
                add_user = False

            if add_user:
                config.addV3User(
                    snmpEngine,
                    authData.userName,
                    authData.authProtocol,
                    authData.authKey,
                    authData.privProtocol,
                    authData.privKey,
                    securityEngineId=authData.securityEngineId,
                    securityName=authData.securityName,
                    authKeyType=authData.authKeyType,
                    privKeyType=authData.privKeyType,
                )
                cache["auth"][authDataKey] = authData
        else:
            raise error.PySnmpError("Unsupported authentication object")

        paramsKey = (authData.securityName, authData.securityLevel, authData.mpModel)
        if paramsKey in cache["parm"]:
            paramsName, useCount = cache["parm"][paramsKey]
            cache["parm"][paramsKey] = paramsName, useCount + 1
        else:
            paramsName = "p%s" % self.nextID()
            config.addTargetParams(
                snmpEngine,
                paramsName,
                authData.securityName,
                authData.securityLevel,
                authData.mpModel,
            )
            cache["parm"][paramsKey] = paramsName, 1

        if transportTarget.TRANSPORT_DOMAIN in cache["tran"]:
            transport, useCount = cache["tran"][transportTarget.TRANSPORT_DOMAIN]
            transportTarget.verifyDispatcherCompatibility(snmpEngine)
            cache["tran"][transportTarget.TRANSPORT_DOMAIN] = transport, useCount + 1
        elif config.getTransport(snmpEngine, transportTarget.TRANSPORT_DOMAIN):
            transportTarget.verifyDispatcherCompatibility(snmpEngine)
        else:
            transport = transportTarget.openClientMode()
            config.addTransport(snmpEngine, transportTarget.TRANSPORT_DOMAIN, transport)
            cache["tran"][transportTarget.TRANSPORT_DOMAIN] = transport, 1

        transportKey = (
            paramsName,
            transportTarget.TRANSPORT_DOMAIN,
            transportTarget.transportAddr,
            transportTarget.timeout,
            transportTarget.retries,
            transportTarget.tagList,
            transportTarget.iface,
        )

        if transportKey in cache["addr"]:
            addrName, useCount = cache["addr"][transportKey]
            cache["addr"][transportKey] = addrName, useCount + 1
        else:
            addrName = "a%s" % self.nextID()
            config.addTargetAddr(
                snmpEngine,
                addrName,
                transportTarget.TRANSPORT_DOMAIN,
                transportTarget.transportAddr,
                paramsName,
                transportTarget.timeout * 100,
                transportTarget.retries,
                transportTarget.tagList,
            )
            cache["addr"][transportKey] = addrName, 1

        return addrName, paramsName

    def unconfigure(self, snmpEngine, authData=None, contextName=b"", **options):
        """Remove command generator targets from the SNMP engine."""
        cache = self._getCache(snmpEngine)
        if authData:
            if isinstance(authData, CommunityData):
                authDataKey = authData.communityIndex
            elif isinstance(authData, UsmUserData):
                authDataKey = authData.userName, authData.securityEngineId
            else:
                raise error.PySnmpError("Unsupported authentication object")
            if authDataKey in cache["auth"]:
                authDataKeys = (authDataKey,)
            else:
                raise error.PySnmpError(f"Unknown authData {authData}")
        else:
            authDataKeys = list(cache["auth"].keys())

        addrNames, paramsNames = set(), set()

        for authDataKey in authDataKeys:
            authDataX = cache["auth"][authDataKey]
            del cache["auth"][authDataKey]
            if isinstance(authDataX, CommunityData):
                config.delV1System(snmpEngine, authDataX.communityIndex)
            elif isinstance(authDataX, UsmUserData):
                config.delV3User(
                    snmpEngine, authDataX.userName, authDataX.securityEngineId
                )
            else:
                raise error.PySnmpError("Unsupported authentication object")

            paramsKey = (
                authDataX.securityName,
                authDataX.securityLevel,
                authDataX.mpModel,
            )
            if paramsKey in cache["parm"]:
                paramsName, useCount = cache["parm"][paramsKey]
                useCount -= 1
                if useCount:
                    cache["parm"][paramsKey] = paramsName, useCount
                else:
                    del cache["parm"][paramsKey]
                    config.delTargetParams(snmpEngine, paramsName)
                    paramsNames.add(paramsName)
            else:
                raise error.PySnmpError(f"Unknown target {paramsKey}")

            addrKeys = [x for x in cache["addr"] if x[0] == paramsName]

            for addrKey in addrKeys:
                addrName, useCount = cache["addr"][addrKey]
                useCount -= 1
                if useCount:
                    cache["addr"][addrKey] = addrName, useCount
                else:
                    config.delTargetAddr(snmpEngine, addrName)
                    del cache["addr"][addrKey]
                    addrNames.add(addrKey)

                    if addrKey[1] in cache["tran"]:
                        transport, useCount = cache["tran"][addrKey[1]]
                        if useCount > 1:
                            useCount -= 1
                            cache["tran"][addrKey[1]] = transport, useCount
                        else:
                            config.delTransport(snmpEngine, addrKey[1])
                            transport.closeTransport()
                            del cache["tran"][addrKey[1]]

        return addrNames, paramsNames

    @staticmethod
    def _usm_auth_changed(cachedAuthData, newAuthData):
        changed = False

        changed |= cachedAuthData.authKey != newAuthData.authKey
        changed |= cachedAuthData.authProtocol != newAuthData.authProtocol
        changed |= cachedAuthData.privKey != newAuthData.privKey
        changed |= cachedAuthData.privProtocol != newAuthData.privProtocol

        return changed


class NotificationOriginatorLcdConfigurator(AbstractLcdConfigurator):
    """Local configuration data (LCD) for Notification Originator."""

    cacheKeys = ["auth", "name"]
    _cmdGenLcdCfg = CommandGeneratorLcdConfigurator()

    def configure(
        self,
        snmpEngine: SnmpEngine,
        authData: "CommunityData | UsmUserData",
        transportTarget: AbstractTransportTarget,
        notifyType: str,
        contextName=None,
        **options,
    ):
        """Configure notification targets on the SNMP engine."""
        cache = self._getCache(snmpEngine)
        notifyName = None

        # Create matching transport tags if not given by user. Not good!
        if not transportTarget.tagList:
            transportTarget.tagList = str(
                hash((authData.securityName, transportTarget.transportAddr))
            )
        if isinstance(authData, CommunityData) and not authData.tag:
            authData.tag = transportTarget.tagList.split()[0]

        addrName, paramsName = self._cmdGenLcdCfg.configure(
            snmpEngine, authData, transportTarget, contextName, **options
        )
        tagList = transportTarget.tagList.split()
        if not tagList:
            tagList = [""]
        for tag in tagList:
            notifyNameKey = paramsName, tag, notifyType
            if notifyNameKey in cache["name"]:
                notifyName, paramsName, useCount = cache["name"][notifyNameKey]
                cache["name"][notifyNameKey] = notifyName, paramsName, useCount + 1
            else:
                notifyName = "n%s" % self.nextID()
                config.addNotificationTarget(
                    snmpEngine, notifyName, paramsName, tag, notifyType
                )
                cache["name"][notifyNameKey] = notifyName, paramsName, 1
        authDataKey = (
            authData.securityName,
            authData.securityModel,
            authData.securityLevel,
            contextName,
        )
        if authDataKey in cache["auth"]:
            authDataX, subTree, useCount = cache["auth"][authDataKey]
            cache["auth"][authDataKey] = authDataX, subTree, useCount + 1
        else:
            subTree = (1, 3, 6)
            config.addVacmUser(
                snmpEngine,
                authData.securityModel,
                authData.securityName,
                authData.securityLevel,
                (),
                (),
                subTree,
                contextName=contextName,
            )
            cache["auth"][authDataKey] = authData, subTree, 1

        return notifyName

    def unconfigure(self, snmpEngine, authData=None, contextName=b"", **options):
        """Remove notification targets from the SNMP engine."""
        cache = self._getCache(snmpEngine)
        if authData:
            authDataKey = (
                authData.securityName,
                authData.securityModel,
                authData.securityLevel,
                contextName,
            )
            if authDataKey in cache["auth"]:
                authDataKeys = (authDataKey,)
            else:
                raise error.PySnmpError(f"Unknown authData {authData}")
        else:
            authDataKeys = tuple(cache["auth"])

        addrNames, paramsNames = self._cmdGenLcdCfg.unconfigure(
            snmpEngine, authData, contextName, **options
        )

        notifyAndParamsNames = [
            (cache["name"][x], x) for x in cache["name"].keys() if x[0] in paramsNames
        ]

        for (notifyName, paramsName, useCount), notifyNameKey in notifyAndParamsNames:
            useCount -= 1
            if useCount:
                cache["name"][notifyNameKey] = notifyName, paramsName, useCount
            else:
                config.delNotificationTarget(snmpEngine, notifyName, paramsName)
                del cache["name"][notifyNameKey]

        for authDataKey in authDataKeys:
            authDataX, subTree, useCount = cache["auth"][authDataKey]
            useCount -= 1
            if useCount:
                cache["auth"][authDataKey] = authDataX, subTree, useCount
            else:
                config.delTrapUser(
                    snmpEngine,
                    authDataX.securityModel,
                    authDataX.securityName,
                    authDataX.securityLevel,
                    subTree,
                )
                del cache["auth"][authDataKey]
