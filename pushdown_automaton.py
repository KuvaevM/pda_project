import sys
from functools import reduce
import pathlib
import ply.yacc as yacc

from parse import *
from automat_demo import automat_demo
from test_automat_demo import test_automat_demo

from typing import Set, List, Union
from dataclasses import dataclass


@dataclass
class Left:
    state: str
    input_symbol: Terminal
    stack_symbol: NonTerminal

    def output(self):
        result = "\t\tLeft: {\n\t\t\tState: "
        result += self.state
        result += '\n\t\t\tInput symbol: '
        result += self.input_symbol.output()
        result += '\n\t\t\tStack symbol: '
        result += self.stack_symbol.output()
        result += '\n\t\t}\n'
        return result


@dataclass
class Right:
    state: str
    stack_sequence: Sequence

    def output(self):
        result = "\t\tRight: {\n\t\t\tState: "
        result += self.state
        result += '\n\t\t\tStack sequence: '
        result += self.stack_sequence.output()
        result += '\n\t\t}\n'
        return result


@dataclass
class Rule:
    left: Left
    right: Right

    def output(self):
        result = "\tRule: {\n"
        result += self.left.output()
        result += self.right.output()
        result += '\t}\n'
        return result


@dataclass
class PushdownAutomaton:
    states: List[str]
    input_alphabet: Set[str]
    stack_alphabet: Set[str]
    start_state: str
    start_stack_element: str
    rules: List[Rule]
    grammar_correct: bool

    def output(self):
        result = 'States: '
        for state in self.states:
            result += state + ' '
        result += '\n'

        result += 'Input alphabet: '
        for alpha in self.input_alphabet:
            result += alpha + ', '
        result = result.removesuffix(', ')
        result += '\n'

        result += 'Stack alphabet: '
        for alpha in self.stack_alphabet:
            result += alpha + ', '
        result = result.removesuffix(', ')
        result += '\n'

        result += 'Start state: '
        result += self.start_state
        result += '\n'

        result += 'Start stack element: '
        result += self.start_stack_element
        result += '\n'

        result += 'Rules: {\n'
        for rule in self.rules:
            result += rule.output()
        result += '}'
        return result

    def is_grammar_correct(self):
        return self.grammar_correct


def build_automaton(gram: Grammar) -> PushdownAutomaton:
    states = ["q0"]
    rules = []
    input_alphabet = gram.terminals
    stack_alphabet = gram.nonterminals
    start_state = states[0]
    start_stack_element = gram.start
    grammar_correct = True
    for bind in gram.binds:
        for sequence in bind.description.sequences:

            if not (isinstance(sequence.singles[0], Empty) or isinstance(sequence.singles[0], Terminal)):
                grammar_correct = False

            left = Left(states[0], sequence.singles[0], bind.source)
            if len(sequence.singles) == 1:
                right = Right(states[0], Sequence([Empty()]))
            else:
                if len(get_terminals(sequence)) > 1:
                    grammar_correct = False

                right = Right(states[0], Sequence(sequence.singles[1::]))

            rules.append(Rule(left, right))

    return PushdownAutomaton(states, input_alphabet, stack_alphabet, start_state, start_stack_element, rules, grammar_correct)


def main():
    if len(sys.argv) != 2:
        print("Usage: python3 <run_file> <input_file>")
        return

    input_file = str(sys.argv[1])
    output_file = input_file + ".out"

    is_correct_automat = True
    automaton_demo = None

    with open(input_file, "r") as f_input, open(output_file, "w") as f_output:
        parser = yacc.yacc(start="grammars")
        grammars = parser.parse("".join(f_input.readlines()))
        pushdown_automaton = build_automaton(grammars)
        automaton_demo = pushdown_automaton
        if not pushdown_automaton.is_grammar_correct():
            print("This grammar is not in Greibach normal form.", file=f_output)
            is_correct_automat = False
        else:
            print(pushdown_automaton.output(), file=f_output)
    if is_correct_automat:
        print("Please choose testing or interactive mode (write test for testing, all other strings for interactive):")
        mode = input()
        if mode == "test":
            print("Please enter a filename of file from automative_tests:")
            input_file = input()
            test_automat_demo(automaton_demo, "automate_tests/"+input_file)
        else:
            print("Please enter a string for automat work demonstration:")
            input_str = input()
            automat_demo(automaton_demo, input_str)

    else:
        print("Sorry, the grammar isn't coorect, the automat doesn't exist.")


if __name__ == "__main__":
    main()
