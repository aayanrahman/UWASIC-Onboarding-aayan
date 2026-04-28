# SPDX-FileCopyrightText: © 2024 Tiny Tapeout
# SPDX-License-Identifier: Apache-2.0

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge
from cocotb.triggers import ClockCycles
from cocotb.types import Logic
from cocotb.types import LogicArray

async def await_half_sclk(dut):
    """Wait for the SCLK signal to go high or low."""
    start_time = cocotb.utils.get_sim_time(units="ns")
    while True:
        await ClockCycles(dut.clk, 1)
        # Wait for half of the SCLK period (10 us)
        if (start_time + 100*100*0.5) < cocotb.utils.get_sim_time(units="ns"):
            break
    return

def ui_in_logicarray(ncs, bit, sclk):
    """Setup the ui_in value as a LogicArray."""
    return LogicArray(f"00000{ncs}{bit}{sclk}")

async def send_spi_transaction(dut, r_w, address, data):
    """
    Send an SPI transaction with format:
    - 1 bit for Read/Write
    - 7 bits for address
    - 8 bits for data
    
    Parameters:
    - r_w: boolean, True for write, False for read
    - address: int, 7-bit address (0-127)
    - data: LogicArray or int, 8-bit data
    """
    # Convert data to int if it's a LogicArray
    if isinstance(data, LogicArray):
        data_int = int(data)
    else:
        data_int = data
    # Validate inputs
    if address < 0 or address > 127:
        raise ValueError("Address must be 7-bit (0-127)")
    if data_int < 0 or data_int > 255:
        raise ValueError("Data must be 8-bit (0-255)")
    # Combine RW and address into first byte
    first_byte = (int(r_w) << 7) | address
    # Start transaction - pull CS low
    sclk = 0
    ncs = 0
    bit = 0
    # Set initial state with CS low
    dut.ui_in.value = ui_in_logicarray(ncs, bit, sclk)
    await ClockCycles(dut.clk, 1)
    # Send first byte (RW + Address)
    for i in range(8):
        bit = (first_byte >> (7-i)) & 0x1
        # SCLK low, set COPI
        sclk = 0
        dut.ui_in.value = ui_in_logicarray(ncs, bit, sclk)
        await await_half_sclk(dut)
        # SCLK high, keep COPI
        sclk = 1
        dut.ui_in.value = ui_in_logicarray(ncs, bit, sclk)
        await await_half_sclk(dut)
    # Send second byte (Data)
    for i in range(8):
        bit = (data_int >> (7-i)) & 0x1
        # SCLK low, set COPI
        sclk = 0
        dut.ui_in.value = ui_in_logicarray(ncs, bit, sclk)
        await await_half_sclk(dut)
        # SCLK high, keep COPI
        sclk = 1
        dut.ui_in.value = ui_in_logicarray(ncs, bit, sclk)
        await await_half_sclk(dut)
    # End transaction - return CS high
    sclk = 0
    ncs = 1
    bit = 0
    dut.ui_in.value = ui_in_logicarray(ncs, bit, sclk)
    await ClockCycles(dut.clk, 600)
    return ui_in_logicarray(ncs, bit, sclk)

