from lexical_analyser import LexicalAnalyser

def test():
	'''Runs Tests'''
	tests = [
		# decimal
		("12", "DEC", 12),
		("-12", "DEC", -12),
		("011", "DEC", 11),
		("101", "DEC", 101),
		("2147483645", "DEC", 2147483645),
		("2147483647", "DEC", 2147483647),
		("-2147483647", "DEC", -2147483647),
		("-2147483648", "DEC", -2147483648),
		("2147483648", "OVERFLOW", None),
		("-2147483649", "OVERFLOW", None),
		("-", "ERROR", None),
		("+", "ERROR", None),
		("+-12", "ERROR", None), # two signs at start
		("+45-12", "ERROR", None), # two sign in middle of input
		("0", "DEC", 0),
		("+0", "DEC", 0),
		("-0", "DEC", 0),
		("-23456", "DEC", -23456),

		# hexademical
		("123H", "HEX", 291),
		("00123H", "HEX", 291),
		("A32H", "HEX", 2610),
		("3F2B1H", "HEX", 258737), # hex with B in it
		("FFFFFFFFH", "HEX", 4294967295),
		("FFFFFFFFFH", "OVERFLOW", None),
		("FFFFFHFFF", "ERROR", None), # H not last character in string
		("H", "ERROR", None), # only the H character
		("FFFFFHH", "ERROR", None), # H after the H character

		# octal
		("256B", "OCT", 174),
		("23456B", "OCT", 10030),
		("37777777777b", "OCT", 4294967295),
		("47777777777b", "OVERFLOW", None),
		("-2345B", "ERROR", None), # signed not allowed

		# end marker
		# thesetest that any character that is not in the input is an end marker
		("256B^", "OCT", 174),
		("256Z", "DEC", 256),
		("256~", "DEC", 256),
		("12H_", "HEX", 18),
	]

	print "%i Tests Found" % len(tests)

	lexical_analyser = LexicalAnalyser()
	for string, expt_base, expt_value in tests:
		print "====="
		print "Testing '%s' is '%s' and equals '%s'" % (string, expt_base, expt_value)
		base, value = lexical_analyser.process(string)
		if base != expt_base:
			raise Exception("Received unexpected base as the result. Expected %s got %s. Value: %s" % (expt_base, base, value))

		if expt_value: # if we are expecting a value
			if value != expt_value:
				raise Exception("Unexpected value returned. Expected %s got %s" % (expt_value, value))
		print "Test Passed"			

	print "ALL TESTS (%i) PASSED!" % len(tests)

if __name__ == "__main__":
	test()