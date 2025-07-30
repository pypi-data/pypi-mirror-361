# -*- coding:utf-8 -*-
# Written for Python 3.12
# Formatted with Black

# Packet parser for App_PAL (OPENCLOSE)

from datetime import datetime
from typing import Any, final

from overrides import override
from pydantic import Field, field_serializer

from .. import common


@final
class ParsedPacket(common.ParsedPacketBase):
    """Dataclass for parsed packets from App_PAL (OPENCLOSE)

    Attributes
    ----------
    router_serial_id: UInt32
        Serial ID for the first router device (0x80000000 with no routing)
    ai1_voltage: common.UInt16
        Voltage for AI1 port in mV
    magnet_state: common.MagnetState
        Magnet state
    magnet_state_changed: bool
        True if the magnet state was changed
    """

    router_serial_id: common.UInt32 = Field(
        default=common.UInt32(0), ge=common.UInt32(0), le=common.UInt32(0xFFFFFFFF)
    )
    ai1_voltage: common.UInt16 = Field(
        default=common.UInt16(0), ge=common.UInt16(0), le=common.UInt16(3700)
    )
    magnet_state: common.MagnetState = Field(default=common.MagnetState.NOT_DETECTED)
    magnet_state_changed: bool = Field(default=False)

    @field_serializer("router_serial_id")
    def serialize_router_serial_id(self, router_serial_id: common.UInt32) -> str:
        """Print router_serial_id in HEX for JSON or something

        Parameters
        ----------
        router_serial_id : common.UInt32
            Router serial ID

        Returns
        -------
        str
            Serialized text for JSON or something
        """

        return router_serial_id.hex().upper()

    @field_serializer("magnet_state")
    def serialize_magnet_state(self, magnet_state: common.MagnetState) -> str:
        """Print magnet_state in readable names for JSON or something

        Parameters
        ----------
        magnet_state : common.MagnetState
            Magnet state

        Returns
        -------
        str
            Serialized text for JSON or something
        """

        return magnet_state.name


@final
class PacketParser(common.PacketParserBase):
    """Packet parser for App_PAL (OPENCLOSE)"""

    @staticmethod
    @override
    def is_valid(bare_packet: common.BarePacket) -> bool:
        """Check the given bare packet is valid or not

        Parameters
        ----------
        bare_packet : common.BarePacket
            Bare packet content

        Returns
        -------
        bool
            True if valid

        Notes
        -----
        Static overridden method
        """
        if (
            (bare_packet.u8_at(0) & 0x80) == 0x80
            and (bare_packet.u8_at(7) & 0x80) == 0x80
            and bare_packet.u8_at(12) == 0x80
            and bare_packet.u8_at(13) == 0x81
            and len(bare_packet.payload) == 33
        ):
            return True
        return False

    @staticmethod
    @override
    def parse(bare_packet: common.BarePacket) -> ParsedPacket | None:
        """Try to parse the given bare packet

        Parameters
        ----------
        bare_packet : common.BarePacket
            Bare packet content

        Returns
        -------
        ParsedPacket | None
            Parsed packet data if valid else None

        Notes
        -----
        Static overridden method
        """
        if not PacketParser.is_valid(bare_packet):
            return None
        parsed_packet_data: dict[str, Any] = {
            "time_parsed": datetime.now(common.Timezone),
            "packet_type": common.PacketType.APP_PAL_OPENCLOSE,
            "sequence_number": bare_packet.u16_at(5),
            "source_serial_id": bare_packet.u32_at(7),
            "source_logical_id": bare_packet.u8_at(11),
            "lqi": bare_packet.u8_at(4),
            "supply_voltage": bare_packet.u16_at(19),
            "router_serial_id": bare_packet.u32_at(0),
            "ai1_voltage": bare_packet.u16_at(25),
            "magnet_state": common.MagnetState(bare_packet.u8_at(31) & 0x0F),
            "magnet_state_changed": False if bare_packet.u8_at(31) & 0x80 else True,
        }
        return ParsedPacket(**parsed_packet_data)
