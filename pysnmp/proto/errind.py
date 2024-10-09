#
# This file is part of pysnmp software.
#
# Copyright (c) 2005-2020, Ilya Etingof <etingof@gmail.com>
# License: https://www.pysnmp.com/pysnmp/license.html
#


class ErrorIndication(Exception):
    """SNMPv3 error-indication values."""

    def __init__(self, descr=None):
        """Create an error indication object."""
        self.__value = self.__descr = (
            self.__class__.__name__[0].lower() + self.__class__.__name__[1:]
        )
        if descr:
            self.__descr = descr

    def __eq__(self, other) -> bool:
        """
        Compare the instance's value with another value for equality.

        Args:
            other: The value to compare against the instance's value.

        Returns:
            bool: True if the instance's value is equal to the other value, False otherwise.
        """
        return self.__value == other

    def __ne__(self, other) -> bool:
        """
        Compare the instance's value with another value for inequality.

        Args:
            other: The value to compare against the instance's value.

        Returns:
            bool: True if the instance's value is not equal to the other value, False otherwise.
        """
        return self.__value != other

    def __lt__(self, other):
        """
        Compare the instance's value with another value for less than.

        Args:
            other: The value to compare against the instance's value.

        Returns:
            bool: True if the instance's value is less than the other value, False otherwise.
        """
        return self.__value < other

    def __le__(self, other):
        """
        Compare the instance's value with another value for less than or equal to.

        Args:
            other: The value to compare against the instance's value.

        Returns:
            bool: True if the instance's value is less than or equal to the other value, False otherwise.
        """
        return self.__value <= other

    def __gt__(self, other):
        """
        Compare the instance's value with another value for greater than.

        Args:
            other: The value to compare against the instance's value.

        Returns:
            bool: True if the instance's value is greater than the other value, False otherwise.
        """
        return self.__value > other

    def __ge__(self, other):
        """
        Compare the instance's value with another value for greater than or equal to.

        Args:
            other: The value to compare against the instance's value.

        Returns:
            bool: True if the instance's value is greater than or equal to the other value, False otherwise.
        """
        return self.__value >= other

    def __str__(self):
        """Return error indication as a string."""
        return self.__descr


# SNMP message processing errors


class SerializationError(ErrorIndication):
    """SNMP message serialization error."""

    pass


serializationError = SerializationError(  # noqa: N816
    "SNMP message serialization error"
)


class DeserializationError(ErrorIndication):
    """SNMP message deserialization error."""

    pass


deserializationError = DeserializationError(  # noqa: N816
    "SNMP message deserialization error"
)


class ParseError(DeserializationError):
    """SNMP message parsing error."""

    pass


parseError = ParseError("SNMP message deserialization error")  # noqa: N816


class UnsupportedMsgProcessingModel(ErrorIndication):
    """Unsupported SNMP message processing model."""

    pass


unsupportedMsgProcessingModel = UnsupportedMsgProcessingModel(  # noqa: N816
    "Unknown SNMP message processing model ID encountered"
)


class UnknownPDUHandler(ErrorIndication):
    """Unknown SNMP PDU handler."""

    pass


unknownPDUHandler = UnknownPDUHandler("Unhandled PDU type encountered")  # noqa: N816


class UnsupportedPDUtype(ErrorIndication):
    """Unsupported SNMP PDU type."""

    pass


unsupportedPDUtype = UnsupportedPDUtype(  # noqa: N816
    "Unsupported SNMP PDU type encountered"
)


class RequestTimedOut(ErrorIndication):
    """SNMP request timed out."""

    pass


requestTimedOut = RequestTimedOut(  # noqa: N816
    "No SNMP response received before timeout"
)


class EmptyResponse(ErrorIndication):
    """Empty SNMP response message."""

    pass


emptyResponse = EmptyResponse("Empty SNMP response message")  # noqa: N816


class NonReportable(ErrorIndication):
    """SNMP report PDU generation not attempted."""

    pass


nonReportable = NonReportable("Report PDU generation not attempted")  # noqa: N816


class DataMismatch(ErrorIndication):
    """SNMP request/response parameters mismatch."""

    pass


dataMismatch = DataMismatch("SNMP request/response parameters mismatched")  # noqa: N816


class EngineIDMismatch(ErrorIndication):
    """SNMP engine ID mismatch."""

    pass


engineIDMismatch = EngineIDMismatch("SNMP engine ID mismatch encountered")  # noqa: N816


class UnknownEngineID(ErrorIndication):
    """Unknown SNMP engine ID."""

    pass


unknownEngineID = UnknownEngineID("Unknown SNMP engine ID encountered")  # noqa: N816


class TooBig(ErrorIndication):
    """SNMP message too big."""

    pass


tooBig = TooBig("SNMP message will be too big")  # noqa: N816


class LoopTerminated(ErrorIndication):
    """SNMP entities talk terminated."""

    pass


loopTerminated = LoopTerminated("Infinite SNMP entities talk terminated")  # noqa: N816


