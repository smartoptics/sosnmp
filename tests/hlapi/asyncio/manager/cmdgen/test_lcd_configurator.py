from unittest import mock

import pytest

from pysnmp.hlapi.v3arch.asyncio import *
from pysnmp.hlapi.v3arch.asyncio.lcd import CommandGeneratorLcdConfigurator


@mock.patch("pysnmp.entity.config.addV3User")
@mock.patch("pysnmp.entity.config.delV3User")
@pytest.mark.asyncio
async def test_usm_auth_cache_cleared(delV3User, addV3User):
    """
    Ensure auth cache is cleared when auth data is changed.
    """
    snmpEngine = SnmpEngine()
    transportTarget = await UdpTransportTarget.create(("198.51.100.1", 161))

    authDataValues = {
        "userName": "username",
        "authKey": "authkey1",
        "authProtocol": USM_AUTH_HMAC96_MD5,
        "privKey": "privkey1",
        "privProtocol": USM_PRIV_CFB128_AES,
    }

    lcd = CommandGeneratorLcdConfigurator()
    initialAuthData = UsmUserData(**authDataValues)
    lcd.configure(snmpEngine, initialAuthData, transportTarget)
    addV3User.assert_called_with(
        snmpEngine,
        initialAuthData.userName,
        initialAuthData.authProtocol,
        initialAuthData.authKey,
        initialAuthData.privProtocol,
        initialAuthData.privKey,
        securityEngineId=initialAuthData.securityEngineId,
        securityName=initialAuthData.securityName,
        authKeyType=initialAuthData.authKeyType,
        privKeyType=initialAuthData.privKeyType,
    )

    # Ensure we do not add/delete if nothing changes
    addV3User.reset_mock()
    lcd.configure(snmpEngine, initialAuthData, transportTarget)
    addV3User.assert_not_called()
    delV3User.assert_not_called()

    changeAuthValues = {
        "authKey": "authKey2",
        "privProtocol": USM_PRIV_CBC56_DES,
        "authProtocol": USM_AUTH_HMAC96_SHA,
        "privKey": "privKey2",
    }

    for field, value in changeAuthValues.items():
        addV3User.reset_mock()
        delV3User.reset_mock()

        authDataValues[field] = value
        authData = UsmUserData(**authDataValues)
        lcd.configure(snmpEngine, authData, transportTarget)

        delV3User.assert_called_with(
            snmpEngine,
            authData.userName,
            authData.securityEngineId,
        )

        addV3User.assert_called_with(
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
