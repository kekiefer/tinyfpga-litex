# TinyFPGA LiteX

A minimal LiteX SoC definition for the TinyFPGA. Currently, only TinyFPGA BX is supported, but more boards may be added in the future.

## Quick Start

1. Install LiteX according to the Advanced or Medium quickstart guide on [LiteX GitHub](https://github.com/enjoy-digital/litex). Note that depending on what CPU you would like to use (see Caveats below) your target compiler may be available in your system's package manager!

2. Install tinyprog, if you don't already have it

        pip3 install tinyprog

3. Clone this repository

        git clone https://github.com/kekiefer/tinyfpga-litex
        cd tinyfpga-litex

4. Build the SoC:

        python3 tinyfpga_litex.py --platform litex_boards.partner.platforms.tinyfpga_bx --cpu-type vexriscv --cpu-variant=lite

5. Program the gateware bitstream and the firmware:

        tinyprog -p soc_tinylitex_tinyfpga_bx/gateware/top.bin -u soc_tinylitex_tinyfpga_bx/software/userdata.bin

If everything works, you should see output on the UART and a flashing LED.

## Footprint `--cpu-type vexriscv --cpu-variant=lite`

    Info: Device utilisation:
    Info: 	         ICESTORM_LC:  4328/ 7680    56%
    Info: 	        ICESTORM_RAM:    32/   32   100%
    Info: 	               SB_IO:    10/  256     3%
    Info: 	               SB_GB:     8/    8   100%
    Info: 	        ICESTORM_PLL:     0/    2     0%
    Info: 	         SB_WARMBOOT:     0/    1     0%

## UART configuration

I have an FTDI serial cable that plugs directly into pins soldered to the TinyFPGA BX, so I have configured tinyfpga_bx platform definition to add the serial peripheral with the following pins:

    (
        "serial", 0,
        Subsignal("tx", Pins("GPIO:0")),
        Subsignal("rx", Pins("GPIO:1")),
        IOStandard("LVCMOS33")
    )

This could be easily reconfigured in any way that suits your application

## Caveats

I have tried (not very hard) and failed to run the picorv32 CPU and also failed to run vexriscv variants other than lite. It is probably possible to get these to work, as well as lm32 or other CPUs, as long as the footprint isn't too large.
