import sys

from typing import Set, List
from dataclasses import dataclass

SEPARATOR = " |- "
unsuccessfull_secs = []
success = False


@dataclass
class Step:
    current_state: str
    current_str_sym: str
    end_of_str: str
    current_stack_sym: str
    stack: List
    previous_steps: str


@dataclass
class StepsSeq:
    current_steps: List[Step]

    def add(self, new_step):
        self.current_steps.append(new_step)


def automat_demo(automat, input_str: str) -> None:
    print("This is interactive testing mode of the automat\n Enter <next> to see next steps\n Enter <next \"number\"> "
          "to see steps 2 after current \"number\"")
    pointer = 1

    if input_str == "":
        cmd = input()

        while cmd.split()[0] != "next":
            print("Wrong command! Please, try again.")
            cmd = input()
        flag = False
        for rule in automat.rules:
            if rule.left.state == automat.states[0] and rule.left.input_symbol.output() == "Empty" and \
                    rule.left.stack_symbol.data == automat.start_stack_element:
                print("Automate successfully ended. Step sequence:")
                print(f"({automat.states[0]}, Empty, {automat.start_stack_element}){SEPARATOR}({automat.states[0]},"
                      f" Empty, Empty)")
                flag = True
                break
        if not flag:
            print("String is not accepted by automat. All sequences:")
            print(f"({automat.states[0]}, Empty, {automat.start_stack_element})")
    else:
        first_sym = input_str[0]
        while first_sym not in automat.input_alphabet and pointer <= len(input_str):
            first_sym = input_str[0: pointer]
            pointer += 1
        current_seq = StepsSeq([Step(automat.states[0], first_sym, input_str, automat.start_stack_element,
                                     [automat.start_stack_element],
                                     f"({automat.states[0]}, {input_str}, {automat.start_stack_element})")])
        while len(current_seq.current_steps) != 0:
            cmd = input()
            if len(cmd.split()) == 2 and cmd.split()[0] == "next" and cmd.split()[1].isdigit():
                is_empty = False
                for i in range(int(cmd.split()[1]) - 1):
                    current_seq = StepsSeq(emulate_automate(current_seq, automat))
                    if len(current_seq.current_steps) == 0:
                        is_empty=True
                        break
                if is_empty:
                    break
                current_seq = print_next(current_seq, automat)
            elif cmd == "next":
                current_seq = print_next(current_seq, automat)
            else:
                print("Wrong command! Please, try again.")
        if not success:
            print("String is not accepted by automat. All sequences:")
            for seq in unsuccessfull_secs:
                print(seq)

    #  print(automat.rules[1].right.stack_sequence.output().replace("Sequence(", "", 1)[:-1].split(', ').reverse())


def print_next(current_seq, automat) -> StepsSeq:
    new_seq_steps = emulate_automate(current_seq, automat)
    if success:
        return StepsSeq([])
    for step in new_seq_steps:
        print(step.previous_steps)
    return StepsSeq(new_seq_steps)


def emulate_automate(current_seq, automat) -> List[Step]:
    new_seq_steps = []
    for step in current_seq.current_steps:
        current_sym = step.current_str_sym
        print(current_sym)
        current_stack_top = step.current_stack_sym
        current_state = step.current_state
        suitable_rules = []
        for rule in automat.rules:
            if rule.left.state == current_state and rule.left.input_symbol.output() == "Empty" and \
                    rule.left.stack_symbol.data == current_stack_top:
                suitable_rules.append(rule)
            elif rule.left.input_symbol.output() == "Empty":
                continue
            elif rule.left.state == current_state and rule.left.input_symbol.data == current_sym and \
                    rule.left.stack_symbol.data == current_stack_top:
                suitable_rules.append(rule)
        if len(suitable_rules) == 0:
            unsuccessfull_secs.append(step.previous_steps)
            continue
        for rule in suitable_rules:
            next_end_str = step.end_of_str
            if rule.left.input_symbol.output() != "Empty":
                next_end_str = next_end_str.replace(step.current_str_sym, "", 1)

            next_stack = step.stack.copy()
            next_stack.pop()
            if rule.right.stack_sequence.output() != "Sequence(Empty)":
                new_elems = rule.right.stack_sequence.output().replace("Sequence(", "", 1)[:-1].split(', ')
                new_elems.reverse()
                for stack_elem in new_elems:
                    next_stack.append(stack_elem.replace("NonTerminal(", "", 1)[:-1])
            if len(next_stack) == 0 and len(next_end_str) == 0:
                global success
                success = True
                print("Automate successfully ended. Step sequence:")
                print(step.previous_steps + SEPARATOR + f"({step.current_state}, Empty, Empty)")
                return []
            elif len(next_stack) == 0:
                unsuccessfull_secs.append(step.previous_steps + SEPARATOR + f"({step.current_state}, {next_end_str}, "
                                                                            f"Empty)")
                print(unsuccessfull_secs[-1])
                continue
            elif next_end_str == "":
                unsuccessfull_secs.append(step.previous_steps + SEPARATOR + f"({step.current_state}, Empty, "
                                                                            f"{next_stack[-1]})")
                print(unsuccessfull_secs[-1])
                continue
            next_sym = next_end_str[0]
            pointer = 1
            while not next_sym in automat.input_alphabet and pointer <= len(next_end_str):
                next_sym = next_end_str[0: pointer]
                pointer += 1
            new_previous_steps = (
                    step.previous_steps + SEPARATOR + f"({step.current_state}, {next_end_str}, {next_stack[-1]})")
            new_seq_steps.append(
                Step(step.current_state, next_sym, next_end_str, next_stack[-1], next_stack, new_previous_steps))
    return new_seq_steps