class InvalidMsg(ErrorIndication):
    """Invalid SNMP message header parameters."""

    pass


invalidMsg = InvalidMsg(  # noqa: N816
    "Invalid SNMP message header parameters encountered"
)


# SNMP security modules errors


class UnknownCommunityName(ErrorIndication):
    """Unknown SNMP community name."""

    pass


unknownCommunityName = UnknownCommunityName(  # noqa: N816
    "Unknown SNMP community name encountered"
)


class NoEncryption(ErrorIndication):
    """No encryption services configured."""

    pass


noEncryption = NoEncryption("No encryption services configured")  # noqa: N816


class EncryptionError(ErrorIndication):
    """SNMP message encryption error."""

    pass


encryptionError = EncryptionError("Ciphering services not available")  # noqa: N816


class DecryptionError(ErrorIndication):
    """SNMP message decryption error."""

    pass


decryptionError = DecryptionError(  # noqa: N816
    "Ciphering services not available or ciphertext is broken"
)


class NoAuthentication(ErrorIndication):
    """No authentication services configured."""

    pass


noAuthentication = NoAuthentication(  # noqa: N816
    "No authentication services configured"
)


class AuthenticationError(ErrorIndication):
    """SNMP message authentication error."""

    pass


authenticationError = AuthenticationError(  # noqa: N816
    "Ciphering services not available or bad parameters"
)


class AuthenticationFailure(ErrorIndication):
    """SNMP message authentication failure."""

    pass


authenticationFailure = AuthenticationFailure("Authenticator mismatched")  # noqa: N816


class UnsupportedAuthProtocol(ErrorIndication):
    """Unsupported SNMP authentication protocol."""

    pass


unsupportedAuthProtocol = UnsupportedAuthProtocol(  # noqa: N816
    "Authentication protocol is not supported"
)


class UnsupportedPrivProtocol(ErrorIndication):
    """Unsupported SNMP privacy protocol."""

    pass


unsupportedPrivProtocol = UnsupportedPrivProtocol(  # noqa: N816
    "Privacy protocol is not supported"
)


class UnknownSecurityName(ErrorIndication):
    """Unknown SNMP security name."""

    pass


unknownSecurityName = UnknownSecurityName(  # noqa: N816
    "Unknown SNMP security name encountered"
)


class UnsupportedSecurityModel(ErrorIndication):
    """Unsupported SNMP security model."""

    pass


unsupportedSecurityModel = UnsupportedSecurityModel(  # noqa: N816
    "Unsupported SNMP security model"
)


class UnsupportedSecurityLevel(ErrorIndication):
    """Unsupported SNMP security level."""

    pass


unsupportedSecurityLevel = UnsupportedSecurityLevel(  # noqa: N816
    "Unsupported SNMP security level"
)


class NotInTimeWindow(ErrorIndication):
    """SNMP message timing parameters not in windows of trust."""

    pass


notInTimeWindow = NotInTimeWindow(  # noqa: N816
    "SNMP message timing parameters not in windows of trust"
)


class UnknownUserName(ErrorIndication):
    """Unknown SNMP user name."""

    pass


unknownUserName = UnknownUserName("Unknown USM user")  # noqa: N816


class WrongDigest(ErrorIndication):
    """Wrong SNMP PDU digest."""

    pass


wrongDigest = WrongDigest("Wrong SNMP PDU digest")  # noqa: N816


class ReportPduReceived(ErrorIndication):
    """Remote SNMP engine reported error."""

    pass


reportPduReceived = ReportPduReceived("Remote SNMP engine reported error")  # noqa: N816


# SNMP access-control errors


class NoSuchView(ErrorIndication):
    """No such MIB view currently exists."""

    pass


noSuchView = NoSuchView("No such MIB view currently exists")  # noqa: N816


class NoAccessEntry(ErrorIndication):
    """Access to MIB node denied."""

    pass


noAccessEntry = NoAccessEntry("Access to MIB node denied")  # noqa: N816


class NoGroupName(ErrorIndication):
    """No such VACM group configured."""

    pass


noGroupName = NoGroupName("No such VACM group configured")  # noqa: N816


class NoSuchContext(ErrorIndication):
    """No such SNMP context exists."""

    pass


noSuchContext = NoSuchContext("SNMP context now found")  # noqa: N816


class NotInView(ErrorIndication):
    """Requested OID is out of MIB view."""

    pass


notInView = NotInView("Requested OID is out of MIB view")  # noqa: N816


class AccessAllowed(ErrorIndication):
    """Access to MIB node allowed."""

    pass


accessAllowed = AccessAllowed()  # noqa: N816


class OtherError(ErrorIndication):
    """Unspecified SNMP engine error."""

    pass


otherError = OtherError("Unspecified SNMP engine error occurred")  # noqa: N816


# SNMP Apps errors


class OidNotIncreasing(ErrorIndication):
    """OID not increasing."""

    pass


oidNotIncreasing = OidNotIncreasing("OID not increasing")  # noqa: N816
