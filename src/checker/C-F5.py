import vera
from utils import is_source_file, is_header_file
from utils.functions import get_functions

MAX_ARGS_COUNT = 4

def lineOfArg(raw, arg):
    index_of_arg = raw.index(arg)
    return raw[0:index_of_arg].count('\n')


def check_function_arguments():
    for file in vera.getSourceFileNames():
        if not is_source_file(file) and not is_header_file(file):
            continue

        functions = get_functions(file)
        for function in functions:
            if len(function.arguments) > MAX_ARGS_COUNT:
                for i in range(MAX_ARGS_COUNT, len(function.arguments)):
                    vera.report(vera.Token(function.arguments[i], function.prototype.column_start + function.raw.index(function.arguments[i]), function.prototype.line_start + lineOfArg(function.prototype.raw, function.arguments[i]), "F5", file), "MAJOR:C-F5")


check_function_arguments()
