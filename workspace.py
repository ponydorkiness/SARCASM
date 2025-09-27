import array
import sys

def disassemble(opcodes):
    mnemonics = {
        1:  "INC PTR1",                 # pointerOne += 1
        2:  "INC PTR2",                 # pointerTwo += 1
        3:  "MOV PTR1, ACC",            # pointerOne = accumulator
        4:  "MOV PTR2, ACC",            # pointerTwo = accumulator
        5:  "MOV PTR1, $PTR1",          # pointerOne = memory[pointerOne]
        6:  "MOV PTR2, $PTR1",          # pointerTwo = memory[pointerOne]
        7:  "MOV $PTR1, $PTR2",         # memory[pointerOne] = memory[pointerTwo]
        8:  "MOV $PTR2, $PTR1",         # memory[pointerTwo] = memory[pointerOne]
        9:  "SWAP $PTR1, $PTR2",        # swap memory[pointerOne], memory[pointerTwo]
        10: "CLR $PTR1",                 # memory[pointerOne] = 0
        11: "CLR $PTR2",                 # memory[pointerTwo] = 0
        12: "ADD ACC, REGA",             # accumulator += registerA
        13: "SUB ACC, REGA",             # accumulator -= registerA
        14: "MUL ACC, REGA",             # accumulator *= registerA
        15: "DIV ACC, REGA",             # accumulator //= registerA
        16: "MOV ACC, REGA",             # accumulator = registerA
        17: "SQR ACC",                   # accumulator = accumulator^2
        18: "MOV REGA, $PTR1",           # registerA = memory[pointerOne]
        19: "MOV REGA, $PTR2",           # registerA = memory[pointerTwo]
        20: "JMP $PTR1, CF",           # jump backwards by $PTR1 if checkflag is 0 jump fowards by $PTR1 if checkflag is 1 
        21: "INC $PTR1",                 # memory[pointerOne] += 1
        22: "INC $PTR2",                 # memory[pointerTwo] += 1
        23: "DEC $PTR1",                 # memory[pointerOne] -= 1
        24: "DEC $PTR2",                 # memory[pointerTwo] -= 1
        25: "JMP ADD PC, ACC",           # program counter += accumulator
        26: "JMP SUB PC, ACC",           # program counter -= accumulator
        27: "MOV $PTR1, ACC",            # memory[pointerOne] = accumulator
        28: "MOV $PTR2, ACC",            # memory[pointerTwo] = accumulator
        29: "IN $PTR1",                  # input char to memory[pointerOne]
        30: "OUT $PTR1",                 # output char from memory[pointerOne]
        31: "CMP EQ ACC, REGA",          # checkFlag = (acc == registerA) ? 1 : 0
        32: "CMP LT ACC, REGA",          # checkFlag = (acc < registerA) ? 1 : 0
        33: "MOV ACC, FLAG",             # accumulator = checkFlag
        34: "NOT FLAG",                   # checkFlag = 1 - checkFlag
        35: "TOGGLE ENCHANT",            # Toggle enchantment on memory[pointerOne]
        36: "NOP"
    }
    
    lines = []
    for addr, code in enumerate(opcodes):
        instr = mnemonics.get(code, f"UNKNOWN_{code}")
        lines.append(f"{addr:04X}: {instr}")
    return "\n".join(lines)

if sys.platform.startswith('win'):
    import msvcrt
    def getch():
        return msvcrt.getch().decode('utf-8', errors='ignore')
else:
    import tty
    import termios

    def getch():
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch

