
# Max/Min integer constantss
UNSIGNED_MAX_INT = 4294967296
MAX_INT = 2147483647
MIN_INT = -2147483648

# Overflow Detection Functions
def mult_will_overflow(a, b, signed=True):
	'''Checks if the mutliplying the two params will
	cause 32 bit signed int overflow.
	'''
	if signed:
		if a > 0 and b > 0:
			return b != 0 and a > MAX_INT / b
		else:
			return b != 0 and abs(a) > abs(MIN_INT) / abs(b)
	else:
		return b != 0 and a > UNSIGNED_MAX_INT / b

def add_will_overflow(a, b, signed=True):
	'''Checks if added these two numbers will cause 32 bit
	signed integer overflow, without actually adding the
	two numbers.
	'''
	if signed:
		if a > 0 and b > 0:
			return b != 0 and a > MAX_INT - b
		else:
			return b != 0 and abs(a) > abs(MIN_INT) - abs(b)
	else:
		return b != 0 and a > UNSIGNED_MAX_INT - b

# Character processing functions
def get_char_value(char):
	'''Given a character it attempts to convert it into a int.
	Useful for converting hexadecimal characters into ints
	'''
	if char is 'a':
		return 10
	elif char is 'b':
		return 11
	elif char is 'c':
		return 12
	elif char is 'd':
		return 13
	elif char is 'e':
		return 14
	elif char is 'f':
		return 15
	else:
		return int(char)