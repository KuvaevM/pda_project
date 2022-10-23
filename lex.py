import ply.lex as lex
import sys

tokens = [
    'TERMINAL',
    'NONTERMINAL',
    'START',
    'EMPTY',
    'EQ',
    'PIPE',
    'SEP'
]


def t_TERMINAL(t):
    r'\`.+?(?<!\\)\`'
    t.value = t.value[1:-1]
    return t


def t_NONTERMINAL(t):
    r'\[.+?(?<!\\)\]'
    t.value = t.value[1:-1]
    return t


def t_START(t):
    r'start=\[.+\]'
    t.value = t.value[7:-1]
    return t


t_EQ = r'='
t_PIPE = r'\|'
t_EMPTY = r'EPS'
t_SEP = r';'

t_ignore = ' \t'


def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)


def t_error(t):
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)


lexer = lex.lex()


def main():
    if len(sys.argv) != 2:
        print("Usage: python3 <run_file> <input_file>")
        return

    input_file = str(sys.argv[1])
    output_file = input_file + ".out"

    with open(input_file, "r") as input, open(output_file, "w") as output:
        lexer = lex.lex()
        lexer.input("".join(input.readlines()))

        while True:
            tok = lexer.token()
            if not tok:
                break
            print(tok, file=output)


if __name__ == "__main__":
    main()
