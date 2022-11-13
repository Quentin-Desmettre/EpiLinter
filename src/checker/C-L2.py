import vera

from utils import is_header_file, is_source_file, is_line_correctly_indented, get_lines

def getSpacesBefore(line):
    spaces = ""
    i = 0
    while line[i] == " ":
        spaces+=" "
        i += 1
    return spaces

def check_line_indentation():
    for file in vera.getSourceFileNames():
        if not is_source_file(file) and not is_header_file(file):
            continue
        for line_number, line in enumerate(get_lines(file, replace_comments=True), start=1):
            if not is_line_correctly_indented(line):
                vera.report(vera.Token(getSpacesBefore(line), 0, line_number, "L2", file), 'MINOR:C-L2')


check_line_indentation()
