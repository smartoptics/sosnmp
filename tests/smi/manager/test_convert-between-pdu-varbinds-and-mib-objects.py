import pytest
from unittest.mock import patch
from pysnmp.smi import builder, view, rfc1902, error


def test_addAsn1MibSource():
    mibBuilder = builder.MibBuilder()
    mibView = view.MibViewController(mibBuilder)
    mibVar = rfc1902.ObjectIdentity("IF-MIB", "ifInOctets", 1)
    mibVar.add_asn1_mib_source("https://mibs.pysnmp.com/asn1/@mib@")
    mibVar.resolve_with_mib(mibView)
    assert mibVar.prettyPrint() == "IF-MIB::ifInOctets.1"
