"""CPU functionality."""

import sys

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        # holds 256 bytes of memory
        self.ram = [0] * 256
        #  and 8 general-purpose registers
        self.reg = [0, 0, 0, 0, 0, 0, 0, 0]
        self.pc = 0 

    def ram_read(self, address):
        """
        Accept the address to read and return the value stored there.
        address == Memory Address Register - address that is being read or written to.
        """
        return self.ram[address]

    def ram_write(self, address, value):
        """
        Accept the value to write, and the address to write it to.
        address == Memory Data Register - data that was read or the data to write.
        value == Memory Address Register - address that is being read or written to.
        """
        self.ram[address] = value


    def load(self, fileName):
        """Load a program into memory."""
        try: 
            address = 0

            with open(fileName) as program:

                for line in program:
                    instruction = line.split('#')[0].strip()
                    # ignore blank lines
                    if instruction != '':
                        # int() converts binary strings to integer values with number base as second argument
                        self.ram[address] = int(instruction, 2)
                        address += 1

        except FileNotFoundError:
            print('File not found')
            sys.exit(2)


    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        elif op == "MUL":
            self.reg[reg_a] *= self.reg[reg_b]
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            #self.fl,
            #self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def run(self):
        """Run the CPU."""
        halted = False

        # Stack Pointer (R7) as per specs
        SP = 7
        self.reg[SP] = 0xf4

        # Operations we can perform:
        HLT = 0b00000001
        LDI = 0b10000010 # Save a value in a register
        PRN = 0b01000111
        MUL = 0b10100010
        PUSH = 0b01000101
        POP = 0b01000110 

        while not halted:
            instruction = self.ram_read(self.pc)

            if instruction == HLT:
                halted = True
            elif instruction == LDI:
                reg_index = self.ram[self.pc + 1]
                value = self.ram[self.pc + 2]
                self.reg[reg_index] = value
                op_size = 3
            elif instruction == PRN:
                reg_index = self.ram[self.pc + 1]
                print(self.reg[reg_index])
                op_size = 2
            elif instruction == MUL:
                register_a = self.ram[self.pc + 1]
                register_b = self.ram[self.pc + 2]
                self.alu("MUL", register_a, register_b)
                op_size = 3
            elif instruction == PUSH:
                reg_index = self.ram[self.pc + 1]
                val = self.reg[reg_index]
                self.reg[SP] -= 1
                self.ram[self.reg[SP]] = val
                op_size = 2
                print(f'Pushing {val} at index {reg_index} and decrementing SP to {self.reg[SP]}')
            elif instruction == POP:
                print(f'Popping off {val} at index {reg_index} and incrementing SP to {self.reg[SP]}')
                reg_index = self.ram[self.pc + 1]
                val = self.reg[SP]
                self.reg[reg_index] = val
                self.reg[SP] += 1
                op_size = 2
            else:
                print('unknown instruction')
            
            self.pc += op_size

        print(f'REGISTERS: {self.reg}')
