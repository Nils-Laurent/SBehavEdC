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
    def __str__(self):
        return 'EqualToken'

class CommaToken(object):
    def __repr__(self):
        return 'CommaToken'

class IdentifierToken(object):
    def __init__(self, value):
        self.value = value
    def __repr__(self):
        return 'IdentifierToken('+self.value+')'

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
        print("Unexpected token ", self.token.__str__(), " : expected ", expected)
        time.sleep(1)
        raise Exception("Unexpected token")


class Parser:
    def __init__(self, fname):
        self.lex = Lexer(fname)
        self.err = Error()
        self.gen = self.lex.next()

    def advance(self):
        self.token = next(self.gen)

    def expect(self, token, type):
        if not isinstance(token, type):
            self.err.token(token, type)
    def expect_multiple(self, token, types):
        match = False
        for t in types:
            match = match or isinstance(token, t)
        if not match:
            self.err.token(token, types)

    def parse(self):
        # SB script must start with SB code
        self.advance()
        if not isinstance(self.token, StartSBCode):
            self.err.token(self.token, StartSBCode)
        self.advance()

        t = self.parse_SBProg()
        if not isinstance(self.token, EndSBCode):
            self.err.token(self.token, EndSBCode)
        return t
    
    def parse_SBProg(self):
        t = TProg()
        while isinstance(self.token, IdentifierToken):
            name = self.token.value
            self.advance()
            t.add_instruction(self.parse_inst(name))
        if not isinstance(self.token, EndSBCode):
            self.err.token(self.token, EndSBCode)
        return t

    def parse_inst(self, identifier):
        t = TInst()
        if isinstance(self.token, EqualToken):
            t.set_inst(self.parse_variable(identifier))
        else:
            t.set_inst(self.parse_function(identifier))
        return t

    def parse_function(self, identifier):
        t = TFunction(identifier)
        argT = [StrToken, NumberToken, IdentifierToken]

        self.expect(self.token, OBracketToken)
        self.advance()
        self.expect_multiple(self.token, argT)
        t.add_argument(self.token.value)
        self.advance()
        while isinstance(self.token, CommaToken):
            self.advance()
            self.expect_multiple(self.token, argT)
            t.add_argument(self.token.value)
            self.advance()
        self.expect(self.token, CBracketToken)
        self.advance()
        return t

    def parse_variable(self, identifier):
        t = TVariable(identifier)
        self.expect(self.token, EqualToken)
        self.advance()
        if isinstance(self.token, StrToken):
            t.set_value(self.token.value)
            self.advance()
        elif isinstance(self.token, OSBracketToken):
            self.advance()
            value = []
            self.expect(self.token, StrToken)
            value.append(self.token.value)
            self.advance()

            while isinstance(self.token, CommaToken):
                self.advance()
                self.expect(self.token, StrToken)
                value.append(self.token.value)
                self.advance()
            self.expect(self.token, CSBracketToken)
            t.set_value(value)
            self.advance()
        elif isinstance(self.token, IdentifierToken):
            name = self.token.value
            self.advance()
            t.set_value(self.parse_function(name))

        return t


class TProg:
    def __init__(self):
        self.inst = []
    def add_instruction(self, instruction):
        self.inst.append(instruction)
    def print(self):
        print("PROGRAM")
        for i in self.inst:
            i.print(0)
    def gen_code(self, env):
        for i in self.inst:
            i.print(0)
            i.gen_code(env)


class TInst:
    def __init__(self):
        self.inst = None
    def set_inst(self, inst):
        self.inst = inst
    def print(self, n):
        print(n*"  ", "INSTRUCTION")
        self.inst.print(n+1)
    def gen_code(self, env):
        self.inst.gen_code(env)


class TFunction:
    def __init__(self, func_name):
        self.name = func_name
        self.arguments = []

    def add_argument(self, arg):
        self.arguments.append(arg)

    def print(self, n):
        args = ""
        for a in self.arguments:
            args += a.__str__() + " "
        print(n*"  ", self.name, "(", args, ")")

    def __str__(self):
        args = ""
        for a in self.arguments:
            args += a.__str__() + " "
        return self.name+"("+args+")"

    def gen_code(self, env):
        env.func.exec(self.name, self.arguments)

    def get_value_from_function(self, env):
        if not env.func.in_affect_function(self.name):
            raise Exception("Cannot assign", self.name, "to variable")
        return env.func.list_str(self.arguments)


class TVariable:
    def __init__(self, var_name):
        self.name = var_name
        self.value = None

    def set_value(self, value):
        self.value = value

    def print(self, n):
        print(n*"  ", self.name, "=", self.value)

    def gen_code(self, env):
        if isinstance(self.value, TFunction):
            env.set_var(self.name, self.value.get_value_from_function(env))
        else:
            env.set_var(self.name, self.value)


class TBehavedCode:
    def __init__(self, code):
        self.code = code

    def print(self):
        print(self.code)


class Compiler:
    def __init__(self, file):
        self.file = file
        self.parser = Parser(file)
        self.env = Env()

    def compile(self):
        tree = self.parser.parse()
        tree.gen_code(self.env)


class Env:
    def __init__(self):
        self.vars = {}
        self.code = {}
        self.func = Function(self)

    def set_var(self, name, value):
        self.vars[name] = value

    def get_value(self, name):
        if name in self.vars.keys():
            return self.vars[name]
        else:
            raise Exception("Undeclared variable use :", name)

    def set_code(self, name, code):
        self.vars[name] = code

    def get_code(self, name):
        if name in self.vars.keys():
            return self.vars[name]
        else:
            raise Exception("Undeclared factor code use :", name)


class Function:
    def __init__(self, env):
        self.functions = ["continue_file", "caffect_multiple", "behaved_factor_code", "list_str"]
        self.affect_functions = ["list_str"]
        self.env = env

    def in_affect_function(self, name):
        return name in self.affect_functions

    def is_function(self, identifier):
        return (identifier in self.functions)

    def exec(self, name, args):
        getattr(self, name)(args)

    def continue_file(self, args):
        print("continue_file")

    def caffect_multiple(self, args):
        print("caffect_multiple")

    def list_str(self, args):
        list = []
        a = int(args[1])
        b = int(args[2])
        for i in range(a, b): # todo : add + 1 à supp
            list.append(args[0] + str(i))
        return list

    def behaved_factor_code(self, args):
        print("behaved_factor_code")


class Types:
    def __init__(self):
        self.str = "str"
        self.tab = "tab"


if True or len(sys.argv) == 2:
    # cfile = sys.argv[1]
    cfile = "C:\\Users\\Nils\\Desktop\\SBehavedC\\ex.sb"
    print("compiling :", cfile)
    c = Compiler(cfile)
    c.compile()
else:
    print("usage :")
    print("SBehavEd.py <file_to_compile>")
print()
print("[end]")
