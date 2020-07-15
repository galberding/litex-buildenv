#!/usr/bin/env python3
# Support for the Digilent Atlys board - digilentinc.com/atlys/
from migen import *

from litex.soc.integration.soc_sdram import *
from litex.soc.integration.builder import *
from litex.soc.interconnect import wishbone

#from litedram.modules import MT46H64M16 #MT46H32M16
from litedram.phy import s6ddrphy
from litedram.core import ControllerSettings

#from litescope import LiteScopeAnalyzer

#from gateware import cas
from gateware import info
from gateware import spi_flash

from targets.utils import dict_set_max, define_flash_constants, period_ns
from .crg import _CRG

from litex.soc.cores import uart

class BaseSoC(SoCSDRAM):
    mem_map = {**SoCSDRAM.mem_map, **{
        'spiflash': 0x20000000,
    }}

    def __init__(self, platform, **kwargs):
        dict_set_max(kwargs, 'integrated_rom_size', 0x8000)
        dict_set_max(kwargs, 'integrated_sram_size', 0x8000)
        #kwargs['uart_name']="stub" #stub
        #kwargs['with_uart'] = False
        sys_clk_freq = 50*1000000
        # SoCSDRAM ---------------------------------------------------------------------------------
        SoCSDRAM.__init__(self, platform, clk_freq=sys_clk_freq, **kwargs)
        self.submodules.uartbone  = uart.UARTWishboneBridge(
                pads     = self.platform.request("serial"),
                clk_freq = self.sys_clk_freq,
                baudrate = 115200)
        self.bus.add_master(name="uartbone", master=self.uartbone.wishbone)
        # CRG --------------------------------------------------------------------------------------
        self.submodules.crg = _CRG(platform, sys_clk_freq)
        
        self.platform.add_period_constraint(self.crg.cd_sys.clk, 1e9/sys_clk_freq)

        #self.submodules.uartbone  = uart.UARTWishboneBridge(
        #        pads     = self.platform.request("serial"),
        #        clk_freq = self.sys_clk_freq,
        #        baudrate = 115200)
        #self.bus.add_master(name="uartbone", master=self.uartbone.wishbone)


        # DDR2 SDRAM -------------------------------------------------------------------------------
        #if True:
        #    sdram_module = MT46H64M16(50*1000000, "1:2") #P3R1GE4JGF  MT46H64M16
        #    self.submodules.ddrphy = s6ddrphy.S6HalfRateDDRPHY(
        #        platform.request("ddram"),
        #        memtype      = sdram_module.memtype,
        #        rd_bitslip   = 0, #0 1
        #        wr_bitslip   = 4, #4 3
        #        dqs_ddr_alignment="C0") #C0 C1
        #    self.add_csr("ddrphy")
        #    controller_settings = ControllerSettings(
        #        with_bandwidth=True)
        #    self.register_sdram(
        #        self.ddrphy,
        #        geom_settings   = sdram_module.geom_settings,
        #        timing_settings = sdram_module.timing_settings,
        #        controller_settings=controller_settings)
        #    print(sdram_module.timing_settings.__dict__)
        ##    print(sdram_module.geom_settings.__dict__)
        #    self.comb += [
        #        self.ddrphy.clk4x_wr_strb.eq(self.crg.clk4x_wr_strb),
        #        self.ddrphy.clk4x_rd_strb.eq(self.crg.clk4x_rd_strb),
        #    ]
        # Basic peripherals ------------------------------------------------------------------------
        # info module
        self.submodules.info = info.Info(platform, self.__class__.__name__)
        self.add_csr("info")
        # control and status module
        #self.submodules.cas = cas.ControlAndStatus(platform, sys_clk_freq)
        self.add_csr("cas")

        # Add debug interface if the CPU has one ---------------------------------------------------
        #if hasattr(self.cpu, "debug_bus"):
        #self.register_mem(
        #    name="vexriscv_debug",
        #    address=0xf00f0000,
        #    interface=self.cpu.debug_bus, #debug_bus,
        #    size=0x100)
    
        #analyzer_signals = [
        #    #self.ddrphy.sys_clk,
        #    #platform.lookup_request("ddram").a,
        #    platform.lookup_request("ddram").ba
        #    platform.lookup_request("ddram").ras_n,
        #    platform.lookup_request("ddram").cas_n,
        #    platform.lookup_request("ddram").we_n,
        #    platform.lookup_request("ddram").cs_n,
        #     platform.lookup_request("ddram").cke,
            #self.cpu.ibus.stb,
        #    self.cpu.ibus.cyc
        #]    
        #self.submodules.analyzer = LiteScopeAnalyzer(analyzer_signals,
        #    depth        = 4096, # 512
        #    clock_domain = "sys",
        #    csr_csv      = "analyzer.csv")
        #self.add_csr("analyzer")
        # Memory mapped SPI Flash ------------------------------------------------------------------
        #self.submodules.spiflash = spi_flash.SpiFlash(
        #    platform.request("spiflash"),
        #    dummy=platform.spiflash_read_dummy_bits,
        #    div=platform.spiflash_clock_div,
        #    endianness=self.cpu.endianness)
        #self.add_csr("spiflash")
        #self.add_constant("SPIFLASH_PAGE_SIZE", platform.spiflash_page_size)
        #self.add_constant("SPIFLASH_SECTOR_SIZE", platform.spiflash_sector_size)
        #self.add_constant("SPIFLASH_TOTAL_SIZE", platform.spiflash_total_size)
        #self.add_wb_slave(
        #    self.mem_map["spiflash"],
        #    self.spiflash.bus,
        #    platform.spiflash_total_size)
        #self.add_memory_region(
        #    "spiflash",
        #    self.mem_map["spiflash"],
        #    platform.spiflash_total_size)

        bios_size = 0x8000
        #self.flash_boot_address = self.mem_map["spiflash"]+platform.gateware_size+bios_size
        #define_flash_constants(self)


SoC = BaseSoC
