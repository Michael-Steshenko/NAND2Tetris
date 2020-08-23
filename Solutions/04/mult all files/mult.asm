// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Mult.asm

// Multiplies R0 and R1 and stores the result in R2.
// (R0, R1, R2 refer to RAM[0], RAM[1], and RAM[2], respectively.)

	@R2
	M=0				//initialize R2 to be 0
	
//Check which mul is bigger to add the 'big' number to itself 'small' times
	@R0
	D=M				//D=R0
	@R1
	D=D-M			//D=R0-R1

	@R0BIGGER
	D;JGT			//if R0 is bigger than R1 jump to R0BIGGER


//else R1 is bigger
	@R1
	D=M
	@big
	M=D				//big=R1

	@R0
	D=M
	@small
	M=D				//small=R0

	@ADD			
	0;JMP			//jump to addition


(R0BIGGER)
	@R0
	D=M
	@big
	M=D				//big=R0

	@R1
	D=M
	@small
	M=D				//small=R1


(ADD)
	@small
	D=M				//D=small
	@LOOP ADDITION
	D;JGT			//if small>0 add big to R2
	
	@END
	0;JMP
	
	(LOOP ADDITION)
		@small
		M=M-1		//small--
		@big
		D=M			//D=big
		@R2
		M=M+D		//R2=R2+big
		@ADD		//jump to ADD
		0;JMP
	
(END)