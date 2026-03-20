<!---
This file is used to generate your project datasheet.
-->

## Overview

This project is an SPI-controlled PWM peripheral designed for the Tiny Tapeout onboarding. The design operates at **10 MHz** and uses SPI communication at **~100 KHz** to configure registers that control output enables, PWM enables, and duty cycles. The system comprises two main modules: an **SPI Peripheral** for register management and a **PWM Peripheral** for signal generation.

## How it works

### SPI Interface
* **Mode 0**: Data sampled on rising `SCLK` edge, valid on falling edge.
* **Fixed Transaction Length**: 16 clock cycles (1 R/W bit + 7 address bits + 8 data bits).
* **Clock Domain Crossing**: Synchronized using a 2-stage flip-flop chain to prevent metastability.

### Register Map
| Addr | Register | Description | Reset Value |
|----|----|----|----|
| `0x00` | `en_reg_out_7_0` | Enable outputs on `uo_out[7:0]` | `0x00` |
| `0x01` | `en_reg_out_15_8` | Enable outputs on `uio_out[7:0]` | `0x00` |
| `0x02` | `en_reg_pwm_7_0` | Enable PWM for `uo_out[7:0]` | `0x00` |
| `0x03` | `en_reg_pwm_15_8` | Enable PWM for `uio_out[7:0]` | `0x00` |
| `0x04` | `pwm_duty_cycle` | PWM Duty Cycle (`0x00`=0%, `0xFF`=100%) | `0x00` |

### PWM Peripheral
* **Frequency**: ~3 kHz (derived from 10 MHz clock).
* **Duty Cycle**: `(pwm_duty_cycle / 256) * 100%`.
* **Output Logic**: Output Enable takes precedence. If enabled and PWM mode is `0`, output is static `1`. If PWM mode is `1`, output is the PWM signal.

## How to test

The design includes a Cocotb testbench suite:
1. **SPI Verification**: Validates register writes, address decoding, and CDC synchronization.
2. **PWM Verification**: Sweeps duty cycles from `0x00` to `0xFF`, verifies the 3 kHz frequency, and tests the interaction between Enable and PWM registers.

To run tests:
```bash
cd test
make