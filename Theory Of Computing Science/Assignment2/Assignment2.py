from enum import Enum, auto


class TokenType(Enum):
    NUMBER = auto()
    IDENT  = auto()
    PLUS   = auto()
    MINUS  = auto()
    MULT   = auto()
    EQUALS = auto()
    COND   = auto()   
    LAMBDA = auto()   
    LET    = auto()   
    LPAREN = auto()
    RPAREN = auto()   
    EOF    = auto() #end of input


class Token:
    def __init__(self, ttype: 'TokenType', value=None):
        self.type = ttype 
        self.value = value 

    def __repr__(self):
        return self.type.name if self.value is None else f"{self.type.name}({self.value})"


#this section maps specific UNICODE characters to token types to recognise
#single -character symbols quickly
SINGLE = {
    '\u002B': TokenType.PLUS,    # +
    '\u2212': TokenType.MINUS,   # − 
    '\u00D7': TokenType.MULT,    # × 
    '\u003D': TokenType.EQUALS,  # =
    '\u003F': TokenType.COND,    # ?
    '\u03BB': TokenType.LAMBDA,  # λ
    '\u225C': TokenType.LET,   
    '\u0028': TokenType.LPAREN,  # (
    '\u0029': TokenType.RPAREN,  # )
}

def _is_ascii_letter(ch):
    return ('A' <= ch <= 'Z') or ('a' <= ch <= 'z')

def _is_ascii_digit(ch):
    return '0' <= ch <= '9'

class Lexer:
    @staticmethod
    #loops through input string character by characer to decide what each part represents and collects tokens
    def tokenize(src: str):
        i, n = 0, len(src)
        out = []

        while i < n:
            ch = src[i]

            #skip whitespace
            if ch.isspace():
                i += 1
                continue

            #recognise single character tokens
            ttype = SINGLE.get(ch)
            if ttype is not None:
                out.append(Token(ttype))
                i += 1
                continue

        # NUMBER: [0-9]
            if _is_ascii_digit(ch):
                start = i
                i += 1
                while i < n and _is_ascii_digit(src[i]):
                    i += 1
                out.append(Token(TokenType.NUMBER, int(src[start:i])))
                continue

            # IDENTIFIERS: [A-Za-z][A-Za-z0-9]*
            if _is_ascii_letter(ch):
                start = i
                i += 1
                while i < n and (_is_ascii_letter(src[i]) or _is_ascii_digit(src[i])):
                    i += 1
                out.append(Token(TokenType.IDENT, src[start:i]))
                continue

            if ch == '-' or ch == 'x': 
                raise ValueError("Incorrect Operator Used")
            raise ValueError("Unknown Character")

        #end of input
        out.append(Token(TokenType.EOF))
        return out

#started implementation of ll(1) parser
#this section identifies are allowed and how thye can be built  
GRAMMAR = {
    1:  ("S",["E"]),
    2:  ("E",[TokenType.NUMBER]),
    3:  ("E",[TokenType.IDENT]),
    4:  ("E",[TokenType.LPAREN, "P", TokenType.RPAREN]),
    5:  ("P",[TokenType.PLUS,  "E", "E"]),
    6:  ("P",[TokenType.MINUS, "E", "E"]),
    7:  ("P",[TokenType.MULT,  "E", "E"]),
    8:  ("P",[TokenType.EQUALS,"E", "E"]),
    9:  ("P",[TokenType.COND,  "E", "E", "E"]),
    10: ("P",[TokenType.LAMBDA, TokenType.IDENT, "E"]),
    11: ("P",[TokenType.LET,    TokenType.IDENT, "E", "E"]),
    12: ("P",["E", "E'"]),
    13: ("E'",["E", "E'"]),
    14: ("E'",[]),  # ε
}


#tells parser which grammar rule to use based on what is being looked at
TABLE = {
    # Row S
    ("S",TokenType.NUMBER): 1,
    ("S",TokenType.IDENT):  1,
    ("S",TokenType.LPAREN): 1,

    # Row E
    ("E",TokenType.NUMBER): 2,
    ("E",TokenType.IDENT):  3,
    ("E",TokenType.LPAREN): 4,

    # Row P
    ("P",TokenType.NUMBER): 12,  
    ("P",TokenType.IDENT):  12,   
    ("P",TokenType.LPAREN): 12,   
    ("P",TokenType.PLUS):   5,
    ("P",TokenType.MINUS):  6,
    ("P",TokenType.MULT):   7,
    ("P",TokenType.EQUALS): 8,
    ("P",TokenType.COND):   9,
    ("P",TokenType.LAMBDA): 10,
    ("P",TokenType.LET):    11,

    # Row E'
    ("E'",TokenType.NUMBER): 13,
    ("E'",TokenType.IDENT):  13,
    ("E'",TokenType.LPAREN): 13,
    ("E'",TokenType.RPAREN): 14, 
}

# Helper Functions to allow parse to work properly
# Helper function (1):
def _terminal_check(token_symbol): 
    # terminals in this case are TokenType values or the special '$' sentinel
    return isinstance(token_symbol, TokenType) or token_symbol == '$'

# Helper Function (2):
def _error_token(token_check: 'Token') -> str:
    # These are token that are readable to work with error messages
    if token_check.type == TokenType.IDENT:
        return f"IDENT({token_check.value})"
    if token_check.type == TokenType.NUMBER:
        return f"NUMBER({token_check.value})"
    return token_check.type.name


# This function implements the standard parsing algorithm that is predictive and uses the table above.
# NOTE: this current implementation does build a parse tree yet (that will be completed in in part B.3). 
def parse(tokens):
    
    i = 0

    grammar_stack = ['$', 'S']

    added_production = []

    # quick getter function that quickly checks what the current token type is that 
    # is currently being looked at
    def current_token_check():
        if i < len(tokens):
            return tokens[i].type
        else:
            return TokenType.EOF

    # Main Stack Loop
    while grammar_stack:
        top_of_stack = grammar_stack.pop()
        current_token = current_token_check()

        # Case (1): the top of the stack is a terminal or '$'
        if _terminal_check(top_of_stack):
            if top_of_stack == '$':
                if current_token == TokenType.EOF:
                    return added_production
                # Error case: in case there is some sort of unexpected input
                if i < len(tokens):
                    case_error = _error_token(tokens[i])
                else:
                    case_error = "EOF"
                raise SyntaxError(f"Syntax error: there was an unexpected end of input which was {case_error}")

            # But if the top is actually a real terminal, we match the current token
            if current_token == top_of_stack:
                i += 1
                continue
            
            # error case check (wont add now, only add if needed later)
        
        # Case (2): the top of the stack is a non terminal
        else:
            # here we check to see what production needs to be used
            prod_index = (top_of_stack, current_token)
            production_number = TABLE.get(prod_index)

            # Error case: if there is no apparant table entry, this is an error
            if production_number is None:
                if i < len(tokens):
                    case_error = _error_token(tokens[i])
                else:
                    case_error = "EOF"
                raise SyntaxError(f"Syntax Error: no rule for the current top of stack")
            
            # grabbing the chosen production
            rhs = GRAMMAR[production_number]

            # we save the production number that we will be using
            added_production.append(production_number)

            # Finally, we apply the production by pushing the rhs onto the stack in reverse order
            # this is important so that the leftmost sybmol is processed next
            for token_symbol in reversed(rhs):
                grammar_stack.append(token_symbol)








                


if __name__ == "__main__":
    print(Lexer.tokenize("42y"))
    print(Lexer.tokenize("(+ 12 3)"))

