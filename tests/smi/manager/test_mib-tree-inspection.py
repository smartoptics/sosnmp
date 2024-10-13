import pytest
from pysnmp.smi import builder, view

mibBuilder = builder.MibBuilder()
mibBuilder.add_mib_sources(builder.DirMibSource("/opt/pysnmp_mibs"))
mibBuilder.load_modules("SNMPv2-MIB", "SNMP-FRAMEWORK-MIB", "SNMP-COMMUNITY-MIB")
mibView = view.MibViewController(mibBuilder)


def test_getNodeName_by_OID():
    oid, label, suffix = mibView.get_node_name((1, 3, 6, 1, 2, 1, 1, 1))
    assert oid == (1, 3, 6, 1, 2, 1, 1, 1)
    assert label == (
        "iso",
        "org",
        "dod",
        "internet",
        "mgmt",
        "mib-2",
        "system",
        "sysDescr",
    )
    assert suffix == ()


def test_getNodeName_by_label():
    oid, label, suffix = mibView.get_node_name((1, 3, 6, 1, 2, "mib-2", 1, "sysDescr"))
    assert oid == (1, 3, 6, 1, 2, 1, 1, 1)
    assert label == (
        "iso",
        "org",
        "dod",
        "internet",
        "mgmt",
        "mib-2",
        "system",
        "sysDescr",
    )
    assert suffix == ()


def test_getNodeName_by_symbol_description():
    oid, label, suffix = mibView.get_node_name(("sysDescr",))
    assert oid == (1, 3, 6, 1, 2, 1, 1, 1)
    assert label == (
        "iso",
        "org",
        "dod",
        "internet",
        "mgmt",
        "mib-2",
        "system",
        "sysDescr",
    )
    assert suffix == ()


def test_getNodeName_by_symbol_description_with_module_name():
    oid, label, suffix = mibView.get_node_name(("snmpEngineID",), "SNMP-FRAMEWORK-MIB")
    assert oid == (1, 3, 6, 1, 6, 3, 10, 2, 1, 1)
    assert label == (
        "iso",
        "org",
        "dod",
        "internet",
        "snmpV2",
        "snmpModules",
        "snmpFrameworkMIB",
        "snmpFrameworkMIBObjects",
        "snmpEngine",
        "snmpEngineID",
    )
    assert suffix == ()

    (mibNode,) = mibBuilder.import_symbols("SNMP-FRAMEWORK-MIB", "snmpEngineID")
    assert mibNode.syntax.prettyPrint() != ""


def test_getNodeName_by_symbol_location_lookup_by_name():
    modName, symName, suffix = mibView.get_node_location(("snmpCommunityEntry",))
    assert modName == "SNMP-COMMUNITY-MIB"
    assert symName == "snmpCommunityEntry"
    assert suffix == ()
