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

  // Synchronizers for Clock Domain Crossing (CDC)
  reg [2:0] sclk_sync, ncs_sync, copi_sync;
  
  // SPI State
  reg [15:0] shift_reg;
  reg [3:0] bit_count;

  // Edge Detection
  wire sclk_rising = (sclk_sync[2:1] == 2'b01);
  wire ncs_falling = (ncs_sync[2:1] == 2'b10);
  wire ncs_active  = ~ncs_sync[1];

    always @(posedge clk or negedge rst_n) begin
    if (!rst_n) begin
      sclk_sync <= 3'b0;
      ncs_sync  <= 3'b111;
      copi_sync <= 3'b0;
      shift_reg <= 16'b0;
      bit_count <= 4'b0;
      reg_0x00  <= 8'h00;
      reg_0x01  <= 8'h00;
      reg_0x02  <= 8'h00;
      reg_0x03  <= 8'h00;
      reg_0x04  <= 8'h00;
    end else begin
      // Synchronization logic
      sclk_sync <= {sclk_sync[1:0], sclk};
      ncs_sync  <= {ncs_sync[1:0], ncs};
      copi_sync <= {copi_sync[1:0], copi};

      if (ncs_falling) begin
        bit_count <= 4'b0;
        shift_reg <= 16'b0;
      end else if (ncs_active) begin
        if (sclk_rising) begin
          shift_reg <= {shift_reg[14:0], copi_sync[1]};
          bit_count <= bit_count + 4'd1;
          
          // Once we have all 16 bits (this is the 16th bit)
          if (bit_count == 4'd15) begin
             // Bit 15 of completion (first bit in) is RW. 
             // We check shift_reg[14] because bit 15 just shifted there.
             if (shift_reg[14] == 1'b1) begin 
                case (shift_reg[13:7]) // Bits 14:8 are address
                   7'h00: reg_0x00 <= {shift_reg[6:0], copi_sync[1]};
                   7'h01: reg_0x01 <= {shift_reg[6:0], copi_sync[1]};
                   7'h02: reg_0x02 <= {shift_reg[6:0], copi_sync[1]};
                   7'h03: reg_0x03 <= {shift_reg[6:0], copi_sync[1]};
                   7'h04: reg_0x04 <= {shift_reg[6:0], copi_sync[1]};
                   default: ;
                endcase
             end
          end
        end
      end
    end
  end

endmodule