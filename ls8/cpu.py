"""CPU functionality."""

import sys

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.halted = False
        # holds 256 bytes of memory
        self.ram = [0] * 256
        #  and 8 general-purpose registers
        self.reg = [0, 0, 0, 0, 0, 0, 0, 0xf4]
        self.fl = 0
        self.pc = 0 

        # Operations we can perform:
        self.operations = {
            0b10100000: self.handle_ADD,
            0b00000001: self.handle_HLT,
            0b10000010: self.handle_LDI,
            0b01000111: self.handle_PRN,
            0b10100010: self.handle_MUL,
            0b01000101: self.handle_PUSH,
            0b01000110: self.handle_POP,
            0b01010000: self.handle_CALL,
            0b00010001: self.handle_RET,
            0b10100111: self.handle_CMP,
            0b01010100: self.handle_JMP,
        }

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
        elif op == "CMP":
            if self.reg[reg_a] > self.reg[reg_b]:
                value = 0b00000010
            elif self.reg[reg_a] == self.reg[reg_b]:
                value = 0b00000001
            else:
                value = 0b00000100
            self.fl = value
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """
        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            # self.fl,
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

        while self.halted is False:
            # self.trace()
            instruction = self.ram_read(self.pc)
            argument_a = self.ram_read(self.pc + 1)
            argument_b = self.ram_read(self.pc + 2)

            # shift numbers right by 6.. 
            # will translate to number of arguments required for function
            num_of_args = instruction >> 6
            # move down to next instruction
            self.pc += 1 + num_of_args

            if num_of_args == 0:
                self.operations[instruction]()
            elif num_of_args == 1:
                self.operations[instruction](argument_a)
            else:
                self.operations[instruction](argument_a, argument_b)   

    def handle_HLT(self):
        self.halted = True

    def handle_LDI(self, register_index, value):
        self.reg[register_index] = value

    def handle_PRN(self, register_index):
        print(self.reg[register_index])

    def handle_ADD(self, register_a_index, register_b_index):
        self.alu("ADD", register_a_index, register_b_index)

    def handle_MUL(self, register_a_index, register_b_index):
        self.alu("MUL", register_a_index, register_b_index)

    def handle_PUSH(self, register_index):
        # print(f'Pushing {self.reg[register_index]} to address {self.reg[7]}')
        # decrement pointer to hold different ram address
        self.reg[7] -= 1
        # write top-stack's value at address register is pointing to
        self.ram_write(self.reg[7], self.reg[register_index])
    
    def handle_POP(self, register_index):
        # value should be the address stored in the stack pointer
        value_to_pop = self.ram[self.reg[7]]
        # write current-stack pointer's value at register
        # current stack's value is a reference to an address in ram
        self.reg[register_index] = value_to_pop
        # increment pointer to hold different ram address
        self.reg[7] += 1
        # print(f'Popping last value ({value_to_pop}) into register {register_index}')

    def handle_CALL(self, register_index):
        # Calls a subroutine (function) at the address stored in the register.
        self.reg[7] -= 1

        # 1 - The address of the instruction directly after CALL is pushed onto the stack. This allows us to return to where we left off when the subroutine finishes executing.
        next_instruction_address = self.pc
        # print(f'Storing address of next instruction ({next_instruction_address}) at SP (Index {self.reg[7]} of RAM)')
        self.ram_write(self.reg[7], next_instruction_address)

        # 2 - The PC is set to the address stored in the given register. We jump to that location in RAM and execute the first instruction in the subroutine. The PC can move forward or backwards from its current location.
        self.handle_JMP(register_index)

    def handle_RET(self):
        # Return from subroutine.
        # Pop the value from the top of the stack and store it in the PC.
        value_to_pop = self.ram[self.reg[7]]
        self.pc = value_to_pop
        self.reg[7] += 1

    def handle_CMP(self, register_a_index, register_b_index): 
        self.alu("CMP", register_a_index, register_b_index)

    def handle_JMP(self, register_index):
        # Set the PC to the address stored in the given register.
        # print(f' Jumping from {self.pc}')
        self.pc = self.reg[register_index]
        # print(f' to {self.pc}')
