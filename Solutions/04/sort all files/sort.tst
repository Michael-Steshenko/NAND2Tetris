output-file sort.out,
compare-to sort.cmp,
output-list RAM[35]%D2.6.2 RAM[36]%D2.6.2 RAM[37]%D2.6.2 RAM[38]%D2.6.2 RAM[39]%D2.6.2 RAM[40]%D2.6.2
			RAM[41]%D2.6.2 RAM[42]%D2.6.2 RAM[43]%D2.6.2;

set RAM[14] 35,   // Set test arguments
set RAM[15] 5,
set RAM[35] -99,   // Set test arguments
set RAM[36] 88,   // Set test arguments
set RAM[37] -77,   // Set test arguments
set RAM[38] 66,   // Set test arguments
set RAM[39] 55,   // Set test arguments
set RAM[40] 0,   // Set test arguments
set RAM[41] 0,   // Set test arguments
set RAM[42] 0,   // Set test arguments
set RAM[43] 0,   // Set test arguments
repeat 700 {
  ticktock;
}
output;