"""CPU functionality."""

import sys

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        # holds 256 bytes of memory
        self.ram = [0] * 256
        #  and 8 general-purpose registers
        self.reg = [0, 0, 0, 0, 0, 0, 0, 0xf4]
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
        self.ram[value] = address


    def load(self, fileName):
        """Load a program into memory."""

        # For now, we've just hardcoded a program:

        # program = [
        #     # From print8.ls8
        #     0b10000010, # LDI R0,8
        #     0b00000000,
        #     0b00001000,
        #     0b01000111, # PRN R0
        #     0b00000000,
        #     0b00000001, # HLT
        # ]

        try: 
            address = 0

            with open(fileName) as program:

                for line in program:
                    instruction = line.split('#')[0].strip()
                    if instruction != '':
                        self.ram[address] = int(instruction, 2)
                        address += 1
        except FileNotFoundError:
            print('File not found')
            sys.exit(2)


    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        #elif op == "SUB": etc
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

        # Operations we can perform:
        HLT = 1
        LDI = 0b10000010 # Save a value in a register
        PRN = 0b01000111

        while not halted:
            instruction = self.ram_read(self.pc)

            if instruction == HLT:
                halted = True
            elif instruction == LDI:
                reg_num = self.ram[self.pc + 1]
                value = self.ram[self.pc + 2]
                self.reg[reg_num] = value
                self.pc += 3
            elif instruction == PRN:
                reg_num = self.ram[self.pc + 1]
                print(self.reg[reg_num])
                self.pc += 2
            else:
                print('unknown instruction')


