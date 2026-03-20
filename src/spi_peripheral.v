`default_nettype none

module spi_peripheral (
    input  wire       clk,
    input  wire       rst_n,
    input  wire       sclk,
    input  wire       copi,
    input  wire       ncs,
    output reg [7:0] reg_0x00,
    output reg [7:0] reg_0x01,
    output reg [7:0] reg_0x02,
    output reg [7:0] reg_0x03,
    output reg [7:0] reg_0x04
);

  // --- Clock Domain Crossing (CDC) Synchronization ---
  // You need to synchronize ncs, sclk, and copi to the 'clk' domain 
  // using a 2-stage flip-flop chain to avoid metastability.
  
  // --- Edge Detection ---
  // Detect the falling edge of ncs and rising edge of sclk in the 'clk' domain.

  // --- SPI State Machine / Shift Register ---
  // 1. On ncs falling edge, start a transaction.
  // 2. On sclk rising edge, shift in 16 bits (RW bit + 7 Address bits + 8 Data bits).
  // 3. When 16 bits are received, if RW == 1, write 'data' to the 'address'.

  // Example register update logic:
  always @(posedge clk) begin
    if (!rst_n) begin
      reg_0x00 <= 8'h00;
      reg_0x01 <= 8'h00;
      reg_0x02 <= 8'h00;
      reg_0x03 <= 8'h00;
      reg_0x04 <= 8'h00;
    end else begin
      // Transaction logic goes here...
    end
  end

endmodule