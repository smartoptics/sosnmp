#
# This file is part of pysnmp software.
#
# Copyright (c) 2005-2020, Ilya Etingof <etingof@gmail.com>
# License: https://www.pysnmp.com/pysnmp/license.html
#
# Copyright (C) 2014, Zebra Technologies
# Authors: Matt Hooks <me@matthooks.com>
#          Zachary Lorusso <zlorusso@gmail.com>
#
import asyncio
import sys

from pysnmp.entity.rfc3413 import ntforg
from pysnmp.hlapi.asyncio.auth import CommunityData, UsmUserData
from pysnmp.hlapi.asyncio.context import ContextData
from pysnmp.hlapi.asyncio.lcd import NotificationOriginatorLcdConfigurator
from pysnmp.hlapi.asyncio.transport import Udp6TransportTarget, UdpTransportTarget
from pysnmp.hlapi.asyncio.varbinds import NotificationOriginatorVarBinds
from pysnmp.smi.rfc1902 import NotificationType, ObjectIdentity

__all__ = ["sendNotification"]

VB_PROCESSOR = NotificationOriginatorVarBinds()
LCD = NotificationOriginatorLcdConfigurator()


async def sendNotification(
    snmpEngine, authData, transportTarget, contextData, notifyType, varBinds, **options
):
    r"""Creates a generator to send SNMP notification.

    When iterator gets advanced by :py:mod:`asyncio` main loop,
    SNMP TRAP or INFORM notification is send (:RFC:`1905#section-4.2.6`).
    The iterator yields :py:class:`asyncio.get_running_loop().create_future()` which gets done whenever
    response arrives or error occurs.

    Parameters
    ----------
    snmpEngine : :py:class:`~pysnmp.hlapi.asyncio.SnmpEngine`
        Class instance representing SNMP engine.

    authData : :py:class:`~pysnmp.hlapi.asyncio.CommunityData` or :py:class:`~pysnmp.hlapi.asyncio.UsmUserData`
        Class instance representing SNMP credentials.

    transportTarget : :py:class:`~pysnmp.hlapi.asyncio.UdpTransportTarget` or :py:class:`~pysnmp.hlapi.asyncio.Udp6TransportTarget`
        Class instance representing transport type along with SNMP peer address.

    contextData : :py:class:`~pysnmp.hlapi.asyncio.ContextData`
        Class instance representing SNMP ContextEngineId and ContextName values.

    notifyType : str
        Indicates type of notification to be sent. Recognized literal
        values are *trap* or *inform*.

    varBinds: tuple
        Single :py:class:`~pysnmp.smi.rfc1902.NotificationType` class instance
        representing a minimum sequence of MIB variables required for
        particular notification type.
        Alternatively, a sequence of :py:class:`~pysnmp.smi.rfc1902.ObjectType`
        objects could be passed instead. In the latter case it is up to
        the user to ensure proper Notification PDU contents.

    Other Parameters
    ----------------
    \*\*options :
        Request options:

            * `lookupMib` - load MIB and resolve response MIB variables at
              the cost of slightly reduced performance. Default is `True`.

    Yields
    ------
    errorIndication : :py:class:`~pysnmp.proto.errind.ErrorIndication`
        True value indicates SNMP engine error.
    errorStatus : str
        True value indicates SNMP PDU error.
    errorIndex : int
        Non-zero value refers to `varBinds[errorIndex-1]`
    varBinds : tuple
        A sequence of :py:class:`~pysnmp.smi.rfc1902.ObjectType` class
        instances representing MIB variables returned in SNMP response.

    Raises
    ------
    PySnmpError
        Or its derivative indicating that an error occurred while
        performing SNMP operation.

    Examples
    --------
    >>> import asyncio
    >>> from pysnmp.hlapi.asyncio import *
    >>>
    >>> async def run():
    ...     errorIndication, errorStatus, errorIndex, varBinds = await sendNotification(
    ...         SnmpEngine(),
    ...         CommunityData('public'),
    ...         UdpTransportTarget(('demo.pysnmp.com', 162)),
    ...         ContextData(),
    ...         'trap',
    ...         NotificationType(ObjectIdentity('IF-MIB', 'linkDown')))
    ...     print(errorIndication, errorStatus, errorIndex, varBinds)
    ...
    >>> asyncio.run(run())
    (None, 0, 0, [])
    >>>

    """

    def __cbFun(
        snmpEngine,
        sendRequestHandle,
        errorIndication,
        errorStatus,
        errorIndex,
        varBinds,
        cbCtx,
    ):
        lookupMib, future = cbCtx
        if future.cancelled():
            return
        try:
            varBindsUnmade = VB_PROCESSOR.unmakeVarBinds(
                snmpEngine, varBinds, lookupMib
            )
        except Exception:
            ex = sys.exc_info()[1]
            future.set_exception(ex)
        else:
            future.set_result(
                (errorIndication, errorStatus, errorIndex, varBindsUnmade)
            )

    notifyName = LCD.configure(
        snmpEngine, authData, transportTarget, notifyType, contextData.contextName
    )

    future = asyncio.get_running_loop().create_future()

    ntforg.NotificationOriginator().sendVarBinds(
        snmpEngine,
        notifyName,
        contextData.contextEngineId,
        contextData.contextName,
        VB_PROCESSOR.makeVarBinds(snmpEngine, varBinds),
        __cbFun,
        (options.get("lookupMib", True), future),
    )

    if notifyType == "trap":

        def __trapFun(future):
            if future.cancelled():
                return
            future.set_result((None, 0, 0, []))

        loop = asyncio.get_event_loop()
        loop.call_soon(__trapFun, future)

    return await future
