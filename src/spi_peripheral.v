`default_nettype none

module spi_peripheral (
    input  wire       clk,
    input  wire       rst_n,      // Should be treated as asynchronous
    input  wire       sclk,
    input  wire       copi,
    input  wire       ncs,
    output reg [7:0]  reg_0x00,
    output reg [7:0]  reg_0x01,
    output reg [7:0]  reg_0x02,
    output reg [7:0]  reg_0x03,
    output reg [7:0]  reg_0x04
);

  // Synchronizers for CDC
  reg [2:0] sclk_sync, ncs_sync, copi_sync;

  // Transaction state
  reg [15:0] shift_reg;
  reg [3:0] bit_counter;

  // Use (posedge clk or negedge rst_n) to fix the SYNCASYNCNET error
  always @(posedge clk or negedge rst_n) begin
    if (!rst_n) begin
      // Reset logic
      sclk_sync <= 0;
      ncs_sync  <= 3'b111;
      copi_sync <= 0;
      reg_0x00  <= 0;
      reg_0x01  <= 0;
      reg_0x02  <= 0;
      reg_0x03  <= 0;
      reg_0x04  <= 0;
    end else begin
      // Sample inputs for CDC
      sclk_sync <= {sclk_sync[1:0], sclk};
      ncs_sync  <= {ncs_sync[1:0], ncs};
      copi_sync <= {copi_sync[1:0], copi};

      // Implement your SPI logic here using the synced signals...
    end
  end
endmodule