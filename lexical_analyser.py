from utils import mult_will_overflow, add_will_overflow, get_char_value

# input character sets
SIGN = ('-', '+')
LOWER_DIGIT = ('0', '1', '2', '3', '4', '5', '6', '7')
UPPER_DIGIT = ('8', '9')
ACF = ('a', 'c', 'd', 'e', 'f')
INPUT_SET = SIGN + LOWER_DIGIT + UPPER_DIGIT + ACF + ('b', 'h') # all valid input characters

class LexicalAnalyser(object):
    '''Lexical Analyser for decimal, octal and hexadecimal numbers.

    All input strings must match the regular expression:
    ((+|-)?[0-9]+) | [0-7]+[bB] | [0-9a-fA-F]+[hH]
    '''
    BASE_DEC = 1
    BASE_OCT = 2
    BASE_HEX = 3

    START_STATE = 1
    ANY_STATE = 2
    DEC_STATE = 3
    HEX_STATE = 4
    DEC_HEX_STATE = 5
    OCT_HEX_STATE = 6
    H_STATE = 7
    ONE_DIGIT_STATE = 8
    OVERFLOW_STATE = 9
    ERROR_STATE = 10
    UNEXPECTED_H_ERROR = 11

    state = START_STATE
    sign = 1 # 1 for positive sign and -1 for negative sign
    base = None # Unkown - at the beginning we don't know what base we have
    dec_total = 0
    oct_total = 0
    hex_total = 0
    dec_overflowed = False
    oct_overflowed = False
    hex_overflowed = False

    def process(self, input_string):
        '''Parses the given input string to determine the number's
        base and the its absolute value.

        Result:
            tuple(base, integer value)
        '''
        self._reset() # reset the state machine
        for char in input_string.lower():
            result = self._next_state(char)
        # keep give the machine end marker characters until it returns a result
        while result is None:
            result = self._next_state('!') # add end marker character if we have reached end of string
        return result

    def _reset(self):
        '''Restarts the state machine to its initial state'''
        self.state = self.START_STATE
        self.sign = 1
        self.base = None
        self.dec_total = 0
        self.oct_total = 0
        self.hex_total = 0
        self.dec_overflowed = False
        self.oct_overflowed = False
        self.hex_overflowed = False

    def _value_transition(self, next_state, char):
        '''Updates the int totals for the three bases and 
        checks if updating the totals will cause overflow. 
        '''
        # convert input character into a int
        value = get_char_value(char)

        # update the running total for each base
        # checking for overflow before it happens
        if not self.dec_overflowed:
            if not mult_will_overflow(self.dec_total, 10):
                self.dec_total *= 10
            else:
                self.dec_overflowed = True

            if not add_will_overflow(self.dec_total, value):
                self.dec_total += (value * self.sign)
            else:
                self.dec_overflowed = True

        if not self.oct_overflowed:
            if value <= 7: # largest value is 7 - if larger obviously not an octal character (maybe end character B)
                if not mult_will_overflow(self.oct_total, 8, False):
                    self.oct_total *= 8
                else:
                    self.oct_overflowed = True

                if not add_will_overflow(self.oct_total, value, False):
                    self.oct_total += value
                else:
                    self.oct_overflowed = True

        if not self.hex_overflowed:
            if not mult_will_overflow(self.hex_total, 16, False):
                self.hex_total *= 16
            else:
                self.hex_overflowed = True

            if not add_will_overflow(self.hex_total, value, False):
                self.hex_total += value
            else:
                self.hex_overflowed = True

        self.state = next_state

    def _next_state(self, char):
        '''Determines the next state and does the transition'''
        #print "STATE: %i INPUT: %s" % (self.state, char)
        if self.state is self.START_STATE:
            # STARTING STATE
            if char in SIGN:
                if char == '-':
                    self.sign = -1
                self.state = self.ONE_DIGIT_STATE 
            elif char in LOWER_DIGIT:
                self._value_transition(self.ANY_STATE, char)
            elif char in UPPER_DIGIT:
                self._value_transition(self.DEC_HEX_STATE, char)
            elif char in ACF + ('b',):
                self._value_transition(self.HEX_STATE, char)
            elif char == 'h':
                self.state = self.UNEXPECTED_H_ERROR
            else: # END MARKER
                self.state = self.ERROR_STATE # empty string

        elif self.state is self.ANY_STATE:
            # ANY STATE
            # number could be any of Dec, Hex or Oct
            if char in SIGN:
                self.state = self.ERROR_STATE 
            elif char in LOWER_DIGIT:
                self._value_transition(self.ANY_STATE, char)
            elif char in UPPER_DIGIT:
                self._value_transition(self.DEC_HEX_STATE, char)
            elif char in ACF:
                self._value_transition(self.HEX_STATE, char)
            elif char == 'b':
                self._value_transition(self.OCT_HEX_STATE, char)
            elif char == 'h':
                self.state = self.H_STATE
            else: # end marker or any other character
                self.base = self.BASE_DEC
                return self.accept()

        elif self.state is self.DEC_STATE:
            # DECIMAL STATE
            # we know we have a decimal number
            self.base = self.BASE_DEC

            if char in SIGN + ACF + ('b',):
                self.state = self.ERROR_STATE 
            elif char in LOWER_DIGIT:
                self._value_transition(self.DEC_STATE, char)
            elif char in UPPER_DIGIT:
                self._value_transition(self.DEC_STATE, char)
            elif char == 'h':
                self.state = self.UNEXPECTED_H_ERROR
            else: # END MARKER
                return self.accept()

        elif self.state is self.HEX_STATE:
            # HEX STATE
            # we know this number is a hexadecimal number
            self.base = self.BASE_HEX

            if char in SIGN:
                self.state = self.ERROR_STATE 
            elif char in LOWER_DIGIT + UPPER_DIGIT + ACF + ('b',):
                self._value_transition(self.HEX_STATE, char)
            elif char == 'h':
                self.state = self.H_STATE
            else: # END MARKER
                self.state = self.ERROR_STATE

        elif self.state is self.DEC_HEX_STATE:
            # DEC/HEX STATE
            # this number is either a decimal or Hexadecial number
            if char in SIGN:
                self.state = self.ERROR_STATE 
            elif char in LOWER_DIGIT + UPPER_DIGIT:
                self._value_transition(self.DEC_HEX_STATE, char)
            elif char in ACF + ('b',):
                self._value_transition(self.HEX_STATE, char)
            elif char == 'h':
                self.state = self.H_STATE
            else: # END MARKER
                self.base = self.BASE_DEC
                return self.accept()

        elif self.state is self.OCT_HEX_STATE:
            # OCT/HEX STATE
            # this number is either an octal or hexadecimal number
            if char in SIGN:
                self.state = self.ERROR_STATE 
            elif char in LOWER_DIGIT + ('b',):
                self._value_transition(self.OCT_HEX_STATE, char)
            elif char in UPPER_DIGIT + ACF:
                self._value_transition(self.HEX_STATE, char)
            elif char == 'h':
                self.state = self.H_STATE
            else: # END MARKER
                self.base = self.BASE_OCT
                return self.accept()

        elif self.state is self.H_STATE:
            # H STATE
            # once we get a H we don't want any more characters except an end marker
            if char in SIGN + LOWER_DIGIT + UPPER_DIGIT + ACF + ('b',):
                self.state = self.ERROR_STATE
            elif char == 'h':
                self.state = self.UNEXPECTED_H_ERROR
            else: # end marker is the only acceptable input at this state
                self.base = self.BASE_HEX
                return self.accept()

        elif self.state is self.ONE_DIGIT_STATE:
            # ONE DIGIT
            # need to see at least one digit after a sign
            # digits are the only accepted input because 
            # decimal numbers are the only signed numbers
            if char in LOWER_DIGIT + UPPER_DIGIT:
                self._value_transition(self.DEC_STATE, char)
            else:
                self.state = self.ERROR_STATE

        elif self.state is self.OVERFLOW_STATE:
            # do nothing if we are still getting input other than end marker
            if char not in INPUT_SET: # end marker is any character not in the input set
                return ("OVERFLOW", None) # hit the end marker finally

        elif self.state is self.ERROR_STATE:
            # do nothing if we are still getting input other than end marker
            if char not in INPUT_SET:
                return ("ERROR", "Unexpected character found in the input stream") # hit the end marker finally
        
        elif self.state is self.UNEXPECTED_H_ERROR:
            # do nothing if we are still getting input other than end marker
            if char not in INPUT_SET:
                return ("ERROR", "Unexpected character 'H'. 'H' marks the end of a hexadecimal number only") # hit the end marker finally

    def accept(self):
        '''Returns a result finally'''
        if self.base is self.BASE_DEC:
            if not self.dec_overflowed:
                return ("DEC", self.dec_total)
            else:
                return ("OVERFLOW", "Signed Integer Overflow: value is outside the range -(2^31) <> +((2^31)-1")

        elif self.base is self.BASE_OCT:
            if not self.oct_overflowed:
                return ("OCT", self.oct_total)
            else:
                return ("OVERFLOW", "Integer Overflow: value is larger than (2^32)-1")

        elif self.base is self.BASE_HEX:
            if not self.hex_overflowed:
                return ("HEX", self.hex_total)
            else:
                return ("OVERFLOW", "Integer Overflow: value is larger than (2^32)-1")

if __name__ == "__main__":
    import sys

    try:
        filename = sys.argv[1]
    except IndexError:
        print "Missing Arguments"
        print "Usage: lexical_analyser.py <filename>"
        sys.exit(0)

    # read file into list
    lexical_analyser = LexicalAnalyser()
    with open(filename) as f:
        lines = f.readlines()

    for line in lines:
        base, value = lexical_analyser.process(line)
        print "%s ==> %s: %s" % (line.rstrip(), base, value)