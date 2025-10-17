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
    EOF    = auto() 


class Token:
    def __init__(self, ttype: 'TokenType', value=None):
        self.type = ttype 
        self.value = value 

    def __repr__(self):
        return self.type.name if self.value is None else f"{self.type.name}({self.value})"

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
    def tokenize(src: str):
        i, n = 0, len(src)
        out = []

        while i < n:
            ch = src[i]

            if ch.isspace():
                i += 1
                continue

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

            # IDENT: [A-Za-z]*
            if _is_ascii_letter(ch):
                start = i
                i += 1
                while i < n and (_is_ascii_letter(src[i]) or _is_ascii_digit(src[i])):
                    i += 1
                out.append(Token(TokenType.IDENT, src[start:i]))
                continue

            i += 1
            continue

        out.append(Token(TokenType.EOF))
        return out

if __name__ == "__main__":
    print(Lexer.tokenize("42y"))
    print(Lexer.tokenize("(+ 12 3)"))
