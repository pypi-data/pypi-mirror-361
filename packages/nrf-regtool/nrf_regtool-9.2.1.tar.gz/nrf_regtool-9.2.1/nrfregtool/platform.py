# Copyright (c) 2022 Nordic Semiconductor ASA
# SPDX-License-Identifier: Apache-2.0

"""Various types and definitions for the Haltium platform."""

from __future__ import annotations

import enum
from dataclasses import dataclass
from typing import Optional

from ._common import get_field, update_field


@enum.unique
class Product(enum.Enum):
    """Enumeration of supported product names in the Haltium family."""

    NRF54H20 = enum.auto()
    NRF9280 = enum.auto()

    @classmethod
    def _missing_(cls, value: object) -> Optional[Product]:
        """Custom enum behavior to support case insensitive values."""
        if not isinstance(value, str):
            return None
        return cls.__members__.get(value.upper())

    @property
    def product_code(self) -> ProductCode:
        match self:
            case Product.NRF54H20:
                return ProductCode(part_number=0x16, revision=0x2)
            case Product.NRF9280:
                return ProductCode(part_number=0x12, revision=0x1)
            case _:
                raise ValueError(f"No product code found for {self}")


@dataclass
class ProductCode:
    part_number: int
    revision: int


@enum.unique
class AddressOffset(enum.IntEnum):
    """Address bit offsets, defined by Address Format of the product specification."""

    REGION = 29
    SECURITY = 28
    DOMAINID = 24
    ADDR = 23


def secure_address_get(address: int) -> int:
    """Get the TrustZone secure address for the given address"""
    addr = Address(address)
    addr.security = True
    return int(addr)


@enum.unique
class AddressRegion(enum.IntEnum):
    """Address regions, defined by Address Format of the product specification."""

    PROGRAM = 0
    DATA = 1
    PERIPHERAL = 2
    EXT_XIP = 3
    EXT_XIP_ENCRYPTED = 4
    STM = 5
    CPU = 7

    @classmethod
    def from_address(cls, address: int) -> AddressRegion:
        """Get the address region of an address."""
        return Address(address).region


ADDRESS_REGION_POS = 29
ADDRESS_REGION_MASK = 0x7 << ADDRESS_REGION_POS
ADDRESS_SECURITY_POS = 28
ADDRESS_SECURITY_MASK = 0x1 << ADDRESS_SECURITY_POS
ADDRESS_DOMAIN_POS = 24
ADDRESS_DOMAIN_MASK = 0xF << ADDRESS_DOMAIN_POS
ADDRESS_BUS_POS = 16
ADDRESS_BUS_MASK = 0xFF << ADDRESS_BUS_POS
ADDRESS_SLAVE_POS = 12
ADDRESS_SLAVE_MASK = 0xF << ADDRESS_SLAVE_POS
ADDRESS_PERIPHID_POS = 12
ADDRESS_PERIPHID_MASK = 0x7FF << ADDRESS_PERIPHID_POS
ADDRESS_SPACE_POS = 0
ADDRESS_PROGRAM_DATA_SPACE_MASK = 0xFF_FFFF
ADDRESS_PERIPHERAL_SPACE_MASK = 0xFFF
ADDRESS_DEFAULT_SPACE_MASK = 0x1FFF_FFFF


# Regions that have domain ID and security fields
_HAS_DOMAIN_SECURITY = [
    AddressRegion.PROGRAM,
    AddressRegion.DATA,
    AddressRegion.PERIPHERAL,
    AddressRegion.STM,
]

# Regions that have the peripheral address format
_HAS_PERIPH_BITS = [
    AddressRegion.PERIPHERAL,
    AddressRegion.STM,
]


