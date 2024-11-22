#! /usr/bin/env python3

import argparse
import sys
import os
import re
import src.search_patterns
import src.rules
import src.files
import settings
import src.literal_manipulation
import src.logging
from src.SearchPattern import SearchPattern
from src.literal_manipulation import negate, variable_from_literal
from src.logging import log
from src.sat_solvers import Status, sat_solve
from src.UnsatInPreprocessing import UnsatInPreprocessing

parser = argparse.ArgumentParser()
parser.add_argument(
    'input_file_name',
    nargs='?',
    default=None,
    help="Name of file containing search pattern. LLS looks in current directory and then search_patterns/"
)
parser.add_argument(
    '-b', '--blank_search_pattern',
    nargs="+",
    type=int,
    metavar="BOUNDS",
    default=None,
    help="""Creates a blank_search_pattern with size BOUND_1 by BOUND_2, and duration BOUND_3. If BOUND_3 isn't present, assume duration is period + 1. If BOUND_2 isn't present, assume bounding box is square."""
)

parser.add_argument(
    '-s', '--symmetry',
    nargs="*",
    action="append",
    default=[],
    help="""Impose a symmetry on the pattern Examples: "D4x" enforces reflection symmetry about both axes, "p7" enforces period 7, "p2 RE\ x1" imposes the glide-reflect symmetry of a glider."""
)
parser.add_argument(
    '-a', '--asymmetry',
    nargs="*",
    action="append",
    default=[],
    help="""Impose an asymmetry on the pattern."""
)
parser.add_argument(
    '-c', '--force_change',
    nargs="*",
    action="append",
    type=int,
    default=[],
    help='Forces the first two generations to be different, or the two given generations to be different'
)
parser.add_argument(
    "-p", "--population", "--pop",
    action='append',
    nargs="*",
    default=[],
    metavar=("constraint", "GEN_0"),
    help=""""Imposes a constraint on the population. Examples: "<10", ">=20", "=15". The population is measured in the first generation by default, or otherwise summed over all generations mentioned."""
)
parser.add_argument(
    '-o', '--output_file_name',
    default=None,
    help='File for the output to be saved to'
)
parser.add_argument(
    '-M', '--method',
    type=int,
    default=None,
    help='Which method to encode transitions in CNF (default is "1" for Life, and "2" otherwise)'
)
parser.add_argument(
    '-S', '--solver',
    default=None,
    help='Which SAT solver to use (default is glucose-syrup)'
)
parser.add_argument(
    '-t', '--timeout',
    type=int,
    default=None,
    help='Program will time out if the solver runs for longer than TIMEOUT seconds'
)
parser.add_argument(
    '--csv',
    action='store_const',
    default=None,
    const="csv",
    help="Give output in csv format rather than the usual RLE."
)
parser.add_argument(
    '-V', '--version',
    action="store_true",
    help='Displays the version number'
)
parser.add_argument(
    '-v', '--verbosity',
    type=int,
    default=settings.verbosity,
    help="""Set the verbosity. Options: 0 - No output. Only useful with -o option to save solution to file. 1 - Only display the solution. 2 (Default) - Displays some information about what the program is doing, some statistics, and the solution. 3 - A huge torrent of information."""
)
parser.add_argument(
    "-n", "--number_of_solutions",
    type=int,
    nargs="?",
    default=1,
    const=float('inf'),
    help="Number of solutions to find, or (if no number is given) all of them."
)
parser.add_argument(
    "--save_dimacs",
    nargs="?",
    default=None,
    const=True,
    help="Save the DIMACS file (to the given filename, or to a default if one isn't given)"
)
parser.add_argument(
    "--save_state",
    nargs="?",
    default=None,
    const=True,
    help="Save the state (to the given filename, or to a default if one isn't given)"
)
parser.add_argument(
    "--dry_run",
    action="store_true",
    help="Don't run the solver, but do preprocess."
)
parser.add_argument(
    '--parameters',
    type=str,
    default=None,
    help='Parameters to pass to the SAT solver. Note that you have to use the format like --parameters="-nthreads=8", or else Python\'s argparse will have a hissy fit.'
)
parser.add_argument(
    "-r", '--rule',
    type=str,
    default=None,
    help="""Which rule to use. Rules can also be specified as partial rules, by adding a "p" to the front. For example "pB3a-c/S23" allows any of the transitions from Life, except 3a must be present and 3c must not. Can also specify rule as a Python dictionary, like so: {'S4e': '0', 'S4a': '0', 'S4c': '0', 'S4n': '0', 'S4i': '0', 'S4j': '0', 'S4k': '0', 'S4t': '0', 'S4w': '0', 'S4q': '0', 'S4r': '0', 'S4y': '0', 'S4z': '0', 'B2n': '0', 'B2k': '0', 'B2i': '0', 'B2e': '0', 'B2c': '0', 'B2a': '0', 'S5e': '0', 'S5c': '0', 'S5a': '0', 'S5n': '0', 'S5k': '0', 'S5j': '0', 'S5i': '0', 'S5r': '0', 'S5q': '0', 'S5y': '0', 'B5y': '0', 'B5r': '0', 'B5q': '0', 'B5j': '0', 'B5k': '0', 'B5i': '0', 'B5n': '0', 'B5c': '0', 'B5a': '0', 'B5e': '0', 'S6n': '0', 'B0c': '0', 'S6k': '0', 'S6i': '0', 'S6e': '0', 'S6c': '0', 'S6a': '0', 'B8c': '0', 'S7c': '0', 'S7e': '0', 'B3y': 'r_7', 'B3q': 'r_5', 'B3r': 'r_6', 'B3n': 'r_4', 'B3i': 'r_1', 'B3j': 'r_2', 'B3k': 'r_3', 'B3e': 'r_0', 'B3a': '1', 'B3c': '0', 'S8c': '0', 'B6c': '0', 'B6a': '0', 'B6e': '0', 'B6k': '0', 'B6i': '0', 'S0c': '0', 'B6n': '0', 'B1e': '0', 'B1c': '0', 'S1c': '0', 'S1e': '0', 'S2c': 'r_9', 'S2a': 'r_8', 'S2e': 'r_10', 'S2k': 'r_12', 'S2i': 'r_11', 'S2n': 'r_13', 'B4t': '0', 'B4w': '0', 'B4q': '0', 'B4r': '0', 'B4y': '0', 'B4z': '0', 'B4e': '0', 'S3n': 'r_20', 'B4a': '0', 'B4c': '0', 'B4n': '0', 'B4i': '0', 'B4k': '0', 'B4j': '0', 'S3y': 'r_23', 'S3q': 'r_21', 'S3r': 'r_22', 'B7c': '0', 'S3i': 'r_17', 'B7e': '0', 'S3k': 'r_19', 'S3j': 'r_18', 'S3e': 'r_16', 'S3a': 'r_14', 'S3c': 'r_15'}"""
)
parser.add_argument(
    '--background', "--bg",
    nargs=1,
    default=None,
    help="""Specify a background, default is vacuum"""
)
parser.add_argument(
    '--background_offset', "--bgos",
    nargs=3,
    type=int,
    default=None,
    help="""Specify a background offset"""
)
parser.add_argument(
    '--max_change',
    type=int,
    default=None,
    help='Maximum number of cells allowed to differ from how they are in the first generation'
)
parser.add_argument(
    '--max_decay',
    type=int,
    default=None,
    help='Maximum number of live cells allowed to differ from how they are in the first generation'
)
parser.add_argument(
    '--max_growth',
    type=int,
    default=None,
    help='Maximum number of dead cells allowed to differ from how they are in the first generation'
)
args = parser.parse_args()

