// Num: number of required key bits (given in multiple of 32*Unroll)
// Input is given in little endian, output is given in big endian
module trivium_core(Key, IV, Stream, Krdy, Drdy, Dvld, Kvld, BSY, CLK, RSTn, EN);
  parameter UNROLL = 9; // Should be devisor of 36
  parameter LATENCY = 36/UNROLL;
  
  input [79:0] Key, IV;
  output [32*UNROLL-1:0] Stream;
  input [5*UNROLL-1:0] Num;

  input Drdy, CLK, RSTn, EN, Krdy;
  output reg Dvld, BSY, Kvld;

  reg [287:0] S;
  reg [79:0] Kreg;
  wire [79:0] reversedKey, reversedIV;
  reg [9:0] CNT;
  reg [5*UNROLL-1:0] Numreg;

  wire [287:0] U [0:UNROLL];
  assign U[0] = S;

  wire [32*UNROLL-1:0] Y, Z;

  genvar r;
  generate
    for (r=0;r<UNROLL;r=r+1) begin
      round32 round (.s(U[r]), .n(U[r+1]), .z(Y[32*(UNROLL-r)-1:32*(UNROLL-r-1)]));
    end
  endgenerate

  assign Z = Y&{(32*UNROLL){Dvld}};
  genvar i;
  generate
    for (i=0;i<4*UNROLL;i=i+1) begin
      assign Stream[8*(i+1)-1:8*i] = br(Z[8*(i+1)-1:8*i]);
    end
  endgenerate

 assign reversedKey = {br(Key[79:72]), br(Key[71:64]), br(Key[63:56]), br(Key[55:48]), br(Key[47:40]),
                       br(Key[39:32]), br(Key[31:24]), br(Key[23:16]), br(Key[15:8]), br(Key[7:0])};
 assign reversedIV = {br(IV[79:72]), br(IV[71:64]), br(IV[63:56]), br(IV[55:48]), br(IV[47:40]),
                      br(IV[39:32]), br(IV[31:24]), br(IV[23:16]), br(IV[15:8]), br(IV[7:0])};

  always @(posedge CLK) begin
    if (RSTn==0) begin
      S <= 0; Dvld <= 0; BSY <= 0; CNT <= 0; Numreg <= 0; Kreg <= 0; Kvld <= 0;
    end else if (EN==1) begin
      if (BSY==0) begin
        if (Krdy == 1) begin
          Kreg <= reversedKey; Kvld <= 1;
        end
        if (Kvld == 1) begin
          if (Drdy==1) begin
            S <= {3'b111, 108'b0, 4'b0, reversedIV, 13'b0, Kreg};
            BSY <= 1; Dvld <= 0; CNT <= 0; Numreg <= Num-1;
          end
        end
      end else begin
        if (Dvld==0) begin
          S <= U[UNROLL]; CNT <= CNT+1;
          if (CNT==LATENCY) begin
            Dvld <= 1; CNT <= 0;
          end
        end else begin
          if (CNT==Numreg) begin
            Dvld <= 0; BSY <= 0; CNT <= 0; Numreg <= 0; S <= 0;
          end else begin
            S <= U[UNROLL]; CNT <= CNT+1;
          end
        end
      end
    end
  end

  // Byte-wise bit reversal
  function [7:0] br;
    input [7:0] x;
    br = {x[0], x[1], x[2], x[3], x[4], x[5], x[6], x[7]};
  endfunction // br
endmodule

module round32(s, n, z);
  input [287:0] s;
  output [287:0] n;
  output [31:0] z;
  wire [31:0] t1, t2, t3, n1, n2, n3;
  wire [31:0] y;

  assign t1 = s[65:34]   ^ s[92:61];
  assign t2 = s[161:130] ^ s[176:145];
  assign t3 = s[242:211] ^ s[287:256];

  assign z = t1 ^ t2 ^ t3;

  assign n1 = t3 ^ (s[285:254]&s[286:255]) ^ s[68:37];
  assign n2 = t1 ^ (s[90:59]&s[91:60]) ^ s[170:139];
  assign n3 = t2 ^ (s[174:143]&s[175:144]) ^ s[263:232];

  assign n = {s[255:177], n3, s[144:93], n2, s[60:0], n1};
endmodule // round32


