// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/mult/Mult.tst

load Divide.asm,
output-file Divide.out,
compare-to Divide.cmp,
output-list RAM[13]%D2.6.2 RAM[14]%D2.6.2 RAM[15]%D2.6.2;

set RAM[13] 12,   // Set test arguments
set RAM[14] 4,
set RAM[15] 3;  // Test that program initialized product to 0
repeat 20 {
  ticktock;
}
set RAM[13] 12,   // Restore arguments in case program used them as loop counter
set RAM[14] 4,
output;

set PC 0,
set RAM[13] 1,   // Set test arguments
set RAM[14] 1,
set RAM[15] 1;  // Ensure that program initialized product to 0
repeat 50 {
  ticktock;
}
set RAM[13] 1,   // Restore arguments in case program used them as loop counter
set RAM[14] 1,
output;

set PC 0,
set RAM[13] 7,   // Set test arguments
set RAM[14] 2,
set RAM[15] 3;  // Ensure that program initialized product to 0
repeat 80 {
  ticktock;
}
set RAM[13] 7,   // Restore arguments in case program used them as loop counter
set RAM[14] 2,
output;

set PC 0,
set RAM[13] 3,   // Set test arguments
set RAM[14] 1,
set RAM[15] 3;  // Ensure that program initialized product to 0
repeat 120 {
  ticktock;
}
set RAM[13] 3,   // Restore arguments in case program used them as loop counter
set RAM[14] 1,
output;

set PC 0,
set RAM[13] 20,   // Set test arguments
set RAM[14] 4,
set RAM[15] 5;  // Ensure that program initialized product to 0
repeat 150 {
  ticktock;
}
set RAM[13] 20,   // Restore arguments in case program used them as loop counter
set RAM[14] 4,
output;

set PC 0,
set RAM[13] 42,   // Set test arguments
set RAM[14] 7,
set RAM[15] 6;  // Ensure that program initialized product to 0
repeat 210 {
  ticktock;
}
set RAM[13] 42,   // Restore arguments in case program used them as loop counter
set RAM[14] 7,
output;