@cocotb.test()
async def test_spi(dut):
    dut._log.info("Start SPI test")

    # Set the clock period to 100 ns (10 MHz)
    clock = Clock(dut.clk, 100, units="ns")
    cocotb.start_soon(clock.start())

    # Reset
    dut._log.info("Reset")
    dut.ena.value = 1
    ncs = 1
    bit = 0
    sclk = 0
    dut.ui_in.value = ui_in_logicarray(ncs, bit, sclk)
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 5)
    dut.rst_n.value = 1
    await ClockCycles(dut.clk, 5)

    dut._log.info("Test project behavior")
    dut._log.info("Write transaction, address 0x00, data 0xF0")
    ui_in_val = await send_spi_transaction(dut, 1, 0x00, 0xF0)  # Write transaction
    assert dut.uo_out.value == 0xF0, f"Expected 0xF0, got {dut.uo_out.value}"
    await ClockCycles(dut.clk, 1000) 

    dut._log.info("Write transaction, address 0x01, data 0xCC")
    ui_in_val = await send_spi_transaction(dut, 1, 0x01, 0xCC)  # Write transaction
    assert dut.uio_out.value == 0xCC, f"Expected 0xCC, got {dut.uio_out.value}"
    await ClockCycles(dut.clk, 100)

    dut._log.info("Write transaction, address 0x30 (invalid), data 0xAA")
    ui_in_val = await send_spi_transaction(dut, 1, 0x30, 0xAA)
    await ClockCycles(dut.clk, 100)

    dut._log.info("Read transaction (invalid), address 0x00, data 0xBE")
    ui_in_val = await send_spi_transaction(dut, 0, 0x30, 0xBE)
    assert dut.uo_out.value == 0xF0, f"Expected 0xF0, got {dut.uo_out.value}"
    await ClockCycles(dut.clk, 100)
    
    dut._log.info("Read transaction (invalid), address 0x41 (invalid), data 0xEF")
    ui_in_val = await send_spi_transaction(dut, 0, 0x41, 0xEF)
    await ClockCycles(dut.clk, 100)

    dut._log.info("Write transaction, address 0x02, data 0xFF")
    ui_in_val = await send_spi_transaction(dut, 1, 0x02, 0xFF)  # Write transaction
    await ClockCycles(dut.clk, 100)

    dut._log.info("Write transaction, address 0x04, data 0xCF")
    ui_in_val = await send_spi_transaction(dut, 1, 0x04, 0xCF)  # Write transaction
    await ClockCycles(dut.clk, 30000)

    dut._log.info("Write transaction, address 0x04, data 0xFF")
    ui_in_val = await send_spi_transaction(dut, 1, 0x04, 0xFF)  # Write transaction
    await ClockCycles(dut.clk, 30000)

    dut._log.info("Write transaction, address 0x04, data 0x00")
    ui_in_val = await send_spi_transaction(dut, 1, 0x04, 0x00)  # Write transaction
    await ClockCycles(dut.clk, 30000)

    dut._log.info("Write transaction, address 0x04, data 0x01")
    ui_in_val = await send_spi_transaction(dut, 1, 0x04, 0x01)  # Write transaction
    await ClockCycles(dut.clk, 30000)

    dut._log.info("SPI test completed successfully")

async def reset_dut(dut):
    """Bring the DUT into a clean reset state."""
    dut.ena.value = 1
    dut.ui_in.value = ui_in_logicarray(1, 0, 0)  # ncs=1, bit=0, sclk=0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 5)
    dut.rst_n.value = 1
    await ClockCycles(dut.clk, 5)


async def configure_pwm_bit0(dut):
    """Enable output and PWM on uo_out[0] only."""
    await send_spi_transaction(dut, 1, 0x00, 0x01)  # en_reg_out_7_0  = bit 0
    await send_spi_transaction(dut, 1, 0x01, 0x00)  # en_reg_out_15_8 = 0
    await send_spi_transaction(dut, 1, 0x02, 0x01)  # en_reg_pwm_7_0  = bit 0
    await send_spi_transaction(dut, 1, 0x03, 0x00)  # en_reg_pwm_15_8 = 0


async def wait_for_rising(dut, timeout_cycles=500_000):
    """Wait for uo_out[0] to transition 0 -> 1. Returns sim time in ns."""
    prev = int(dut.uo_out.value) & 0x1
    for _ in range(timeout_cycles):
        await RisingEdge(dut.clk)
        cur = int(dut.uo_out.value) & 0x1
        if prev == 0 and cur == 1:
            return cocotb.utils.get_sim_time(units="ns")
        prev = cur
    return None


async def wait_for_falling(dut, timeout_cycles=500_000):
    """Wait for uo_out[0] to transition 1 -> 0. Returns sim time in ns."""
    prev = int(dut.uo_out.value) & 0x1
    for _ in range(timeout_cycles):
        await RisingEdge(dut.clk)
        cur = int(dut.uo_out.value) & 0x1
        if prev == 1 and cur == 0:
            return cocotb.utils.get_sim_time(units="ns")
        prev = cur
    return None


