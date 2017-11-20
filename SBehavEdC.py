#Super Behaved Compiler
#Author : Nils Laurent

import sys
import time

class EOFToken(object):
    def __repr__(self):
        return 'EOFToken'

class StartSBCode(object):
    def __repr__(self):
        return 'StartSBCode'
class EndSBCode(object):
    def __repr__(self):
        return 'EndSBCode'

class OBracketToken(object):
    def __repr__(self):
        return 'OBracketToken'
class CBracketToken(object):
    def __repr__(self):
        return 'CBracketToken'
class OCBracketToken(object):
    def __repr__(self):
        return 'OCBracketToken'
class CCBracketToken(object):
    def __repr__(self):
        return 'CCBracketToken'
class OSBracketToken(object):
    def __repr__(self):
        return 'OSBracketToken'
class CSBracketToken(object):
    def __repr__(self):
        return 'CSBracketToken'
class EqualToken(object):
    def __repr__(self):
        return 'EqualToken'

class CommaToken(object):
    def __repr__(self):
        return 'CommaToken'

class IdentifierToken(object):
    def __init__(self, name):
        self.name = name
    def __repr__(self):
        return 'IdentifierToken('+self.name+')'

class NumberToken(object):
    def __init__(self, value):
        self.value = value
    def __repr__(self):
        return 'NumberToken('+self.value+')'

class StrToken(object):
    def __init__(self, value):
        self.value = value
    def __repr__(self):
        return 'StrToken('+self.value+')'

class BehavEdToken(object):
    def __init__(self, value):
        self.value = value
    def __repr__(self):
        return 'StrToken('+self.value+')'

class CharacterToken(object):
    def __init__(self, char): self.char = char
    def __eq__(self, other):
        return isinstance(other, CharacterToken) and self.char == other.char
    def __ne__(self, other): return not self == other

class Lexer:
    def __init__(self, fname):
        self.id_symbols = "_"
        
        self.fname = fname
        with open(self.fname, 'r') as content_file:
            self.buf = content_file.read()
        self.pos = 0
        self.current = self.buf[self.pos]
        self.buf_len = len(self.buf)

    def _advance(self):
        self.pos = self.pos + 1
        if self.pos < self.buf_len:
            self.current = self.buf[self.pos]
        else:
            self.current = None

    def _get_behaved(self):
        start_pos = self.pos
        end_BehavEd = "END_BEHAVED"
        eB_len = len(end_BehavEd)
        while self.buf[self.pos:self.pos+eB_len] != end_BehavEd and self.current:
            self._advance()
            while self.current != 'E' and self.current:
                self._advance()
        if not self.current:
            raise Exception("END_BEHAVED not found, position = "+self.pos)
        end_pos = self.pos
        self.pos = self.pos + eB_len
        if self.pos < self.buf_len:
            self.current = self.buf[self.pos]
        else:
            self.current = None
        return self.buf[start_pos:end_pos]
        
    def next(self):
        while self.current:
            # Skip whitespace
            while self.current.isspace():
                self._advance()
            # Identifier or keyword
            if self.current.isalpha() or self.current in self.id_symbols:
                id_str = ''
                while self.current.isalnum() or self.current in self.id_symbols:
                    id_str += self.current
                    self._advance()
                if id_str == "START_BEHAVED":
                    behaved_str = self._get_behaved()
                    yield BehavEdToken(behaved_str)
                else:
                    yield IdentifierToken(id_str)
            # Number
            elif self.current.isdigit():
                num_str = ''
                while self.current.isdigit():
                    num_str += self.current
                    self._advance()
                yield NumberToken(num_str)
            elif self.current == '=':
                self._advance()
                yield EqualToken()
            elif self.current == '<':
                self._advance()
                if self.current == '<':
                    self._advance()
                    yield StartSBCode()
            elif self.current == '>':
                self._advance()
                if self.current == '>':
                    self._advance()
                    yield EndSBCode()
            elif self.current == '(':
                self._advance()
                yield OBracketToken()
            elif self.current == ')':
                self._advance()
                yield CBracketToken()
            elif self.current == '{':
                self._advance()
                yield OCBracketToken()
            elif self.current == '}':
                self._advance()
                yield CCBracketToken()
            elif self.current == '[':
                self._advance()
                yield OSBracketToken()
            elif self.current == ']':
                self._advance()
                yield CSBracketToken()
            elif self.current == '"':
                str_str = ''
                self._advance()
                while self.current != '"':
                    str_str += self.current
                    self._advance()
                self._advance()
                yield StrToken(str_str)
            elif self.current == ',':
                self._advance()
                yield CommaToken()
            # Comment
            elif self.current == '/':
                self._advance()
                if self.current == '/':
                    while self.current and self.current not in '\r\n':
                        self._advance()
            elif self.current:
                # Some other char
                print("Unknown character '" + self.current + "' at position " + str(self.pos))
                raise Exception()
        yield EOFToken()

    def fast_forward_to_SBCode(self):
        while self.current != '<' and self.current != None:
            self._advance()
            if self.current == '<':
                self._advance()
        if self.current == '<':
            return StartSBCode()
        else:
            return EOFToken()

    def test_lex_all(self):
        token_gen = self.next()
        token = next(token_gen)
        print("token = ", token)
        i = 0
        while not isinstance(token, EOFToken) and i < 200:
            token = next(token_gen)
            if isinstance(token, EndSBCode):
                print("token = ", token)
                token = self.fast_forward_to_SBCode()
            print("token = ", token)
            i = i + 1