lls_dir = os.path.dirname(os.path.realpath(__file__))

src.logging.verbosity_level = args.verbosity

if args.version:
    log('4', 0, 1)
    sys.exit()
pattern_output_format = args.csv
output_file_name = args.output_file_name

log('Getting search pattern...', 1, 2)


force_change = []
for generations in args.force_change:
    assert len(generations) in [0, 2], "Wrong number of arguments to -c"
    if len(generations) == 0:
        force_change.append([0, 1])
    elif len(generations) == 2:
        force_change.append(generations)

population_at_most = []
population_at_least = []
population_exactly = []
for arguments in args.population:
    if len(arguments) == 0:
        population_at_least.append([[0], 1])
    else:
        constraint = arguments[0]
        times = [int(t) for t in arguments[1:]] if len(arguments) > 1 else [0]
        re_match = re.match("(^.*?)([0-9]*$)", constraint)
        sign = re_match.group(1)
        amount = int(re_match.group(2))
        if sign in ["", "="]:
            population_exactly.append([times, amount])
        elif sign in ["<=", "=<"]:
            population_at_most.append([times, amount])
        elif sign in [">=", "=>"]:
            population_at_least.append([times, amount])
        elif sign == "<":
            population_at_most.append([times, amount - 1])
        elif sign == ">":
            population_at_least.append([times, amount + 1])

