# SPDX-FileCopyrightText: © 2026 Leo Moser <leomoser99@gmail.com>
# SPDX-License-Identifier: Apache-2.0

import os
import math
import random
from pathlib import Path
import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles, Timer, Edge, RisingEdge, FallingEdge
from cocotb_tools.runner import get_runner
from cocotb.types import LogicArray, Logic

proj_path = Path(__file__).resolve().parent

testname = "counter"

if __name__ == "__main__":

    sim = os.getenv("SIM", "icarus")

    tile_library = os.getenv("TILE_LIBRARY", "classic")
    
    sources = []
    defines = {}
    test_filter = None
    
    tiles_path = Path(proj_path / "../.." / "ip" / "fabulous-tiles")
    primitives_path = Path(tiles_path) / "primitives"
    sources.extend([path.resolve() for path in primitives_path.glob('**/yosys/primitives/*.v')])

    tiles_path = Path(proj_path / "../.." / "ip" / "fabulous-extra")
    primitives_path = Path(tiles_path) / "primitives"
    sources.extend([path.resolve() for path in primitives_path.glob('**/yosys/primitives/*.v')])
    
    # Add counter design
    sources.append(proj_path / f'../../user_designs/designs/{tile_library}/{testname}/{testname}_synth.v')

    print(f"sources: {sources}")

    hdl_toplevel = testname

    runner = get_runner(sim)
    runner.build(
        sources=sources,
        hdl_toplevel=hdl_toplevel,
        defines=defines,
        always=True,
        clean=True,
        timescale=("1ns", "1ps"),
        waves=True,
    )

    runner.test(
        hdl_toplevel=hdl_toplevel,
        test_module="counter",
        plusargs=['-fst'],
        waves=True,
        test_filter=test_filter,
    )

@cocotb.test()
async def test_counter(dut):

    # Start a clock
    cocotb.start_soon(Clock(dut.clk1, 10, 'ns').start())
    
    # Assert reset, disable design
    dut.rst.value = 1
    dut.ena.value = 0
    
    await ClockCycles(dut.clk1, 10)
    
    # Deassert reset
    dut.rst.value = 0
    
    await ClockCycles(dut.clk1, 10)
    
    # Enable design
    dut.ena.value = 1
    
    await ClockCycles(dut.clk1, 100)
    
    # Check output
    assert (dut.c.value == 100 - 1)