class Address:
    """Helper for working with addresses on the Haltium products."""

    def __init__(self, value: int = 0) -> None:
        self._val = value

    def __repr__(self) -> str:
        if self.region in _HAS_DOMAIN_SECURITY:
            domain_sec_str = (
                f", domain={self.domain.name} ({int(self.domain)}), "
                f"security={self.security}"
            )
        else:
            domain_sec_str = ""

        if self.region in _HAS_PERIPH_BITS:
            periph_bits_str = (
                f", bus={self.bus} (0b{self.bus:09_b}), "
                f"slave_index={self.slave_index} (0b{self.slave_index:09_b})"
            )
        else:
            periph_bits_str = ""

        field_str = (
            f"region={self.region.name} ({int(self.region)}){domain_sec_str}{periph_bits_str}, "
            f"address_space=0x{self.address_space:_x}"
        )

        return f"{type(self).__name__}({field_str})"

    def __str__(self) -> str:
        return repr(self)

    @property
    def region(self) -> AddressRegion:
        """Address region."""
        return AddressRegion(
            get_field(self._val, ADDRESS_REGION_POS, ADDRESS_REGION_MASK)
        )

    @region.setter
    def region(self, new: int) -> None:
        self._val = update_field(
            self._val, new, ADDRESS_REGION_POS, ADDRESS_REGION_MASK
        )

    @property
    def security(self) -> bool:
        """Address security (only present in some regions)."""
        self._check_has_security()
        return bool(get_field(self._val, ADDRESS_SECURITY_POS, ADDRESS_SECURITY_MASK))

    @security.setter
    def security(self, new: bool) -> None:
        self._check_has_security()
        self._val = update_field(
            self._val, int(new), ADDRESS_SECURITY_POS, ADDRESS_SECURITY_MASK
        )

    def _check_has_security(self) -> None:
        self._check_region_has_field(_HAS_DOMAIN_SECURITY, "security bit")

    @property
    def domain(self) -> DomainID:
        """Address domain ID (only present in some regions)."""
        self._check_has_domain_id()
        return DomainID(get_field(self._val, ADDRESS_DOMAIN_POS, ADDRESS_DOMAIN_MASK))

    @domain.setter
    def domain(self, new: DomainID | int) -> None:
        self._check_has_domain_id()
        self._val = update_field(
            self._val, new, ADDRESS_DOMAIN_POS, ADDRESS_DOMAIN_MASK
        )

    def _check_has_domain_id(self) -> None:
        self._check_region_has_field(_HAS_DOMAIN_SECURITY, "domain ID")

    @property
    def bus(self) -> int:
        """Bus ID (only present in some regions)."""
        self._check_has_bus()
        return get_field(self._val, ADDRESS_BUS_POS, ADDRESS_BUS_MASK)

    @bus.setter
    def bus(self, new: int) -> None:
        self._check_has_bus()
        self._val = update_field(self._val, new, ADDRESS_BUS_POS, ADDRESS_BUS_MASK)

    def _check_has_bus(self) -> None:
        self._check_region_has_field(_HAS_PERIPH_BITS, "Peripheral/APB bus number")

    @property
    def slave_index(self) -> int:
        """Slave index (only present in some regions)."""
        self._check_has_slave_index()
        return get_field(self._val, ADDRESS_SLAVE_POS, ADDRESS_SLAVE_MASK)

    @slave_index.setter
    def slave_index(self, new: int) -> None:
        self._check_has_slave_index()
        self._val = update_field(self._val, new, ADDRESS_SLAVE_POS, ADDRESS_SLAVE_MASK)

    def _check_has_slave_index(self) -> None:
        self._check_region_has_field(_HAS_PERIPH_BITS, "Peripheral/APB slave index")

    @property
    def address_space(self) -> int:
        """Internal address space address (semantics depend on the region)."""
        match self.region:
            case AddressRegion.PROGRAM | AddressRegion.DATA:
                return get_field(
                    self._val, ADDRESS_SPACE_POS, ADDRESS_PROGRAM_DATA_SPACE_MASK
                )
            case AddressRegion.PERIPHERAL | AddressRegion.STM:
                return get_field(
                    self._val, ADDRESS_SPACE_POS, ADDRESS_PERIPHERAL_SPACE_MASK
                )
            case _:
                return get_field(
                    self._val, ADDRESS_SPACE_POS, ADDRESS_DEFAULT_SPACE_MASK
                )

    @address_space.setter
    def address_space(self, new: int) -> None:
        match self.region:
            case AddressRegion.PROGRAM | AddressRegion.DATA:
                self._val = update_field(
                    self._val, new, ADDRESS_SPACE_POS, ADDRESS_PROGRAM_DATA_SPACE_MASK
                )
            case AddressRegion.PERIPHERAL | AddressRegion.STM:
                self._val = update_field(
                    self._val, new, ADDRESS_SPACE_POS, ADDRESS_PERIPHERAL_SPACE_MASK
                )
            case _:
                self._val = update_field(
                    self._val, new, ADDRESS_SPACE_POS, ADDRESS_DEFAULT_SPACE_MASK
                )

    def _check_region_has_field(
        self, valid_regions: list[AddressRegion], field_name: str
    ) -> None:
        if self.region not in valid_regions:
            raise ValueError(
                f"{field_name} is not defined for address region {self.region.name}"
            )

    def __int__(self) -> int:
        return self._val


def peripheral_id_get(periph_address: int) -> int:
    """Get the peripheral ID of a peripheral address."""
    return get_field(periph_address, ADDRESS_PERIPHID_POS, ADDRESS_PERIPHID_MASK)


