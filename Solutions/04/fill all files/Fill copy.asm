// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Fill.asm

// Runs an infinite loop that listens to the keyboard input.
// When a key is pressed (any key), the program blackens the screen,
// i.e. writes "black" in every pixel;
// the screen should remain fully black as long as the key is pressed. 
// When no key is pressed, the program clears the screen, i.e. writes
// "white" in every pixel;
// the screen should remain fully clear as long as no key is pressed.



@color
M=0						//current=0 (the current screen color)

@24576
D=A						//D=24576
@last
M=D;JMP						//last=24576 (number of the last word in the screen memory map)

(LOOP)
	@SCREEN
	D=A					//D=16384 (first word in the screen map
	@i
	M=D					//i=16384

	@KBD
	D=M					//D=KBD
	@WHITE
	D;JEQ				//if KBD=0 jump to WHITE

	//BLACK
	D=-1
	@fill
	M=D					//fill=-1

	@color
	D=D-M				//D=fill-current
	@LOOP
	D;JEQ				//if fill = current jump to LOOP

	@fill				//updating the color variable to the color we're about to fill
	D=M
	@color
	M=D

	@FILL
	0;JMP				//else jump to fill screen


	(WHITE)
	D=0					
	@fill
	M=D					//fill=0
	@color
	D=D-M				//D=fill-color
	@LOOP
	D;JEQ				//if color=fill jump to LOOP (else just continue to fill screen)

	@fill				//updating the color variable to the color we're about to fill
	D=M
	@color
	M=D


	(FILL)

	//RAM[i]=fill
	@fill
	D=M
	@i
	A=M
	M=D

	@i
	M=M+1				//i++

	@last
	D=M					//D=last
	@i
	D=D-M				//D=n-i
	@LOOP
	D;JEQ				//if n=i jump to LOOP
	
	@FILL
	0;JMP