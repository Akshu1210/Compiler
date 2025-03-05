#include <iostream>
#include <string>
#include <vector>
#include <map>
#include <cctype>
#include <stdexcept>

enum TokenType {
    NUMBER, PLUS, MINUS, MULTIPLY, DIVIDE, IDENTIFIER, EQUALS, SEMICOLON, END_OF_FILE, LPAREN, RPAREN
};

struct Token {
    TokenType type;
    std::string value;
    int line;
    int column;
    
    Token(TokenType t, std::string v, int l, int c) : type(t), value(v), line(l), column(c) {}
};

class Lexer {
private:
    std::string text;
    size_t pos;
    int line;
    int column;
    char current_char;

    void advance() {
        if (pos < text.length()) {
            if (text[pos] == '\n') {
                line++;
                column = 0;
            }
        }
        pos++;
        column++;
        current_char = (pos < text.length()) ? text[pos] : '\0';
    }

    void skip_whitespace() {
        while (current_char != '\0' && std::isspace(current_char)) {
            advance();
        }
    }

    Token number() {
        std::string result;
        int col_start = column;
        while (current_char != '\0' && std::isdigit(current_char)) {
            result += current_char;
            advance();
        }
        return Token(NUMBER, result, line, col_start);
    }

    Token identifier() {
        std::string result;
        int col_start = column;
        while (current_char != '\0' && (std::isalnum(current_char) || current_char == '_')) {
            result += current_char;
            advance();
        }
        return Token(IDENTIFIER, result, line, col_start);
    }

public:
    Lexer(const std::string& input) : text(input), pos(0), line(1), column(1), current_char(input.empty() ? '\0' : input[0]) {}

    Token get_next_token() {
        while (current_char != '\0') {
            if (std::isspace(current_char)) {
                skip_whitespace();
                continue;
            }
            if (std::isdigit(current_char)) return number();
            if (std::isalpha(current_char) || current_char == '_') return identifier();
            if (current_char == '+') return Token(PLUS, "+", line, column++), advance(), Token(PLUS, "+", line, column);
            if (current_char == '-') return Token(MINUS, "-", line, column++), advance(), Token(MINUS, "-", line, column);
            if (current_char == '*') return Token(MULTIPLY, "*", line, column++), advance(), Token(MULTIPLY, "*", line, column);
            if (current_char == '/') return Token(DIVIDE, "/", line, column++), advance(), Token(DIVIDE, "/", line, column);
            if (current_char == '=') return Token(EQUALS, "=", line, column++), advance(), Token(EQUALS, "=", line, column);
            if (current_char == ';') return Token(SEMICOLON, ";", line, column++), advance(), Token(SEMICOLON, ";", line, column);
            if (current_char == '(') return Token(LPAREN, "(", line, column++), advance(), Token(LPAREN, "(", line, column);
            if (current_char == ')') return Token(RPAREN, ")", line, column++), advance(), Token(RPAREN, ")", line, column);
            throw std::runtime_error("Invalid character at line " + std::to_string(line) + ", column " + std::to_string(column));
        }
        return Token(END_OF_FILE, "", line, column);
    }
};

class Parser {
private:
    Lexer lexer;
    Token current_token;
    std::map<std::string, double> variables;

    void eat(TokenType token_type) {
        if (current_token.type == token_type) {
            current_token = lexer.get_next_token();
        } else {
            throw std::runtime_error("Syntax error");
        }
    }

    double factor() {
        Token token = current_token;
        if (token.type == NUMBER) { eat(NUMBER); return std::stod(token.value); }
        if (token.type == LPAREN) { eat(LPAREN); double result = expr(); eat(RPAREN); return result; }
        if (token.type == IDENTIFIER) {
            eat(IDENTIFIER);
            if (variables.find(token.value) == variables.end()) throw std::runtime_error("Undefined variable: " + token.value);
            return variables[token.value];
        }
        throw std::runtime_error("Invalid factor");
    }

    double term() {
        double result = factor();
        while (current_token.type == MULTIPLY || current_token.type == DIVIDE) {
            Token token = current_token;
            if (token.type == MULTIPLY) { eat(MULTIPLY); result *= factor(); }
            else if (token.type == DIVIDE) {
                eat(DIVIDE); double divisor = factor();
                if (divisor == 0) throw std::runtime_error("Division by zero");
                result /= divisor;
            }
        }
        return result;
    }

    double expr() {
        double result = term();
        while (current_token.type == PLUS || current_token.type == MINUS) {
            Token token = current_token;
            if (token.type == PLUS) { eat(PLUS); result += term(); }
            else if (token.type == MINUS) { eat(MINUS); result -= term(); }
        }
        return result;
    }

public:
    Parser(const std::string& text) : lexer(text) { current_token = lexer.get_next_token(); }

    double parse() {
        if (current_token.type == IDENTIFIER) {
            std::string var_name = current_token.value;
            eat(IDENTIFIER);
            if (current_token.type == EQUALS) {
                eat(EQUALS); double value = expr(); variables[var_name] = value;
                if (current_token.type == SEMICOLON) eat(SEMICOLON);
                return value;
            }
        }
        double result = expr();
        if (current_token.type == SEMICOLON) eat(SEMICOLON);
        return result;
    }
};

int main() {
    std::string line;
    while (true) {
        std::cout << "> ";
        std::getline(std::cin, line);
        if (line.empty()) continue;
        try { Parser parser(line); std::cout << parser.parse() << std::endl; }
        catch (const std::exception& e) { std::cout << "Error: " << e.what() << std::endl; }
    }
    return 0;
}
