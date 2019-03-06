
import argparse
import sys
import re


def output(line):
    print(line)


def grep(lines, params):
    # For lines that were used before. For context intersections
    outputted_keys = []
    for number_line, line in enumerate(lines):
        pattern = params.pattern
        if '?' in pattern:
            pattern = pattern.replace('?', '.')
        if '*' in pattern:
            pattern = pattern.replace('*', '\w*')
        params_list = [pattern, line]
        if params.ignore_case:
            params_list.append(re.IGNORECASE)
        searched = re.search(*params_list)
        found = not searched and params.invert or searched and not params.invert
        if found:
            start = number_line - (params.before_context or params.context or 0)
            number_lines_to_add = params.after_context or params.context or 0
            end = number_line + number_lines_to_add if len(lines) > number_line + number_lines_to_add else len(lines) - 1

            # +1 Because of including
            # Getting used keys
            line_keys = [c for c in range(start, end + 1) if c not in outputted_keys]
            outputted_keys.extend(range(start, end + 1))

            for key in line_keys:
                output_string = lines[key]
                if params.count:
                    output_string = str(len(searched.group()))
                # Change delimeter if string is in context
                delimeter = '-' if params.context and not re.search(*[pattern, lines[key]]) else ':'
                output('{}{}{}'.format(key + 1, delimeter, output_string) if params.line_number else output_string)



def parse_args(args):
    parser = argparse.ArgumentParser(description='This is a simple grep on python')
    parser.add_argument(
        '-v', action="store_true", dest="invert", default=False, help='Selected lines are those not matching pattern.')
    parser.add_argument(
        '-i', action="store_true", dest="ignore_case", default=False, help='Perform case insensitive matching.')
    parser.add_argument(
        '-c',
        action="store_true",
        dest="count",
        default=False,
        help='Only a count of selected lines is written to standard output.')
    parser.add_argument(
        '-n',
        action="store_true",
        dest="line_number",
        default=False,
        help='Each output line is preceded by its relative line number in the file, starting at line 1.')
    parser.add_argument(
        '-C',
        action="store",
        dest="context",
        type=int,
        default=0,
        help='Print num lines of leading and trailing context surrounding each match.')
    parser.add_argument(
        '-B',
        action="store",
        dest="before_context",
        type=int,
        default=0,
        help='Print num lines of trailing context after each match')
    parser.add_argument(
        '-A',
        action="store",
        dest="after_context",
        type=int,
        default=0,
        help='Print num lines of leading context before each match.')
    parser.add_argument('pattern', action="store", help='Search pattern. Can contain magic symbols: ?*')
    return parser.parse_args(args)


def main():
    params = parse_args(sys.argv[1:]) 
    grep(sys.stdin.readlines(), params)

if __name__ == '__main__':
    main()
