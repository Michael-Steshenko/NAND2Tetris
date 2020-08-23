// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Sort.asm

//The program input will be at R13,R14 while the result R13/R14 will be stored at R15.
//discarding the remainder
//assumes both numbers are positive.

@quotient
M=0
@remainder
M=0					//initializing quotient and remainder to 0

@R13
D=M
@dividend
M=D					//dividend=R13

@R14
D=M
@divisor
M=D					//divisor=R14

@16
D=A					//D=16
@i
M=D					//initializing i to be the number of bits in a word

(LOOP)
	@i
	M=M-1			//i--
	
	D=M				//D=i
	@END
	D;JLT			//i goes from 15 to 0, if i<0 jump to END
	
	@remainder
	M=M<<			//remainder<<
	@compare
	M=1				//compare=1 a number used to determine the i bit 
	
	@i
	D=M
	@j
	M=D				//j=i
	
	@SET REMAINDER
	0;JMP
	
	(CHECK REMAINDER)

		@R14
		D=M			//D=divisor
		@remainder
		D=M-D		//D=remainder-divisor
		
		@LOOP		//if remainder<divisor jump to LOOP
		D;JLT
		//else code:
		
		@remainder
		M=D			//remainder=remainder-divisor
		
		@compare
		D=M			
		@quotient
		M=M+D		//quotient=quotient+compare (compare has 1 in the i bit, 0 elsewhere)
					//so this makes quotient[i]=1
		
		@LOOP
		0;JMP

	(SET REMAINDER)
	//finding a number 'compare' such that compare&dividend=0 <==> dividend[i]=0 
		
		@j
		D=M				//D=j
		
		@AND
		D;JEQ			//if j=0 jump to AND ('dividend' and 'compare')
		
		@compare
		M=M<<			//shift left compare (do it i times)
		
		@j
		M=M-1			//j=j-1
		
		@SET REMAINDER
		0;JMP		
		
		
	
	(AND)
	//find the the 'i' bit of dividend
	
		@compare
		D=M				//D=compare
		@dividend
		
		D=D&M			//D=compare&dividend
			
		@CHECK REMAINDER		
		D;JEQ			//if D (the i bit) equals to 0, nothing to change
						//remainder[i]=0, it is already 0 because remainder shifted left
		//else code:
		@remainder		//remainder[0]=1
		M=M+1			//remainder=remainder+1 this sets remainder LSB from 0 to 1
		
		@CHECK REMAINDER
		0;JMP
		
(END)
@quotient
D=M
@R15
M=D			//R15=quotient		
			
	