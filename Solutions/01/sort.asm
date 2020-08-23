// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Sort.asm

// Sorts an array from large to small
// the first index of the array is stored at R14
// the length of the array is stored in R15

// Selection sort implementation:

@R14
D=M						//D=R14
@j
M=D-1					//j=R14-1

@j
M=D						//last=R14-1
@R15
D=M						//D=R15
@last
M=M+D					//last=R14+R15-1

D=M-1					//D=last-1
@beforeLast
M=D						//beforeLast=last-1


(SORT)
	@j
	M=M+1				//j=j+1
	D=M					//D=j
	@last
	D=D-M				//D=j-last
	@END
	D;JEQ				//if j=last (j>last-1) jump to end
	
	@j
	D=M					//D=j
	@biggest
	M=D					//biggest=j
	
	@j
	D=M					//D=j
	@i
	M=D					//i=j
	
	(FIND BIGGEST)
		@i
		M=M+1			//i=i+1
		
		D=M				//D=i
		@last
		D=D-M			//D=i-last
		@SORT
		D;JGT			//if i>last jump to SORT		
		
		@i
		A=M				//go to the 'i' memory
		D=M				//D=RAM[i]
		
		@biggest
		D=D-M			//D=RAM[i]-biggest
		
		@FIND BIGGEST
		D;JLE			//if RAM[i]<=biggest jump to FIND BIGGEST
		
		
		//else: RAM[i] is biggest
		@i
		A=M
		D=M				//D=RAM[i]
		@biggest
		M=D				//biggest=RAM[i]
		
		@FIND BIGGEST
		0;JMP
	
	
(END)
		
		
		
		
		
		
		






