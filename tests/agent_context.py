from pysnmp.carrier.asyncio.dgram import udp, udp6
from pysnmp.entity import config, engine
from pysnmp.entity.rfc3413 import cmdrsp, context
from pysnmp.hlapi.v3arch.asyncio import SnmpEngine
from pysnmp.proto.api import v2c


import asyncio
import time

# Set the port to 1611 instead of 161, because 161 is a
# privileged port and requires root access
AGENT_PORT = 1611


async def start_agent(
    enable_ipv6: bool = False,
    enable_custom_objects: bool = False,
    enable_table_creation: bool = False,
) -> SnmpEngine:
    # Create SNMP engine
    snmpEngine = engine.SnmpEngine()

    # Set up transport endpoint
    config.addTransport(
        snmpEngine,
        udp.DOMAIN_NAME,
        udp.UdpTransport().openServerMode(("localhost", AGENT_PORT)),
    )

    if enable_ipv6:
        config.addTransport(
            snmpEngine,
            udp6.DOMAIN_NAME,
            udp6.Udp6Transport().openServerMode(("localhost", AGENT_PORT)),
        )

    # Set up community data
    config.addV1System(snmpEngine, "public", "public")
    # Add SNMP v3 user
    config.addV3User(
        snmpEngine, "usr-none-none", config.USM_AUTH_NONE, config.USM_PRIV_NONE
    )

    config.addV3User(
        snmpEngine,
        "usr-sha-aes",
        config.USM_AUTH_HMAC96_SHA,
        "authkey1",
        config.USM_PRIV_CFB128_AES,
        "privkey1",
    )

    config.addV3User(snmpEngine, "usr-sha-none", config.USM_AUTH_HMAC96_SHA, "authkey1")

    # Allow read MIB access for this user / securityModels at VACM
    config.addVacmUser(snmpEngine, 1, "public", "noAuthNoPriv", (1, 3, 6), (1, 3, 6))
    config.addVacmUser(snmpEngine, 2, "public", "noAuthNoPriv", (1, 3, 6), (1, 3, 6))
    config.addVacmUser(snmpEngine, 3, "usr-none-none", "noAuthNoPriv", (1, 3, 6))
    config.addVacmUser(snmpEngine, 3, "usr-sha-none", "authNoPriv", (1, 3, 6))
    config.addVacmUser(snmpEngine, 3, "usr-sha-aes", "authPriv", (1, 3, 6))

    # Configure SNMP context
    snmpContext = context.SnmpContext(snmpEngine)

    if enable_custom_objects:
        # --- create custom Managed Object Instances ---
        mibBuilder = snmpContext.getMibInstrum().getMibBuilder()

        MibScalar, MibScalarInstance = mibBuilder.importSymbols(
            "SNMPv2-SMI", "MibScalar", "MibScalarInstance"
        )

        class SlowMibScalarInstance(MibScalarInstance):
            def getValue(self, name, idx):
                time.sleep(2)  # Add a 2-second sleep
                return self.getSyntax().clone(f"Test agent")

            def setValue(self, name, idx, value):
                print(f"SET operation received. New value: {value}")
                return self.getSyntax().clone(value)

        class NoAccessMibScalarInstance(MibScalarInstance):
            def getValue(self, name, idx):
                time.sleep(2)  # Add a 2-second sleep
                return self.getSyntax().clone(f"Test agent")

            def setValue(self, name, idx, value):
                print(f"SET operation received. New value: {value}")
                return self.getSyntax().clone(value)

        mibBuilder.exportSymbols(
            "__MY_MIB",
            MibScalar((1, 3, 6, 1, 4, 1, 60069, 9, 1), v2c.OctetString()),
            SlowMibScalarInstance(
                (1, 3, 6, 1, 4, 1, 60069, 9, 1), (0,), v2c.OctetString()
            ),
            MibScalar((1, 3, 6, 1, 4, 1, 60069, 9, 3), v2c.OctetString()).setMaxAccess(
                "not-accessible"
            ),
            MibScalar((1, 3, 6, 1, 4, 1, 60069, 9, 4), v2c.OctetString()).setMaxAccess(
                "readonly"
            ),  # PySMI <1.3.0 generates such objects
        )

        # --- end of Managed Object Instance initialization ----

    if enable_table_creation:
        # --- define custom SNMP Table within a newly defined EXAMPLE-MIB ---

        mibBuilder = snmpContext.getMibInstrum().getMibBuilder()

        (
            MibTable,
            MibTableRow,
            MibTableColumn,
            MibScalarInstance,
        ) = mibBuilder.importSymbols(
            "SNMPv2-SMI",
            "MibTable",
            "MibTableRow",
            "MibTableColumn",
            "MibScalarInstance",
        )

        (RowStatus,) = mibBuilder.importSymbols("SNMPv2-TC", "RowStatus")

        mibBuilder.exportSymbols(
            "__EXAMPLE-MIB",
            # table object
            exampleTable=MibTable((1, 3, 6, 6, 1)).setMaxAccess("read-create"),
            # table row object, also carries references to table indices
            exampleTableEntry=MibTableRow((1, 3, 6, 6, 1, 5))
            .setMaxAccess("read-create")
            .setIndexNames((0, "__EXAMPLE-MIB", "exampleTableColumn1")),
            # table column: string index
            exampleTableColumn1=MibTableColumn(
                (1, 3, 6, 6, 1, 5, 1), v2c.OctetString()
            ).setMaxAccess("read-create"),
            # table column: string value
            exampleTableColumn2=MibTableColumn(
                (1, 3, 6, 6, 1, 5, 2), v2c.OctetString()
            ).setMaxAccess("read-create"),
            # table column: integer value with default
            exampleTableColumn3=MibTableColumn(
                (1, 3, 6, 6, 1, 5, 3), v2c.Integer32(123)
            ).setMaxAccess("read-create"),
            # table column: row status
            exampleTableStatus=MibTableColumn(
                (1, 3, 6, 6, 1, 5, 4), RowStatus("notExists")
            ).setMaxAccess("read-create"),
        )

        # --- end of custom SNMP table definition, empty table now exists ---

        # --- populate custom SNMP table with one row ---

        (
            exampleTableEntry,
            exampleTableColumn2,
            exampleTableColumn3,
            exampleTableStatus,
        ) = mibBuilder.importSymbols(
            "__EXAMPLE-MIB",
            "exampleTableEntry",
            "exampleTableColumn2",
            "exampleTableColumn3",
            "exampleTableStatus",
        )
        rowInstanceId = exampleTableEntry.getInstIdFromIndices("example record one")
        mibInstrumentation = snmpContext.getMibInstrum()
        mibInstrumentation.writeVars(
            (exampleTableColumn2.name + rowInstanceId, "my string value"),
            (exampleTableColumn3.name + rowInstanceId, 123456),
            (exampleTableStatus.name + rowInstanceId, "createAndGo"),
        )

    # Register SNMP Applications at the SNMP engine for particular SNMP context
    cmdrsp.GetCommandResponder(snmpEngine, snmpContext)
    cmdrsp.NextCommandResponder(snmpEngine, snmpContext)
    cmdrsp.BulkCommandResponder(snmpEngine, snmpContext)
    cmdrsp.SetCommandResponder(snmpEngine, snmpContext)

    # Start the event loop
    snmpEngine.transportDispatcher.jobStarted(1)

    snmpEngine.openDispatcher()

    # Wait for the agent to start
    await asyncio.sleep(1)

    # return the engine
    return snmpEngine


class AgentContextManager:
    """
    A context manager for managing the lifecycle of an SNMP test agent.

    Usage:
    async with AgentContextManager() as agent:
        # Perform operations with the agent

    When the context is entered, the agent is started using the `start_agent()` function.
    When the context is exited, the agent's transport dispatcher is stopped and closed.

    Note: The `start_agent()` function and the `transportDispatcher` attribute are not defined in this code snippet.
    """

    def __init__(
        self,
        enable_ipv6: bool = False,
        enable_custom_objects: bool = False,
        enable_table_creation: bool = False,
    ):
        self.enable_ipv6 = enable_ipv6
        self.enable_custom_objects = enable_custom_objects
        self.enable_table_creation = enable_table_creation

    async def __aenter__(self):
        self.agent = await start_agent(
            self.enable_ipv6, self.enable_custom_objects, self.enable_table_creation
        )
        return self.agent

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        self.agent.transportDispatcher.jobFinished(1)
        self.agent.closeDispatcher()