class Error:
    def token(self, token, expected):
            print("Unexpected token ", self.token, " ... expected ", expected)
            exit()

class Parser:
    def __init__(self, fname):
        print("toto")
        self.lex = Lexer(fname)
        self.err = Error()
        self.gen = self.lex.next()
        self.token = next(self.gen)
        self.func = Function()
        
        # SB script must start with SB code
        if not isinstance(self.token, StartSBCode):
            self.err.token(self.token, StartSBCode)
        parse_SBProg()
    
    def parse_SBProg(self):
        self.token = next(self.gen)
        parse_instructions()

    def parse_instructions(self):
        while isinstance(self.token, IdentifierToken):
            self.token = next(self.gen)
            parse_inst()
    def parse_inst(self, identifier):
        if self.func.isFunction(identifier):
            parse_function(identifier)
        else:
            parse_variable(identifier)

    def parse_function(self, identifier):
        t = TFunction(identifier)

        self.token = next(self.gen)
        if isinstance(self.token, OBracketToken):
            self.token = next(self.gen)
            if isinstance(self.token, IdentifierToken):
                t.add_argument(self.token.name)
            self.token = next(self.gen)
            while isinstance(self.token, CommaToken):
                self.token = next(self.gen)
                if isinstance(self.token, IdentifierToken):
                    t.add_argument(self.token.name)
                self.token = next(self.gen)
            if not isinstance(self.token, CBracketToken):
                self.err.token(self.token, CBracketToken)
        elif isinstance(self.token, IdentifierToken):
            # saving BehavEd code
            t.add_argument(self.token.value)
            self.token = next(self.gen)
            if isinstance(self.token, BehavEdToken):
                t.add_argument(self.token.value)

    def parse_variable(self, identifier):
        self.token = next(self.gen)
        t = TVariable(identifier)
        if isinstance(self.token, EqualToken):
            self.token = next(self.gen)
            if isinstance(self.token, StrToken):
                t.set_value(self.token.value)
            elif isinstance(self.token, OSBracketToken):
                value = []
                self.token = next(self.gen)
                if isinstance(self.token, StrToken):
                    value.append(StrToken.value)
            elif isinstance(self.token, IdentifierToken):
                t.set_value(self.parse_function(self.token.name))

        else:
            self.err.token(self.token, EqualToken)
        
class Function(self):
    def __init__(self):
        self.functions = ["continue_file", "caffect_multiple", "list_str", "behaved_factor_code"]

    def is_function(self, identifier):
        return (identifier in self.functions)


class TProg:
    def __init__(self):
        self.inst = []
    def add_instruction(self, instruction):
        self.inst.append(variables)

class TInst:
    def __init__(self):
        pass
class TFunction:
    def __init__(self, func_name):
        self.name = func_name
        self.arguments = []

    def add_argument(self, arg):
        self.arguments.append(arg)

class TBehavedCode:
    def __init__(self, code):
        self.code = code
    
class TVariable:
    def __init__(self, var_name):
        self.name = var_name
    def set_value(self, value):
        self.value = value

class Types:
    def __init__(self):
        self.str = "str"
        self.tab = "tab"

if len(sys.argv) == 2:
    cfile = sys.argv[1]
    print("compiling :", cfile)
    parser = Parser(cfile)
    parser.parseSBProg
else:
    print("usage :")
    print("SBehavEd.py <file_to_compile>")
print()
print("[end]")
time.sleep(3)
