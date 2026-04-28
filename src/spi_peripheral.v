`default_nettype none

module spi_peripheral (
    input  wire       clk,
    input  wire       rst_n,
    input  wire       sclk,
    input  wire       copi,
    input  wire       ncs,
    output reg [7:0]  reg_0x00,
    output reg [7:0]  reg_0x01,
    output reg [7:0]  reg_0x02,
    output reg [7:0]  reg_0x03,
    output reg [7:0]  reg_0x04
);

  localparam [6:0] MAX_ADDRESS = 7'h04;

  // 2-FF synchronizers for CDC
  reg [1:0] sclk_sync, ncs_sync, copi_sync;

  // Previous-cycle synced values for edge detection (clk domain)
  reg sclk_prev, ncs_prev;

  // SPI state
  reg [15:0] shift_reg;
  reg [4:0]  bit_count;

  wire sclk_rising = sclk_sync[1] & ~sclk_prev;
  wire ncs_falling = ~ncs_sync[1] & ncs_prev;
  wire ncs_rising  =  ncs_sync[1] & ~ncs_prev;
  wire ncs_active  = ~ncs_sync[1];

  always @(posedge clk or negedge rst_n) begin
    if (!rst_n) begin
      sclk_sync <= 2'b00;
      ncs_sync  <= 2'b11;
      copi_sync <= 2'b00;
      sclk_prev <= 1'b0;
      ncs_prev  <= 1'b1;
      shift_reg <= 16'b0;
      bit_count <= 5'b0;
      reg_0x00  <= 8'h00;
      reg_0x01  <= 8'h00;
      reg_0x02  <= 8'h00;
      reg_0x03  <= 8'h00;
      reg_0x04  <= 8'h00;
    end else begin
      sclk_sync <= {sclk_sync[0], sclk};
      ncs_sync  <= {ncs_sync[0], ncs};
      copi_sync <= {copi_sync[0], copi};
      sclk_prev <= sclk_sync[1];
      ncs_prev  <= ncs_sync[1];

      if (ncs_falling) begin
        bit_count <= 5'b0;
        shift_reg <= 16'b0;
      end else if (ncs_active && sclk_rising) begin
        shift_reg <= {shift_reg[14:0], copi_sync[1]};
        if (bit_count != 5'd16) bit_count <= bit_count + 5'd1;
      end

      // Commit only on nCS rising edge after a complete 16-bit transaction
      if (ncs_rising && bit_count == 5'd16) begin
        // shift_reg[15]    = R/W (1 = write)
        // shift_reg[14:8]  = address
        // shift_reg[7:0]   = data
        if (shift_reg[15] && shift_reg[14:8] <= MAX_ADDRESS) begin
          case (shift_reg[14:8])
            7'h00: reg_0x00 <= shift_reg[7:0];
            7'h01: reg_0x01 <= shift_reg[7:0];
            7'h02: reg_0x02 <= shift_reg[7:0];
            7'h03: reg_0x03 <= shift_reg[7:0];
            7'h04: reg_0x04 <= shift_reg[7:0];
            default: ;
          endcase
        end
      end
    end
  end

endmodule