symmetries = []
asymmetries = []
max_period = 0
for symmetry_list, argument_list in [(symmetries, args.symmetry), (asymmetries, args.asymmetry)]:
    for arguments in argument_list:
        transformations = []
        period = None
        x_translate = None
        y_translate = None
        for argument in arguments:
            re_match = re.match("(^.*?)([0-9]*$)", argument)
            letters = re_match.group(1).upper()
            number = re_match.group(2)
            if letters == "P":
                assert period is None, "Can only have one period at a time"
                period = int(number)
                max_period = max(max_period, period)
            elif letters == "X":
                assert x_translate is None, "Can only have one x_translate at a time"
                x_translate = int(number)
            elif letters == "Y":
                assert y_translate is None, "Can only have one y_translate at a time"
                y_translate = int(number)
            else:
                assert transformations == [], "Can only impose one symmetry at a time"
                transformation = letters + str(number)
                if letters == "RO":
                    transformations.append(letters + str(int(number) % 4))
                elif transformation == "C1":
                    transformations.append("RO0")
                elif transformation == "C2":
                    transformations.append("ro2")
                elif transformation == "C4":
                    transformations.append("ro1")
                elif transformation == "D2-":
                    transformations.append("re-")
                elif transformation == "D2\\":
                    transformations.append("re\\")
                elif transformation == "D2|":
                    transformations.append("re|")
                elif transformation == "D2/":
                    transformations.append("re/")
                elif transformation == "D4+":
                    transformations += ["re-", "re|"]
                elif transformation == "D4X":
                    transformations += ["re/", "re\\"]
                elif transformation == "D8":
                    transformations += ["re-", "re\\"]
                else:
                    assert transformation in ["RE-", "RE/", "RE|",
                                              "RE\\"], 'Symmetry argument "' + transformation + '" not recognized'
                    transformations.append(transformation)
        if not transformations:
            transformations = ["RO0"]
        if period is None:
            period = 0
        if x_translate is None:
            x_translate = 0
        if y_translate is None:
            y_translate = 0
        for transformation in transformations:
            symmetry_list.append(
                [transformation, x_translate, y_translate, period])

solutions_remaining = 0 if args.dry_run else args.number_of_solutions

ignore_transition = None  # Default value
rule = src.rules.rule_from_rulestring(args.rule)

# Add "user_input_" to user's variable names, to prevent collisions"
if args.rule is not None and args.rule.strip()[0] == "{":
    for transition, literal in rule.items():
        if literal not in ["0", "1"]:
            variable, negated = variable_from_literal(literal)
            literal = negate("user_input_" + variable, negated)
            rule[transition] = literal

if args.background:
    # Check current directory and then backgrounds/
    log('Creating background from file "' + args.background[0] + '" ...', 1)
    if os.path.isfile(args.background[0]):
        input_string = src.files.string_from_file(args.background[0])
    elif os.path.isfile(lls_dir +
                        "/backgrounds/" + args.background[0]):
        input_string = src.files.string_from_file(
            lls_dir + "/backgrounds/" + args.background[0])
    else:
        assert False, "Search pattern file not found"
    background_grid, background_ignore_transition = src.search_patterns.search_pattern_from_string(
        input_string)
    log('Done\n', -1)
else:
    (
        background_grid,
        background_ignore_transition
    ) = src.search_patterns.search_pattern_from_string(
        src.files.string_from_file(lls_dir +
                                   "/backgrounds/" + settings.background,
                                   )
    )

if args.background_offset:
    src.literal_manipulation.offset_background(
        background_grid, *args.background_offset)
    src.literal_manipulation.offset_background(
        background_ignore_transition, *args.background_offset)


if args.input_file_name and args.blank_search_pattern:
    raise Exception("Too many search patterns specified")

if args.input_file_name:
    # Check current directory and then search_pattern/
    log('Creating search pattern from file "' + args.input_file_name + '" ...', 1)
    if os.path.isfile(args.input_file_name):
        input_string = src.files.string_from_file(args.input_file_name)
    elif os.path.isfile(lls_dir + "/search_patterns/" + args.input_file_name):
        input_string = src.files.string_from_file(
            lls_dir + "/search_patterns/" + args.input_file_name)
    else:
        assert False, "Search pattern file not found"
    grid, ignore_transition = src.search_patterns.search_pattern_from_string(
        input_string)
    log('Done\n', -1)

elif args.blank_search_pattern:
    assert len(args.blank_search_pattern) in range(
        1, 4), "Wrong number of arguments for bounding box"
    if len(args.blank_search_pattern) == 1:
        width = args.blank_search_pattern[0]
        height = args.blank_search_pattern[0]
        duration = max_period + 1
    elif len(args.blank_search_pattern) == 2:
        width = args.blank_search_pattern[0]
        height = args.blank_search_pattern[1]
        duration = max_period + 1
    elif len(args.blank_search_pattern) == 3:
        width = args.blank_search_pattern[0]
        height = args.blank_search_pattern[1]
        duration = args.blank_search_pattern[2]
    else:
        raise Exception("Wrong number of arguments for bounding box")
    grid = src.search_patterns.blank_search_pattern(width, height, duration)
