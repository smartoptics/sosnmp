from pysnmp.entity.engine import SnmpEngine
from pysnmp.hlapi.asyncio.sync.cmdgen import walkCmd
from pysnmp.hlapi.asyncio.transport import UdpTransportTarget
from pysnmp.hlapi.auth import CommunityData
from pysnmp.hlapi.context import ContextData
from pysnmp.proto.rfc1155 import TimeTicks
from pysnmp.proto.rfc1902 import OctetString
from pysnmp.smi.rfc1902 import ObjectIdentity, ObjectType


def test_v1_get_table():
    snmpEngine = SnmpEngine()
    objects = walkCmd(
        snmpEngine,
        CommunityData("public", mpModel=0),
        UdpTransportTarget(("demo.pysnmp.com", 161)),
        ContextData(),
        ObjectType(ObjectIdentity("SNMPv2-MIB", "sysDescr", 0)),
    )

    errorIndication, errorStatus, errorIndex, varBinds = next(objects)

    assert errorIndication is None
    assert errorStatus == 0
    assert len(varBinds) == 1
    assert varBinds[0][0].prettyPrint() == "SNMPv2-MIB::sysObjectID.0"
    assert varBinds[0][1].prettyPrint() == "SNMPv2-SMI::internet"
    # assert isinstance(varBinds[0][1], ObjectIdentifier)

    errorIndication, errorStatus, errorIndex, varBinds = next(objects)

    assert errorIndication is None
    assert errorStatus == 0
    assert len(varBinds) == 1
    assert varBinds[0][0].prettyPrint() == "SNMPv2-MIB::sysUpTime.0"
    # assert isinstance(varBinds[0][1], TimeTicks)

    objects_list = list(objects)
    assert len(objects_list), 50

    snmpEngine.transportDispatcher.closeDispatcher()
