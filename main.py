import sys
import array
import sys

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

def extract_letters_and_spaces(filename):
    with open(filename, 'r', encoding='utf-8') as file:
        content = file.read()

    # Replace newlines with spaces
    content = content.replace('\n', ' ')

    # Keep only letters and spaces
    filtered = ''.join(c for c in content if c.isalpha() or c == ' ')
    
    # Convert to lowercase
    return filtered.lower()

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

def restore_register_with_enchantment(reg, snap):
    if not reg.enchanted:
        return snap.clone()
    return UInt16(int(reg), enchanted=False)  # keep the enchanted value

def fetch(s: str) -> int:
    filtered = ''.join(ch.lower() for ch in s if ch.isalpha())
    result = 0
    for ch in filtered:
        digit = ord(ch) - ord('a') + 1  # 1-26 instead of 0-25
        result = result * 26 + digit
    return result
    
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python run.py <filename>")
        sys.exit(1)

    Input = True
    Output =  True
    Debug = True
    
    input_file = sys.argv[1]
    sentence = extract_letters_and_spaces(input_file)
    sentence = sentence.split()

    memory = UInt16Array(65536) # Fix this because this is supposed to have all range of 16 bits

    pointerOne = UInt16(0)
    pointerTwo = UInt16(0)
    accumulator = UInt16(0)
    registerA = UInt16(0)
    checkFlag = UInt16(0)
    overheadPC = 0
    
    while overheadPC < len(sentence):
        if overheadPC >= 0:
            word = sentence[overheadPC]
            wordz = fetch(word)
            wordz = shuffle(wordz)
            base = 36
            wordz += 1
            array = to_base_n_1_indexed(wordz, base)
            pc = 0  # program counter
            jumpModification = 0
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
                        checkFlag = UInt16(1) if int(accumulator) == int(registerA) else UInt16(0)
                    elif opcode == 32:
                        checkFlag = UInt16(1) if int(accumulator) < int(registerA) else UInt16(0)
                    elif opcode == 33:
                        accumulator = UInt16(int(checkFlag))
                    elif opcode == 34:
                        checkFlag = UInt16(1 - int(checkFlag))
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


        overheadPC += jumpModification
        overheadPC += 1
    if Debug:
        print("")
        print(f"P1: {pointerOne} P2: {pointerTwo}\nACC: {accumulator}  REG:{registerA} CHKF:{checkFlag} OHPC:{checkFlag}")
        print(memory[:30])