else:
    log('\nNo pattern specified, getting from STDIN... (End with EOF character)\n', 0, 2)
    input_string = sys.stdin.read()
    log('\n', 0, 2)
    grid, ignore_transition = src.search_patterns.search_pattern_from_string(
        input_string)

# Create the search pattern
search_pattern = SearchPattern(
    grid,
    ignore_transition=ignore_transition,
    background_grid=background_grid,
    background_ignore_transition=background_ignore_transition,
    rule=rule
)

log('Done\n', -1, 2)
log('Preprocessing...', 1, 2)

try:
    # Constraints that change the grid
    search_pattern.standardise_variables_names()
    for symmetry in symmetries:
        search_pattern.force_symmetry(symmetry)

    search_pattern.remove_redundancies()
    search_pattern.standardise_variables_names()
except UnsatInPreprocessing:
    log("Unsatisfiability proved in preprocessing", 0, 2)
    log('Done\n', -1, 2)
    sys.exit()

log("Search grid:\n", 1)
log(search_pattern.make_string(pattern_output_format="csv", show_background=True))
log('Done\n', -1)

# Constraints that are enforced by clauses
for asymmetry in asymmetries:
    search_pattern.force_asymmetry(asymmetry)
for constraint in population_at_most:
    search_pattern.force_population_at_most(constraint)
for constraint in population_at_least:
    search_pattern.force_population_at_least(constraint)
for constraint in population_exactly:
    search_pattern.force_population_exactly(constraint)
if args.max_change is not None:
    search_pattern.force_max_change(args.max_change)
if args.max_decay is not None:
    search_pattern.force_max_decay(args.max_decay)
if args.max_growth is not None:
    search_pattern.force_max_growth(args.max_growth)
for times in force_change:
    search_pattern.force_change(times)

# The most important bit. Enforces the evolution rules
search_pattern.force_evolution(method=args.method)

log('Done\n', -1, 2)
save_state = args.save_state
if save_state:
    if isinstance(save_state, str):
        state_file = save_state
    else:
        state_file = src.files.find_free_file_name("lls_state", ".pkl")
    log("Saving state...", 1)
    src.files.file_from_object(
        state_file,
        (search_pattern.grid, search_pattern.ignore_transition, search_pattern.background_grid,
         search_pattern.background_ignore_transition, search_pattern.rule,
         search_pattern.clauses.DIMACS_literal_from_variable)
    )
    log("Done\n", -1)
# Problem statistics
log('Width: ' + str(len(search_pattern.grid[0][0])), 0, 2)
log('Height: ' + str(len(search_pattern.grid[0])), 0, 2)
log('Duration: ' + str(len(search_pattern.grid)) + "\n", 0, 2)
log('Number of undetermined cells: ' +
    str(search_pattern.number_of_cells()), 0, 2)
log('Number of variables: ' + str(search_pattern.clauses.number_of_variables), 0, 2)
log('Number of clauses: ' + str(len(search_pattern.clauses.clause_set)) + "\n", 0, 2)

save_dimacs = args.save_dimacs
if save_dimacs is not None:
    if not isinstance(save_dimacs, str):
        save_dimacs = src.files.find_free_file_name("lls_dimacs", ".cnf")
    search_pattern.clauses.make_file(save_dimacs)

determined = search_pattern.deterministic()
show_background = search_pattern.background_nontrivial()

time_taken = 0
while solutions_remaining > 0:
    (
        status,
        solution,
        extra_time_taken
    ) = sat_solve(
        search_pattern,
        solver=args.solver,
        parameters=args.parameters,
        timeout=args.timeout
    )
    time_taken += extra_time_taken
    if status == Status.SAT:
        solutions_remaining -= 1
        output_string = solution.make_string(
            pattern_output_format=pattern_output_format,
            determined=determined,
            show_background=show_background
        )
    else:
        output_string = status.value
    log(f"live cells: {output_string.count('o')}", 0, 1)
    log(output_string + "\n", 0, 1)
    if output_file_name:
        log('Writing output file...', 1, 2)
        src.files.append_to_file_from_string(output_file_name, output_string)
        log('Done\n', -1, 2)
    if status == Status.SAT and solutions_remaining > 0:
        search_pattern.force_distinct(solution, determined=determined)
    else:
        break

log('Total solver time: ' + str(time_taken), 0, 2)
