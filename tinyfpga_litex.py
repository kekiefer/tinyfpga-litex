#!/usr/bin/env python3

import argparse
import importlib
import os

from migen import Cat
from migen.genlib.io import CRG

from litex.build.generic_platform import Subsignal, IOStandard, Pins

from litex.soc.integration.soc_core import *
from litex.soc.integration.builder import *
from litex.soc.cores import spi_flash
from litex.soc.cores.gpio import GPIOOut

from litex_boards.partner.platforms import tinyfpga_bx

# TinyFPGASoC ------------------------------------------------------------------

class TinyLiteX(SoCCore):
    """
    Basic SoC for TinyFPGA BX
    """

    # Add SPI flash to the Control and Status Register memory space
    csr_map = {
        "spiflash":   16,
        "leds": None, # csr_id not provided: allocate csr to the first available id
    }
    csr_map.update(SoCCore.csr_map)

    # Add SPI flash to the memory map
    mem_map = {
        "spiflash": 0x20000000,  # (default shadow @0xa0000000)
    }
    mem_map.update(SoCCore.mem_map)

    def __init__(self, platform, **kwargs):

        # We need at least a serial port peripheral
        platform.add_extension(tinyfpga_bx.serial)

        sys_clk_freq = int(1e9/platform.default_clk_period)
        SoCCore.__init__(self, platform, clk_freq=sys_clk_freq,
                         integrated_rom_size=0,
                         integrated_main_ram_size=0,
                         integrated_sram_size=10*1024,
                         cpu_reset_address=0x20050000,
                         **kwargs)

        # Configure the clock and reset generator
        self.submodules.crg = CRG(platform.request(platform.default_clk_name))

        # Configure the TinyFPGA BX SPI flash
        self.submodules.spiflash = spi_flash.SpiFlash(
            platform.request("spiflash"),
            dummy=8, div=2, endianness="little"
        )
        self.config["SPIFLASH_PAGE_SIZE"] = 256
        self.config["SPIFLASH_SECTOR_SIZE"] = 0x10000

        # Map the entire SPI flash
        spiflash_total_size = int((8/8)*1024*1024)
        self.register_mem("spiflash", self.mem_map["spiflash"],
                          self.spiflash.bus, size=spiflash_total_size)

        # Configure a special region for the ROM (bootloader/bios)
        self.flash_boot_address = 0x20050000 + 0x8000
        self.add_memory_region("rom", self.cpu_reset_address, 0x8000)

        # Configure a special region for our user code (firmware)
        self.add_memory_region(
            "user_flash",
            self.flash_boot_address,
            # Leave a grace area- possible one-by-off bug in add_memory_region?
            # Possible fix: addr < origin + length - 1
            spiflash_total_size - (self.flash_boot_address - self.mem_map["spiflash"]) - 0x100
        )

        # Configure the board LED
        leds = platform.request("user_led", 0)
        self.submodules.leds = GPIOOut(leds)

        # Need to specify '-s' flash isn't put into deep-sleep power down after bitstream loads
        platform.toolchain.nextpnr_build_template[2] = "icepack -s {build_name}.txt {build_name}.bin"

# Build ------------------------------------------------------------------------

def main():
    """
    Program to build the TinyLiteX SoC
    """

    # Configure command line arguments
    parser = argparse.ArgumentParser(description="TinyFPGA BX LiteX SoC")
    builder_args(parser)
    soc_core_args(parser)
    parser.add_argument("--platform",
                        help="module name of the platform to build for",
                        default="litex_boards.partner.platforms.tinyfpga_bx")
    parser.add_argument("--gateware-toolchain", default=None,
                        help="FPGA gateware toolchain used for build")
    args = parser.parse_args()

    # Pick the platform module from litex
    platform_module = importlib.import_module(args.platform)

    # Load the platform module and toolchain
    if args.gateware_toolchain is not None:
        platform = platform_module.Platform(toolchain=args.gateware_toolchain)
    else:
        platform = platform_module.Platform()

    # Instantiate our custom SoC
    soc = TinyLiteX(platform, **soc_core_argdict(args))

    # Set up the LiteX SoC Builder
    builder = Builder(soc, **builder_argdict(args))

    # Add our runtime code package, relative to this SoC definition
    builder.add_software_package(
        "firmware",
        src_dir=os.path.abspath(
            os.path.join(os.path.dirname(__file__), "firmware")
        )
    )

    # Kick off the build
    builder.build()


if __name__ == "__main__":
    main()
