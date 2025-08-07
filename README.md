# SARCASM

SARCASM is an assembly language poking fun at the x86 Assembly instruction set for having hyperspecific instructions. What better way to show this then having an infinite amount of instructions, for every single purpose!

# How do you do it?

Provided in the python file workspace.py you will see these 4 functions set up for you.

run_snippet(CATprogram)<br>
print(microinstructions_to_instruction(CATprogram))<br>
print(disassemble(CATprogram))<br>
print(instruction_to_microinstructions(microinstructions_to_instruction(CATprogram)))<br>

Run_snippet runs a series of microinstructions, microinstructions are stored in an array. 
The second function converts those microinstructions into a full instruction. 
The disassemble function prints all the microinstructions out in an assembly style for readablity and comphrensibility.
The last function decompiles an instruction into its microinstructions.

To run a file do python main.py file.asm
