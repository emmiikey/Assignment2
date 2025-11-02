# Part B: Implementation (Lexer, Parse Table, Parse tree)

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
# \\\ this function is for the "B.2" part of the implemenation ///
def _terminal_check(token_symbol): 
    # terminals in this case are TokenType values or the special '$' sentinel
    return isinstance(token_symbol, TokenType) or token_symbol == '$'

# Helper Function (2):
# \\\ this function is for the "B.2" part of the implemenation ///
def _error_token(token_check: 'Token') -> str:
    # These are token that are readable to work with error messages
    if token_check.type == TokenType.IDENT:
        return f"IDENT({token_check.value})"
    if token_check.type == TokenType.NUMBER:
        return f"NUMBER({token_check.value})"
    return token_check.type.name

# Helper Function (3):
# \\\ this helper function is for the "B.3 parse tree output" part of the implementation ///
# helps push the build marker and rhs
def _push_build_and_rhs(grammar_stack, production_number, rhs):
    # a BUILD marker is placed under the rhs so it will be popped
    # after all rhs symbols have been matched and their values have been pushed
    # onto a different stack
    grammar_stack.append(('BUILD', production_number))
    for token_symbol in reversed(rhs):
        grammar_stack.append(token_symbol)

# Helper Function (4):
# \\\ this helper function is for the "B.3 parse tree output" part of the implementation ///
# helps perform the actual tree building
def _reduce_node(production_number, tree_stack):
    # based on the given production number, we pop the necessary values from the tree
    # stack and push the node back 

    # Case (1): S to E
    if production_number == 1:
        e = tree_stack.pop()
        tree_stack.append(e)
    
    # Case (2): E to NUMBER
    elif production_number == 2:
        # since the numbers value is already on the stack, there is nothing to change
        pass

    # Case (3): E to IDENT
    elif production_number == 3:
        # IDENT value is already on the stack, so nothing that needs to be changed
        pass

    # Case (4): E to 'P'
    elif production_number == 4:
        p = tree_stack.pop()
        tree_stack.append(p)
    
    # Case (5): E to PLUS E E
    elif production_number == 5:
        second_e = tree_stack.pop()
        first_e = tree_stack.pop()
        tree_stack.append(['PLUS', first_e, second_e])

    # Case (6): P to MINUS E E
    elif production_number == 6:
        second_e = tree_stack.pop()
        first_e = tree_stack.pop()
        tree_stack.append(['MINUS', first_e, second_e])
    
    # Case (7): P to MULT E E
    elif production_number == 7:
        second_e = tree_stack.pop()
        first_e = tree_stack.pop()
        tree_stack.append(['MULT', first_e, second_e])

    # Case (8): P to EQUALS E E
    elif production_number == 8:
        second_e = tree_stack.pop()
        first_e = tree_stack.pop()
        tree_stack.append(['EQUALS', first_e, second_e])

    # Case (9): P to COND E E E
    elif production_number == 9:
        third_e = tree_stack.pop()
        second_e = tree_stack.pop()
        first_e = tree_stack.pop()
        tree_stack.append(['COND', first_e, second_e, third_e])
    
    # Case (10): P to LAMBDA IDENT E
    elif production_number == 10:
        e = tree_stack.pop()
        ident = tree_stack.pop()
        tree_stack.append(['LAMBDA', ident, e])
    
    # Case (11): P to LET IDENT E E
    elif production_number == 11:
        second_e = tree_stack.pop()
        first_e = tree_stack.pop()
        ident = tree_stack.pop()
        tree_stack.append(['LET', ident, first_e, second_e])
    
    # Case (12): P to E E'
    elif production_number == 12:
        e_list = tree_stack.pop()
        prev_e = tree_stack.pop()
        if len(e_list) == 0:
            tree_stack.append(prev_e)
        else:
            tree_node = ['APPLY', prev_e]
            tree_node.extend(e_list)
            tree_stack.append(tree_node)
    
    # Case (13): E' to E E'
    elif production_number == 13:
        second_e = tree_stack.pop()
        first_e = tree_stack.pop()
        final_list = [first_e]
        final_list.extend(second_e)
        tree_stack.append(final_list)
    
    # Case (14): E to ε
    elif production_number == 14:
        tree_stack.append([])
        

# This function implements the standard parsing algorithm that is predictive and uses the table above.
# NOTE: this current implementation includes both the working parts of Part B.2 and B.3. 
def parse(tokens):    
    i = 0

    grammar_stack = ['$', 'S']

    # needed for part b.3 part tree output implementation
    tree_stack = []

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

        # Special case for build tree
        if isinstance(top_of_stack, tuple) and len(top_of_stack) == 2 and top_of_stack[0] == 'BUILD':
            prod_index = top_of_stack[1]
            _reduce_node(prod_index, tree_stack)
            continue
    
        # Case (1): the top of the stack is a terminal or '$'
        if _terminal_check(top_of_stack):
            if top_of_stack == '$':
                if current_token == TokenType.EOF:
                    return tree_stack.pop()
                # Error case: in case there is some sort of unexpected input
                if i < len(tokens):
                    case_error = _error_token(tokens[i])
                else:
                    case_error = "EOF"
                raise SyntaxError(f"Syntax error: expected end of input but saw extra input which was {case_error}")

            if current_token == top_of_stack:
                if top_of_stack == TokenType.NUMBER:
                    tree_stack.append(tokens[i].value)
                elif top_of_stack == TokenType.IDENT:
                    tree_stack.append(tokens[i].value)
                # But if the top is actually a real terminal, we match the current token
                i += 1
                continue
            
            # error case check: being added now since we need to check if the top is a real terminal
            # but it may not match the current token
            if i < len(tokens):
                case_error = _error_token(tokens[i])
            else:
                case_error = "EOF"
            raise SyntaxError(f"Syntax Error: expected the top of the stack but got a different expected token, {case_error}")
        
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
                raise SyntaxError(f"Syntax Error: no rule for the current top of stack, instead we saw {case_error}")
            
            # grabbing the chosen production
            rhs = GRAMMAR[production_number][1]

            # we save the production number that we will be using
            added_production.append(production_number)

            _push_build_and_rhs(grammar_stack, production_number, rhs)


if __name__ == "__main__":
    print(Lexer.tokenize("42y"))
    print(Lexer.tokenize("(+ 12 3)"))