@enum.unique
class DomainID(enum.IntEnum):
    """Domain IDs in Haltium products."""

    RESERVED = 0
    SECURE = 1
    APPLICATION = 2
    RADIOCORE = 3
    CELLCORE = 4
    CELLDSP = 5
    CELLRF = 6
    ISIMCORE = 7
    GLOBALFAST = 12
    GLOBALSLOW = 13
    GLOBAL_ = 14
    GLOBAL = 15

    @classmethod
    def from_address(cls, address: int) -> DomainID:
        """Get the domain ID of an address."""
        return cls((address >> AddressOffset.DOMAINID) & 0xF)

    @classmethod
    def from_processor(cls, processor: ProcessorID | int) -> DomainID:
        """Get the domain ID corresponding to a processor ID."""
        processor_domain = {
            ProcessorID.SECURE: cls.SECURE,
            ProcessorID.APPLICATION: cls.APPLICATION,
            ProcessorID.RADIOCORE: cls.RADIOCORE,
            ProcessorID.CELLCORE: cls.CELLCORE,
            ProcessorID.CELLDSP: cls.CELLDSP,
            ProcessorID.CELLRF: cls.CELLRF,
            ProcessorID.ISIMCORE: cls.ISIMCORE,
            ProcessorID.SYSCTRL: cls.GLOBALFAST,
            ProcessorID.PPR: cls.GLOBALSLOW,
            ProcessorID.FLPR: cls.GLOBAL_,
        }
        return processor_domain[ProcessorID(processor)]

    @property
    def c_enum(self) -> str:
        return f"NRF_DOMAIN_{self.name.upper()}"


@enum.unique
class OwnerID(enum.IntEnum):
    """Enumeration of ownership IDs in haltium products."""

    NONE = 0
    SECURE = 1
    APPLICATION = 2
    RADIOCORE = 3
    CELL = 4
    ISIMCORE = 5
    SYSCTRL = 8

    @classmethod
    def from_domain(cls, domain: DomainID | int) -> OwnerID:
        """Get the owner ID corresponding to a domain ID."""
        domain_owner = {
            DomainID.SECURE: cls.SECURE,
            DomainID.APPLICATION: cls.APPLICATION,
            DomainID.RADIOCORE: cls.RADIOCORE,
            DomainID.CELLCORE: cls.CELL,
            DomainID.CELLDSP: cls.CELL,
            DomainID.CELLRF: cls.CELL,
            DomainID.ISIMCORE: cls.ISIMCORE,
            DomainID.GLOBALFAST: cls.SYSCTRL,
        }
        return domain_owner[DomainID(domain)]

    @classmethod
    def from_processor(cls, processor: ProcessorID | int) -> OwnerID:
        """Get the owner ID corresponding to a processor ID."""
        return cls.from_domain(DomainID.from_processor(processor))

    @property
    def c_enum(self) -> str:
        return f"NRF_OWNER_{self.name.upper()}"


@enum.unique
class ProcessorID(enum.IntEnum):
    """Processor IDs in haltium products."""

    SECURE = 1
    APPLICATION = 2
    RADIOCORE = 3
    CELLCORE = 4
    CELLDSP = 5
    CELLRF = 6
    ISIMCORE = 7
    BBPR = 11
    SYSCTRL = 12
    PPR = 13
    FLPR = 14

    @classmethod
    def from_domain(cls, domain: DomainID | int) -> ProcessorID:
        """Get the processor ID corresponding to a domain ID."""
        domain_processor = {
            DomainID.SECURE: cls.SECURE,
            DomainID.APPLICATION: cls.APPLICATION,
            DomainID.RADIOCORE: cls.RADIOCORE,
            DomainID.CELLCORE: cls.CELLCORE,
            DomainID.CELLDSP: cls.CELLDSP,
            DomainID.CELLRF: cls.CELLRF,
            DomainID.ISIMCORE: cls.ISIMCORE,
            DomainID.GLOBALFAST: cls.SYSCTRL,
            DomainID.GLOBALSLOW: cls.PPR,
            DomainID.GLOBAL_: cls.FLPR,
        }
        return domain_processor[DomainID(domain)]

    @property
    def c_enum(self) -> str:
        return f"NRF_PROCESSOR_{self.name.upper()}"


@enum.unique
class Ctrlsel(enum.IntEnum):
    """
    Enumeration of GPIO.PIN_CNF[n].CTRLSEL values.
    The list here may not be exhaustive.
    """

    GPIO = 0
    VPR_GRC = 1
    CAN_PWM_I3C = 2
    SERIAL0 = 3
    EXMIF_RADIO_SERIAL1 = 4
    CAN_TDM_SERIAL2 = 5
    CAN = 6
    TND = 7


# Default CTRLSEL value indicating that CTRLSEL should not be used
CTRLSEL_DEFAULT = Ctrlsel.GPIO
