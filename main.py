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
    def __init__(self, value):
        self.value = value & 0xFFFF  # Force 16-bit range

    def __int__(self):
        return self.value

    # Arithmetic operations
    def __add__(self, other):
        return UInt16(self.value + int(other))

    def __sub__(self, other):
        return UInt16(self.value - int(other))

    def __mul__(self, other):
        return UInt16(self.value * int(other))

    def __floordiv__(self, other):
        return UInt16(self.value // int(other))

    def __pow__(self, power, modulo=None):
        return UInt16(pow(self.value, int(power), 0x10000))

    # In-place variants (return new objects to prevent aliasing bugs)
    def __iadd__(self, other):
        return self.__add__(other)

    def __isub__(self, other):
        return self.__sub__(other)

    def __imul__(self, other):
        return self.__mul__(other)

    def __ifloordiv__(self, other):
        return self.__floordiv__(other)

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
        return str(self.value)

    def __str__(self):
        return str(self.value)

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
    Debug = False
    
    input_file = sys.argv[1]
    sentence = extract_letters_and_spaces(input_file)
    sentence = sentence.split()

    memory = UInt16Array(65536) # Fix this because this is supposed to have all range of 16 bits

    pointerOne = UInt16(0)
    pointerTwo = UInt16(0)
    accumulator = UInt16(0)
    registerA = UInt16(0)
    checkFlag = 0

    for word in sentence:
        wordz = fetch(word)
        wordz = shuffle(wordz)
        base = 36
        wordz += 1
        array = to_base_n_1_indexed(wordz, base)
        pc = 0  # program counter
        while pc < len(array):
            if pc >= 0:
                opcode = array[pc]
                if opcode == 1: # Increment pointer
                    pointerOne += UInt16(1)
                elif opcode == 2: # Decrement pointer
                    pointerTwo += UInt16(1)
                elif opcode == 3: # Set pointerone to accumlator
                    pointerOne = UInt16(int(accumulator))
                elif opcode == 4: # Set pointertwo to accumlator
                    pointerTwo = UInt16(int(accumulator))
                elif opcode == 5: # Set pointer to the memory addr it is pointing at
                    pointerOne = memory[int(pointerOne)]
                elif opcode == 6: # Set pointer to the memory addr it is pointing at
                    pointerTwo = memory[int(pointerOne)]
                elif opcode == 7: # set pointerOne addr to pointerTwo addr
                    memory[int(pointerOne)] = UInt16(int(memory[int(pointerTwo)]))
                elif opcode == 8: # set pointerTwo addr to pointerOne addr
                    memory[int(pointerTwo)] = memory[int(pointerOne)]
                elif opcode == 9: # swap values
                    memory[int(pointerOne)], memory[int(pointerTwo)] = memory[int(pointerTwo)], memory[int(pointerOne)]
                elif opcode == 10:
                    memory[int(pointerOne)] = UInt16(0)
                elif opcode == 11:
                    memory[int(pointerTwo)] = UInt16(0)
                elif opcode == 12:
                    accumulator += registerA
                elif opcode == 13:
                    accumulator -= registerA
                elif opcode == 14:
                    accumulator  *= registerA
                elif opcode == 15:
                    accumulator  //= registerA
                elif opcode == 16:
                    accumulator = UInt16(int(registerA))
                elif opcode == 17:
                    accumulator = accumulator  ** 2
                elif opcode == 18:
                    registerA = UInt16(int(memory[int(pointerOne)]))
                elif opcode == 19:
                    registerA = UInt16(int(memory[int(pointerTwo)]))
                elif opcode == 20:
                    memory[int(pointerOne)] = UInt16(int(registerA))
                elif opcode == 21:
                    memory[int(pointerOne)] += 1
                elif opcode == 22:
                    memory[int(pointerTwo)] += 1
                elif opcode == 23:
                    memory[int(pointerOne)] -= 1
                elif opcode == 24:
                    memory[int(pointerTwo)] -= 1
                elif opcode == 25:
                    pc += int(accumulator)
                elif opcode == 26:
                    pc -= int(accumulator)
                elif opcode == 27:
                    memory[int(pointerOne)] = UInt16(int(accumulator))
                elif opcode == 28:
                    memory[int(pointerTwo)] = UInt16(int(accumulator))
                elif opcode == 29: # input
                    if Input:
                        char = getch()
                        memory[int(pointerOne)] = ord(char)
                elif opcode == 30:
                    if Output:
                        val = int(memory[int(pointerOne)])
                        try:
                            print(chr(val), end='') 
                        except ValueError:
                            print('?', end='')
                elif opcode == 31:
                    if int(accumulator) == int(registerA):
                        checkFlag = 1
                    else:
                        checkFlag = 0
                elif opcode == 32:
                    if int(accumulator) < int(registerA):
                        checkFlag = 1
                    else:
                        checkFlag = 0
                elif opcode == 33:
                    accumulator = UInt16(checkFlag)
                elif opcode == 34: # Not Checkflag
                    checkFlag = 1-checkFlag 
                elif opcode:
                    pass
            pc += 1
        if Debug:
            print("")
            print(f"P1: {pointerOne} P2: {pointerTwo}\nACC: {accumulator}  REG:{registerA} CHKF:{checkFlag}")

            print(memory[:30])
