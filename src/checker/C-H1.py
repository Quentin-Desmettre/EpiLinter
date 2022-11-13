import re

import vera
from utils import is_source_file, is_header_file, get_lines


def check_static_inline_functions():
    for file in vera.getSourceFileNames():
        if not is_source_file(file) and not is_header_file(file):
            continue
        s = ""
        for line in get_lines(file):
            s += line
            s += "\n"
        p = re.compile(r"^[\t ]*(?P<modifiers>(?:(?:inline|static|unsigned|signed|short|long|volatile|struct)[\t ]+)*)"
                       r"(?!else|typedef|return)(?P<type>\w+)\**[\t ]+\**[\t ]*\**[\t ]*(?P<name>\w+)(?P<spaces>[\t ]*)"
                       r"\((?P<parameters>[\t ]*"
                       r"(?:(void|(\w+\**[\t ]+\**[\t ]*\**\w+[\t ]*(,[\t \n]*)?))+|)[\t ]*)\)[\t ]*"
                       r"(?P<endline>;\n|\n?{*\n){1}", re.MULTILINE)
        for search in p.finditer(s):
            line_start = s.count('\n', 0, search.start()) + 1
            if is_source_file(file):
                if search.group('endline') and search.group('modifiers'):
                    is_static_inline = 'static' in search.group('modifiers') and 'inline' in search.group('modifiers')
                    if is_static_inline and is_source_file(file):
                        vera.report(file, line_start, "MAJOR:C-H1")
            elif is_header_file(file) and search.group('endline') and '{' in search.group('endline') \
                    and 'static' not in search.group('modifiers') and 'inline' not in search.group('modifiers'):
                vera.report(file, line_start, "MAJOR:C-H1")


FORBIDDEN_SOURCE_FILE_DIRECTIVES = ['typedef', 'pp_define']


def check_forbidden_directives():
    for file in vera.getSourceFileNames():
        if not is_source_file(file):
            continue
        for token in vera.getTokens(file, 1, 0, -1, -1, FORBIDDEN_SOURCE_FILE_DIRECTIVES):
            vera.report(token, 'MAJOR:C-H1')


check_static_inline_functions()
check_forbidden_directives()
