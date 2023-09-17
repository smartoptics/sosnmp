"""
SNMPv1
++++++

Send SNMP GET request using the following options:

  * with SNMPv1, community 'public'
  * over IPv4/UDP
  * to an Agent at demo.pysnmp.com:161
  * for an instance of SNMPv2-MIB::sysDescr.0 MIB object
  * Based on asyncio I/O framework

Functionally similar to:

| $ snmpgetnext -v1 -c public demo.pysnmp.com SNMPv2-MIB::sysDescr.0

"""#
import asyncio
import pytest
from pysnmp.hlapi.asyncio.slim import Slim
from pysnmp.smi.rfc1902 import ObjectIdentity, ObjectType

@pytest.mark.asyncio
async def test_v1_next():
    slim = Slim(1)
    errorIndication, errorStatus, errorIndex, varBinds = await slim.next(
        'public',
        'demo.pysnmp.com',
        161,
        ObjectType(ObjectIdentity("SNMPv2-MIB", "sysDescr", 0)),
    )

    assert errorIndication is None
    assert errorStatus == 0
    assert errorIndex == 0
    assert len(varBinds) > 0

    slim.close()