from enum import Enum
from typing import List, Optional, Dict

# Token types
class TokenType(Enum):
    NUMBER = 'NUMBER'
    PLUS = 'PLUS'
    MINUS = 'MINUS'
    MULTIPLY = 'MULTIPLY'
    DIVIDE = 'DIVIDE'
    LPAREN = 'LPAREN'
    RPAREN = 'RPAREN'
    EOF = 'EOF'
    IDENTIFIER = 'IDENTIFIER'
    EQUALS = 'EQUALS'
    SEMICOLON = 'SEMICOLON'
    IF = 'IF'
    ELSE = 'ELSE'
    WHILE = 'WHILE'
    PRINT = 'PRINT'

class Token:
    def __init__(self, type: TokenType, value: str, line: int, column: int):
        self.type = type
        self.value = value
        self.line = line
        self.column = column

class Lexer:
    def __init__(self, text: str):
        self.text = text
        self.pos = 0
        self.current_char = self.text[0] if text else None
        self.line = 1
        self.column = 1
        self.keywords = {
            'if': TokenType.IF,
            'else': TokenType.ELSE,
            'while': TokenType.WHILE,
            'print': TokenType.PRINT
        }

    def error(self):
        raise Exception(f'Invalid character at line {self.line}, column {self.column}')

    def advance(self):
        self.pos += 1
        self.column += 1
        if self.pos > len(self.text) - 1:
            self.current_char = None
        else:
            if self.text[self.pos] == '\n':
                self.line += 1
                self.column = 0
            self.current_char = self.text[self.pos]

    def skip_whitespace(self):
        while self.current_char and self.current_char.isspace():
            self.advance()

    def number(self) -> Token:
        result = ''
        column_start = self.column
        
        while self.current_char and self.current_char.isdigit():
            result += self.current_char
            self.advance()

        return Token(TokenType.NUMBER, result, self.line, column_start)

    def identifier(self) -> Token:
        result = ''
        column_start = self.column
        
        while self.current_char and (self.current_char.isalnum() or self.current_char == '_'):
            result += self.current_char
            self.advance()

        # Check if identifier is a keyword
        token_type = self.keywords.get(result.lower(), TokenType.IDENTIFIER)
        return Token(token_type, result, self.line, column_start)

    def get_next_token(self) -> Token:
        while self.current_char:
            if self.current_char.isspace():
                self.skip_whitespace()
                continue

            if self.current_char.isalpha() or self.current_char == '_':
                return self.identifier()

            if self.current_char.isdigit():
                return self.number()

            if self.current_char == '=':
                token = Token(TokenType.EQUALS, '=', self.line, self.column)
                self.advance()
                return token

            if self.current_char == ';':
                token = Token(TokenType.SEMICOLON, ';', self.line, self.column)
                self.advance()
                return token

            if self.current_char == '+':
                token = Token(TokenType.PLUS, '+', self.line, self.column)
                self.advance()
                return token

            if self.current_char == '-':
                token = Token(TokenType.MINUS, '-', self.line, self.column)
                self.advance()
                return token

            if self.current_char == '*':
                token = Token(TokenType.MULTIPLY, '*', self.line, self.column)
                self.advance()
                return token

            if self.current_char == '/':
                token = Token(TokenType.DIVIDE, '/', self.line, self.column)
                self.advance()
                return token

            if self.current_char == '(':
                token = Token(TokenType.LPAREN, '(', self.line, self.column)
                self.advance()
                return token

            if self.current_char == ')':
                token = Token(TokenType.RPAREN, ')', self.line, self.column)
                self.advance()
                return token

            self.error()

        return Token(TokenType.EOF, '', self.line, self.column)

class Parser:
    def __init__(self, lexer: Lexer):
        self.lexer = lexer
        self.current_token = self.lexer.get_next_token()

    def error(self):
        raise Exception('Invalid syntax')

    def eat(self, token_type: TokenType):
        if self.current_token.type == token_type:
            self.current_token = self.lexer.get_next_token()
        else:
            self.error()

    def factor(self) -> float:
        token = self.current_token
        if token.type == TokenType.NUMBER:
            self.eat(TokenType.NUMBER)
            return float(token.value)
        elif token.type == TokenType.LPAREN:
            self.eat(TokenType.LPAREN)
            result = self.expr()
            self.eat(TokenType.RPAREN)
            return result
        else:
            self.error()

    def term(self) -> float:
        result = self.factor()

        while self.current_token.type in (TokenType.MULTIPLY, TokenType.DIVIDE):
            token = self.current_token
            if token.type == TokenType.MULTIPLY:
                self.eat(TokenType.MULTIPLY)
                result *= self.factor()
            elif token.type == TokenType.DIVIDE:
                self.eat(TokenType.DIVIDE)
                result /= self.factor()

        return result

    def expr(self) -> float:
        result = self.term()

        while self.current_token.type in (TokenType.PLUS, TokenType.MINUS):
            token = self.current_token
            if token.type == TokenType.PLUS:
                self.eat(TokenType.PLUS)
                result += self.term()
            elif token.type == TokenType.MINUS:
                self.eat(TokenType.MINUS)
                result -= self.term()

        return result

class Interpreter:
    def __init__(self):
        self.variables: Dict[str, float] = {}

    def interpret(self, parser: Parser) -> Optional[float]:
        while parser.current_token.type != TokenType.EOF:
            result = self.statement(parser)
            if result is not None:
                return result
        return None

    def statement(self, parser: Parser) -> Optional[float]:
        token = parser.current_token

        if token.type == TokenType.IDENTIFIER:
            name = token.value
            parser.eat(TokenType.IDENTIFIER)
            
            if parser.current_token.type == TokenType.EQUALS:
                parser.eat(TokenType.EQUALS)
                value = parser.expr()
                self.variables[name] = value
                parser.eat(TokenType.SEMICOLON)
                return None
            
        elif token.type == TokenType.PRINT:
            parser.eat(TokenType.PRINT)
            value = parser.expr()
            print(value)
            parser.eat(TokenType.SEMICOLON)
            return None

        return parser.expr()

def compile_and_run(text: str) -> Optional[float]:
    lexer = Lexer(text)
    parser = Parser(lexer)
    interpreter = Interpreter()
    return interpreter.interpret(parser)

# Example usage
if __name__ == "__main__":
    print("Simple Programming Language Compiler")
    print("Type your code (Ctrl+C to exit)")
    print("Examples:")
    print("x = 5;")
    print("print 2 + 3 * 4;")
    
    while True:
        try:
            text = input('> ')
            if not text:
                continue
            result = compile_and_run(text)
            if result is not None:
                print(result)
        except Exception as e:
            print(f'Error: {str(e)}') 