@cocotb.test()
async def test_pwm_freq(dut):
    dut._log.info("Start PWM frequency test")

    clock = Clock(dut.clk, 100, units="ns")  # 10 MHz
    cocotb.start_soon(clock.start())

    await reset_dut(dut)
    await configure_pwm_bit0(dut)

    # Use mid-range duty so we get clean rising edges to measure.
    await send_spi_transaction(dut, 1, 0x04, 0x80)
    await ClockCycles(dut.clk, 5000)

    t1 = await wait_for_rising(dut)
    assert t1 is not None, "No first rising edge on uo_out[0]"
    t2 = await wait_for_rising(dut)
    assert t2 is not None, "No second rising edge on uo_out[0]"

    period_ns = t2 - t1
    freq_hz = 1e9 / period_ns
    dut._log.info(f"PWM period = {period_ns} ns, frequency = {freq_hz:.2f} Hz")

    # 3 kHz ±1% -> 2970..3030 Hz
    assert 2970.0 <= freq_hz <= 3030.0, \
        f"PWM frequency {freq_hz:.2f} Hz outside 2970-3030 Hz tolerance"

    dut._log.info("PWM Frequency test completed successfully")


async def measure_duty_cycle(dut, duty_value):
    """Program the duty register and return measured duty cycle in percent."""
    await send_spi_transaction(dut, 1, 0x04, duty_value)
    # Allow at least one full PWM period for the new duty to take effect.
    await ClockCycles(dut.clk, 5000)

    # 0% — signal must stay low across more than one PWM period.
    if duty_value == 0x00:
        for _ in range(40_000):  # 4 ms > 1 PWM period (~333 us)
            await RisingEdge(dut.clk)
            assert (int(dut.uo_out.value) & 0x1) == 0, \
                "uo_out[0] went high while duty=0x00"
        return 0.0

    # 100% — signal must stay high across more than one PWM period.
    if duty_value == 0xFF:
        for _ in range(40_000):
            await RisingEdge(dut.clk)
            assert (int(dut.uo_out.value) & 0x1) == 1, \
                "uo_out[0] went low while duty=0xFF"
        return 100.0

    # General case: rising -> falling -> next rising.
    t_rise = await wait_for_rising(dut)
    assert t_rise is not None, f"No rising edge for duty=0x{duty_value:02X}"
    t_fall = await wait_for_falling(dut)
    assert t_fall is not None, f"No falling edge for duty=0x{duty_value:02X}"
    t_next = await wait_for_rising(dut)
    assert t_next is not None, f"No second rising edge for duty=0x{duty_value:02X}"

    period_ns = t_next - t_rise
    high_ns   = t_fall - t_rise
    return (high_ns / period_ns) * 100.0


@cocotb.test()
async def test_pwm_duty(dut):
    dut._log.info("Start PWM duty cycle test")

    clock = Clock(dut.clk, 100, units="ns")
    cocotb.start_soon(clock.start())

    await reset_dut(dut)
    await configure_pwm_bit0(dut)

    # 0% duty
    duty = await measure_duty_cycle(dut, 0x00)
    dut._log.info(f"duty=0x00 measured {duty:.2f}%")
    assert duty == 0.0, f"Expected 0%, got {duty:.2f}%"

    # 50% duty (0x80 / 256 = 50%)
    duty = await measure_duty_cycle(dut, 0x80)
    dut._log.info(f"duty=0x80 measured {duty:.2f}%")
    assert abs(duty - 50.0) <= 1.0, f"Expected ~50%, got {duty:.2f}%"

    # 100% duty
    duty = await measure_duty_cycle(dut, 0xFF)
    dut._log.info(f"duty=0xFF measured {duty:.2f}%")
    assert duty == 100.0, f"Expected 100%, got {duty:.2f}%"

    dut._log.info("PWM Duty Cycle test completed successfully")
