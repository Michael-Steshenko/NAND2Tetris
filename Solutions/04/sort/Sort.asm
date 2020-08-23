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

@last
M=D-1					//last=R14-1
@R15
D=M						//D=R15
@last
M=M+D					//last=R14+R15-1

@SORT
0;JMP


(SWAP)					//swaps the biggest value found with the j value in array

	@j
	A=M					
	D=M					//D=RAM[j]
	@temp
	M=D					//temp=RAM[j]
	
	@biggest
	A=M
	D=M					//D=RAM[biggest]
	@j
	A=M
	M=D					//RAM[j]=RAM[biggest]
	
	@temp
	D=M					//D=RAM[j]
	@biggest
	A=M
	M=D					//RAM[biggest]=Ram[j]


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
		
		@SWAP
		D;JGT			//if i>last jump to SWAP		
		
		@i
		A=M				//go to the 'i' memory
		D=M				//D=RAM[i]
		
		@biggest
		A=M
		D=D-M			//D=RAM[i]-RAM[biggest]
		
		@FIND BIGGEST
		D;JLE			//if RAM[i]<=biggest jump to FIND BIGGEST
		
		
		//else: RAM[i] is biggest
		@i
		D=M				//D=i
		@biggest
		M=D				//biggest=i
		
		@FIND BIGGEST
		0;JMP
	
	
(END)
		
		
		
		
		
		
		






