#!/usr/bin/env python3

from forest.configuration import Configuration
from forest.logger import get_logger
from forest.parse_examples import preprocess
from forest.synthesizer import MultiTreeSynthesizer
from forest.visitor import RegexInterpreter, ToZ3

logger = get_logger('forest')

synthesizer = None


def sig_handler(received_signal, frame):
    print('\nSIGINT or SIGTERM detected. Exiting gracefully.')
    if synthesizer is not None:
        print('Printing the last valid program found.')
        synthesizer.configuration.die = True


def main():
    valid_exs = ["CSCI1710", "CSCI1870", "CSCI1710", "CSCI0220", "CSCI2952"]
    invalid_exs = ["15-814"]

    configuration = Configuration()

    print("Synthesis with disambiguation")
    synthesize(valid_exs, invalid_exs, configuration)

    print("Synthesis without disambiguation (show all solutions)")
    configuration.disambiguation = False
    solutions = synthesize(valid_exs, invalid_exs, configuration)

    # disambiguation by hand:
    # dist_input, keep_if_valid, keep_if_invalid, unknown = \
    #     self._distinguisher.distinguish(self.solutions)
    # if dist_input is not None:
    #     # interaction_start_time = time.time()
    #
    #     valid_answer = False
    #     # Do not count time spent waiting for user input: add waiting time to start_time.
    #     while not valid_answer and not self.configuration.die:
    #         x = input(f'Is "{dist_input}" valid? (y/n)\n')
    #         if x.lower().rstrip() in yes_values:
    #             logger.info(f'"{dist_input}" is {colored("valid", "green")}.')
    #             valid_answer = True
    #             self._decider.add_example([dist_input], True)
    #             self.solutions = keep_if_valid
    #             # self.indistinguishable = 0
    #         elif x.lower().rstrip() in no_values:
    #             logger.info(f'"{dist_input}" is {colored("invalid", "red")}.')
    #             valid_answer = True
    #             self._decider.add_example([dist_input], False)
    #             self.solutions = keep_if_invalid
    #             # self.indistinguishable = 0
    #         else:
    #             logger.info(f"Invalid answer {x}! Please answer 'yes' or 'no'.")
    #
    # else:  # programs are indistinguishable
    #     logger.info("Regexes are indistinguishable")
    #     smallest_regex = min(self.solutions, key=lambda r: len(self._printer.eval(r)))
    #     self.solutions = [smallest_regex]
    # stats.regex_distinguishing_time += time.time() - distinguish_start
    # stats.regex_synthesis_time += time.time() - distinguish_start


def synthesize(valid, invalid, configuration):
    dsl, valid, invalid, _, _, _ = \
        preprocess(valid, invalid, [], False)
    synthesizer = MultiTreeSynthesizer(valid, invalid, [], [], dsl,
                                       "", configuration)
    printer = RegexInterpreter()
    to_z3 = ToZ3()
    program = synthesizer.synthesize()
    solution_regexes = list(map(lambda x: x[0], synthesizer.solutions))
    if program is not None:
        for solution_idx, regex in enumerate(solution_regexes):
            solution_str = printer.eval(regex)
            print(f'Solution #{solution_idx}:  {solution_str} ({regex})')
    else:
        print('Solution not found!')
    return solution_regexes


if __name__ == '__main__':
    main()
