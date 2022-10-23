import ply.yacc as yacc
import sys
from functools import reduce
import pathlib

from typing import Set, List, Union
from dataclasses import dataclass

from lex import tokens


# Bind : NONTERMINAL EQ Enumeration

# Enumeration : Enumeration PIPE Sequence
#             | Sequence

# Sequence : Single
#          | Sequence Single

# Single : NONTERMINAL
#        | TERMINAL
#        | EMPTY


def removesuffix(input_string, suffix):
    if suffix and input_string.endswith(suffix):
        return input_string[:-len(suffix)]
    return input_string


@dataclass
class Terminal:
    data: str

    def output(self) -> str:
        result = "Terminal(" + self.data + ")"
        return result


@dataclass
class NonTerminal:
    data: str

    def output(self) -> str:
        result = "NonTerminal(" + self.data + ")"
        return result


@dataclass
class Empty:
    def output(self) -> str:
        result = "Empty"
        return result


Single = Union[NonTerminal, Terminal, Empty]


@dataclass
class Sequence:
    singles: List[Single]

    def output(self) -> str:
        result = "Sequence("
        for item in self.singles:
            result += item.output() + ", "
        result = removesuffix(result, ", ")
        result += ")"
        return result


@dataclass
class Enumeration:
    sequences: List[Sequence]

    def output(self) -> str:
        result = "Enumeration("
        for item in self.sequences:
            result += item.output() + ", "
        result = removesuffix(result, ", ")
        result += ")"
        return result


@dataclass
class Bind:
    source: NonTerminal
    description: Enumeration

    def output(self) -> str:
        result = self.source.output() + " = "
        result += self.description.output()
        return result


@dataclass
class Grammar:
    terminals: Set[str]
    nonterminals: Set[str]
    start: str
    binds: List[Bind]

    def output(self) -> str:
        result = "Grammar's description:\n"
        result += "Start: " + self.start + "\n"
        result += "Terminals: "
        for terminal in self.terminals:
            result += terminal + ", "
        result = removesuffix(result, ", ")
        result += "\n"
        result += "NonTerminals: "
        for nonterminal in self.nonterminals:
            result += nonterminal + ", "
        result = removesuffix(result, ", ")
        result += "\n"
        result += "Rules:\n"
        for rule in self.binds:
            result += rule.output() + "\n"
        return result


def get_terminals(variant: Union[Enumeration, Sequence, Single]) -> Set[str]:
    if isinstance(variant, Terminal):
        return set([variant.data])
    res = set()
    if isinstance(variant, Enumeration):
        for seq in variant.sequences:
            res = res.union(get_terminals(seq))
    if isinstance(variant, Sequence):
        for sin in variant.singles:
            res = res.union(get_terminals(sin))
    return res


def get_nonterminals(variant: Union[Enumeration, Sequence, Single]) -> Set[str]:
    if isinstance(variant, NonTerminal):
        return set([variant.data])
    res = set()
    if isinstance(variant, Enumeration):
        for seq in variant.sequences:
            res = res.union(get_nonterminals(seq))
    if isinstance(variant, Sequence):
        for sin in variant.singles:
            res = res.union(get_nonterminals(sin))
    return res


def grammar(start: str, rules: List[Bind]) -> Grammar:
    terminals = set()
    nonterminals = set()
    for bind in rules:
        terminals = terminals.union(get_terminals(bind.description))
        nonterminals.add(bind.source.data)
        nonterminals = nonterminals.union(get_nonterminals(bind.description))
    return Grammar(terminals, nonterminals, start, rules)


def p_grammar(p):
    'grammars : START Rules'
    p[0] = grammar(p[1], p[2])


def p_rules(p):
    """Rules : Bind
             | Rules Bind"""
    if len(p) == 3:
        p[0] = p[1] + [p[2]]
    else:
        p[0] = [p[1]]


def p_bind(p):
    'Bind : NONTERMINAL EQ Enumeration SEP'
    p[0] = Bind(NonTerminal(p[1]), Enumeration(p[3]))


def p_enumeration(p):
    """Enumeration : Enumeration PIPE Sequence
                   | Sequence"""
    if len(p) == 2:
        p[0] = [Sequence(p[1])]
    else:
        p[0] = p[1] + [Sequence(p[3])]


def p_sequence(p):
    """Sequence : Single
                | Sequence Single"""
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[2]]


def p_empty(p):
    'Single : EMPTY'
    p[0] = Empty()


def p_terminal(p):
    'Single : TERMINAL'
    p[0] = Terminal(p[1])


def p_nonterminal(p):
    'Single : NONTERMINAL'
    p[0] = NonTerminal(p[1])


def p_error(p):
    if p is None:
        token = "end of file"
    else:
        token = f"{p.type}({p.value}) on line {p.lineno}"

    print(f"Syntax error: Unexpected {token}")


def main():
    if len(sys.argv) != 2:
        print("Usage: python3 <run_file> <input_file>")
        return

    input_file = str(sys.argv[1])
    output_file = input_file + ".out"

    with open(input_file, "r") as f_input, open(output_file, "w") as f_output:
        parser = yacc.yacc(start="grammars")
        grammars = parser.parse("".join(f_input.readlines()))
        print(grammars.output(), file=f_output)


if __name__ == "__main__":
    main()
