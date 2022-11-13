import re

from utils import is_source_file, is_header_file

import vera

INCLUDE_REGEX = re.compile(r'#define\s+(?:(?:(?P<identifier_function>\w+)\((?P<function_parameters>.*)\))|(?P<identifier_string>.*))\s(?P<token>.+)')


def check_define_usage():
    for file in vera.getSourceFileNames():
        if not is_source_file(file) and not is_header_file(file):
            continue
        tokens = vera.getTokens(file, 1, 0, -1, -1, ["pp_define"])
        for token in tokens:
            line = ""
            count = 0
            while len(line) == 0 or line.endswith('\\'):
                if line.endswith('\\'):
                    line = line[:-1]
                line += vera.getLine(file, token.line + count)
                count += 1

            match = re.match(INCLUDE_REGEX, line.strip())
            if not match:
                continue
            if match['identifier_string'] and match['token'] is not None:
                vera.report(token, "MINOR:C-H3")
            elif match['identifier_function'] and not match['function_parameters'] and match['token'] is not None:
                vera.report(token, "MINOR:C-H3")

            # this code handle some case which are not yet supported like define with parameters
            # and also report if a case is not implemented
            #elif match['identifier_function'] and match['function_parameters'] and match['token'] is not None:
            #    parameters = [s.strip() for s in match['function_parameters'].split(',')]
            #    print(list(filter(len, [s.strip() for s in re.split(r'[+\-*/=; ]',match['token'])])))
            #else:
            #    print("CHECK", match['identifier_function'], match['function_parameters'])

check_define_usage()