class UInt16:
    def __init__(self, value, enchanted=False):
        self.value = value & 0xFFFF  # Force 16-bit range
        self.enchanted = enchanted

    def __int__(self):
        return self.value

    # Arithmetic operations
    def __add__(self, other):
        return UInt16(self.value + int(other), self.enchanted)

    def __sub__(self, other):
        return UInt16(self.value - int(other), self.enchanted)

    def __mul__(self, other):
        return UInt16(self.value * int(other), self.enchanted)

    def __floordiv__(self, other):
        return UInt16(self.value // int(other), self.enchanted)

    def __pow__(self, power, modulo=None):
        return UInt16(pow(self.value, int(power), 0x10000), self.enchanted)

    # In-place variants
    def __iadd__(self, other):
        self.value = (self.value + int(other)) & 0xFFFF
        return self

    def __isub__(self, other):
        self.value = (self.value - int(other)) & 0xFFFF
        return self

    def __imul__(self, other):
        self.value = (self.value * int(other)) & 0xFFFF
        return self

    def __ifloordiv__(self, other):
        self.value = (self.value // int(other)) & 0xFFFF
        return self

    # Comparisons
    def __eq__(self, other):
        return self.value == int(other)

    def __lt__(self, other):
        return self.value < int(other)

    def __le__(self, other):
        return self.value <= int(other)

    def __gt__(self, other):
        return self.value > int(other)

    def __ge__(self, other):
        return self.value >= int(other)

    # String representation
    def __repr__(self):
        return f"{self.value}{'*' if self.enchanted else ''}"

    def __str__(self):
        return f"{self.value}{'*' if self.enchanted else ''}"

    def clone(self):
        return UInt16(self.value, self.enchanted)

class UInt16Array:
    def __init__(self, size):
        self.max_value = 2**16
        self.data = [UInt16(0) for _ in range(size)]

    def __getitem__(self, index):
        return self.data[index]

    def __setitem__(self, index, value):
        if isinstance(value, UInt16):
            self.data[index] = value
        else:
            self.data[index] = UInt16(value)

    def __len__(self):
        return len(self.data)

    def snapshot(self):
        return [cell.clone() for cell in self.data]

    def restore_with_enchantments(self, snapshot):
        for i, snap in enumerate(snapshot):
            if snap.enchanted:
                # keep modified value, drop enchant flag
                self.data[i].enchanted = False
            else:
                # revert unenchanted cells
                self.data[i] = snap.clone()

def shuffle(n):
    # Swap even and odd:
    if n % 2 == 0:
        n = n + 1
    else:
        n = n - 1
    
    # Then swap mod3 pairs on the new n:
    r = n % 3
    base = n - r
    if r == 0:
        return base + 2
    elif r == 2:
        return base + 0
    else:
        return n

def fetch(s: str) -> int:
    filtered = ''.join(ch.lower() for ch in s if ch.isalpha())
    result = 0
    for ch in filtered:
        digit = ord(ch) - ord('a') + 1  # 1-26 instead of 0-25
        result = result * 26 + digit
    return result

def to_base_n_1_indexed(num, base):
    if num <= 0:
        raise ValueError("Number must be positive")

    digits = []
    n = num
    while n > 0:
        remainder = (n - 1) % base + 1  # digits 1..N
        digits.append(remainder)
        n = (n - 1) // base
    digits.reverse()
    return digits

def microinstructions_to_instruction(digits, base=36):
    # Step 1: digits -> number
    num = 0
    for d in digits:
        if d < 1 or d > base:
            raise ValueError(f"Digit {d} out of range for base {base}")
        num = num * base + d
    
    # Step 2: Undo the +1 added after shuffle
    num -= 1
    
    # Step 3: Undo shuffle
    r = num % 3
    base_val = num - r

    if r == 2:
        m = base_val + 0
    elif r == 0:
        m = base_val + 2
    else:
        m = num

    if m % 2 == 0:
        original_num = m + 1
    else:
        original_num = m - 1

    # Step 4: Convert number back to string
    # Inverse of fetch: number to letters (a=1,...z=26)
    letters = []
    n = original_num
    while n > 0:
        n, remainder = divmod(n - 1, 26)
        letters.append(chr(ord('a') + remainder))
    letters.reverse()
    return ''.join(letters)

def instruction_to_microinstructions(word):
    wordz = fetch(word)
    wordz = shuffle(wordz)
    base = 36
    wordz += 1
    array = to_base_n_1_indexed(wordz, base)
    return array

def restore_register_with_enchantment(reg, snap):
    if not reg.enchanted:
        return snap.clone()
    return UInt16(int(reg), enchanted=False)  # keep the enchanted value

def run_snippet(array):
    memory = UInt16Array(65536)

    pc = 0
    pointerOne = UInt16(0)
    pointerTwo = UInt16(0)
    accumulator = UInt16(0)
    registerA = UInt16(0)
    checkFlag = UInt16(0)
     
    overheadPC = 0

    Input = True
    Output =  True

    snapshot = {
        "memory": memory.snapshot(),
        "pointerOne": pointerOne.clone(),
        "pointerTwo": pointerTwo.clone(),
        "accumulator": accumulator.clone(),
        "registerA": registerA.clone(),
        "checkFlag": checkFlag.clone(),
    }
    while pc < len(array):
        if pc >= 0:
            opcode = array[pc]

            if opcode == 1:  # Increment pointer1
                pointerOne += UInt16(1)
            elif opcode == 2:  # Increment pointer2
                pointerTwo += UInt16(1)
            elif opcode == 3:  # Set pointerOne to accumulator
                pointerOne = accumulator.clone()
            elif opcode == 4:  # Set pointerTwo to accumulator
                pointerTwo = accumulator.clone()
            elif opcode == 5:  # Set pointerOne to the memory addr it is pointing at
                pointerOne = memory[int(pointerOne)].clone()
            elif opcode == 6:  # Set pointerTwo to the memory addr it is pointing at
                pointerTwo = memory[int(pointerOne)].clone()
            elif opcode == 7:  # Set pointerOne addr to pointerTwo addr
                memory[int(pointerOne)] = memory[int(pointerTwo)].clone()
            elif opcode == 8:  # Set pointerTwo addr to pointerOne addr
                memory[int(pointerTwo)] = memory[int(pointerOne)].clone()
            elif opcode == 9:  # Swap values
                memory[int(pointerOne)], memory[int(pointerTwo)] = memory[int(pointerTwo)].clone(), memory[int(pointerOne)].clone()
            elif opcode == 10:
                memory[int(pointerOne)] = UInt16(0)
            elif opcode == 11:
                memory[int(pointerTwo)] = UInt16(0)
            elif opcode == 12:
                accumulator += registerA.clone()
            elif opcode == 13:
                accumulator -= registerA.clone()
            elif opcode == 14:
                accumulator *= registerA.clone()
            elif opcode == 15:
                accumulator //= registerA.clone()
            elif opcode == 16:
                accumulator = registerA.clone()
            elif opcode == 17:
                accumulator = accumulator.clone() ** 2
            elif opcode == 18:
                registerA = memory[int(pointerOne)].clone()
            elif opcode == 19:
                registerA = memory[int(pointerTwo)].clone()
            elif opcode == 20:
                if int(checkFlag) == 1:
                    overheadPC = memory[int(pointerOne)].clone().value
                else:
                    overheadPC = -memory[int(pointerOne)].clone().value
            elif opcode == 21:
                memory[int(pointerOne)] += UInt16(1)
            elif opcode == 22:
                memory[int(pointerTwo)] += UInt16(1)
            elif opcode == 23:
                memory[int(pointerOne)] -= UInt16(1)
            elif opcode == 24:
                memory[int(pointerTwo)] -= UInt16(1)
            elif opcode == 25:
                pc += int(accumulator.clone().value)
            elif opcode == 26:
                pc -= int(accumulator.clone().value)
            elif opcode == 27:
                memory[int(pointerOne)] = accumulator.clone()
            elif opcode == 28:
                memory[int(pointerTwo)] = accumulator.clone()
            elif opcode == 29:  # Input
                if Input:
                    char = getch()
                    memory[int(pointerOne)] = UInt16(ord(char))
            elif opcode == 30:  # Output
                if Output:
                    val = memory[int(pointerOne)].clone().value
                    try:
                        print(chr(val), end='')
                    except ValueError:
                        print('?', end='')
            elif opcode == 31:
                checkFlag = 1 if accumulator.clone().value == registerA.clone().value else 0
            elif opcode == 32:
                checkFlag = 1 if accumulator.clone().value < registerA.clone().value else 0
            elif opcode == 33:
                accumulator = UInt16(checkFlag)
            elif opcode == 34:  # Not checkFlag
                checkFlag = 1 - checkFlag
            elif opcode == 35:  # Toggle enchantment
                cell = memory[int(pointerOne)]
                cell.enchanted = not cell.enchanted
            else:
                pass

        pc += 1
    any_enchanted = any(cell.enchanted for cell in memory.data)

    if any_enchanted:
        # Save current enchanted values (unenchant them)
        final_enchanted = {i: int(cell) for i, cell in enumerate(memory.data) if cell.enchanted}
        
        # Restore **all memory** from snapshot
        memory.data = [snap.clone() for snap in snapshot["memory"]]
        
        # Overwrite enchanted cells with their original value WITHOUT enchantment
        for i, val in final_enchanted.items():
            memory[i] = UInt16(val, enchanted=False)
        
        # Restore registers
        pointerOne = restore_register_with_enchantment(pointerOne, snapshot["pointerOne"])
        pointerTwo = restore_register_with_enchantment(pointerTwo, snapshot["pointerTwo"])
        accumulator = restore_register_with_enchantment(accumulator, snapshot["accumulator"])
        registerA = restore_register_with_enchantment(registerA, snapshot["registerA"])
        checkFlag = restore_register_with_enchantment(checkFlag, snapshot["checkFlag"])

    print("=== End Of Execution ===")
    print(f"P1: {pointerOne} P2: {pointerTwo}\nACC: {accumulator}  REG:{registerA} CHKF:{checkFlag}")
    print(memory[:30])
    print(f"EFFECT ON OHPC:{overheadPC}")

CATprogram = [
    10, # Clear cell
    21, # Increment
    18, # Move to register A
    16, # Move to accumlator
    12, # acc += reg
    12, # acc += reg
    12, # acc += reg
    17, # square
    13, # acc -= reg
    13, # acc -= reg
    13, # acc -= reg
    29, # get input
    18, # load into regA
    31, # check equal
    34, # NOT checkflag
    33, # load checkflag into accumlator
    14, # accumlator *= 13
    14, # accumlator *= 13
    30, # Print Char
    26  # pc -= accumlator
]

run_snippet(CATprogram)
print(microinstructions_to_instruction(CATprogram))
print(disassemble(CATprogram))

print(instruction_to_microinstructions(microinstructions_to_instruction(CATprogram)))