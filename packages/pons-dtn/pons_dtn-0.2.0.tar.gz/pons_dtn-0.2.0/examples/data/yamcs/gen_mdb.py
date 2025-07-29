from yamcs.pymdb import (
    ArgumentEntry,
    Command,
    IntegerArgument,
    System,
    ccsds,
    uint16_t,
    FloatArgument,
    AggregateArgument,
    float32_t,
)

spacecraft = System("Spacecraft")
ccsds_header = ccsds.add_ccsds_header(spacecraft)

command_id = IntegerArgument(
    name="command_id",
    signed=False,
    encoding=uint16_t,
)


vec3_t = AggregateArgument(
    name="vec3_t",
    members=[
        FloatArgument(name="x", encoding=float32_t),
        FloatArgument(name="y", encoding=float32_t),
        FloatArgument(name="z", encoding=float32_t),
    ],
)

project_command = Command(
    system=spacecraft,
    name="MyProjectPacket",
    abstract=True,
    base=ccsds_header.tc_command,
    assignments={
        ccsds_header.tc_secondary_header.name: "NotPresent",
        ccsds_header.tc_apid.name: 101,
    },
    arguments=[
        command_id,
    ],
    entries=[
        ArgumentEntry(command_id),
    ],
)

reboot_command = Command(
    system=spacecraft,
    base=project_command,
    name="Reboot",
    assignments={command_id.name: 1},
)

switch_voltage_on = Command(
    system=spacecraft,
    base=project_command,
    name="SwitchVoltageOn",
    short_description="Switches a battery on",
    assignments={command_id.name: 2},
    arguments=[
        IntegerArgument(
            name="battery",
            short_description="Number of the battery",
            signed=False,
            minimum=1,
            maximum=3,
            encoding=uint16_t,
        ),
    ],
)

switch_voltage_off = Command(
    system=spacecraft,
    base=project_command,
    name="SwitchVoltageOff",
    short_description="Switches a battery off",
    assignments={command_id.name: 3},
    arguments=[
        IntegerArgument(
            name="battery",
            short_description="Number of the battery",
            signed=False,
            minimum=1,
            maximum=3,
            encoding=uint16_t,
        ),
    ],
)

vehicle_move = Command(
    system=spacecraft,
    base=project_command,
    name="VehicleMove",
    short_description="Moves the vehicle to a new position",
    assignments={command_id.name: 4},
    arguments=[
        FloatArgument(name="x", encoding=float32_t),
        FloatArgument(name="y", encoding=float32_t),
        FloatArgument(name="z", encoding=float32_t),
    ],
)
cancel_command = Command(
    system=spacecraft,
    base=project_command,
    name="Cancel",
    assignments={command_id.name: 5},
)

# with open("ccsds.xml", "wt") as f:
#    spacecraft.dump(f)

print(spacecraft.dumps())
