import atexit
import os
import bisect

all_file_names = []
reports = []
files_lines = {}
tokens_for_file = {}

def setSourceFileNames(names):
    global all_file_names
    all_file_names = names

class Token:
    def __init__(self, value, column, line, name, file):
        self.value = value
        self.column = column
        self.line = line
        self.name = name
        self.file = file
        self.type = name

    def __gt__(self, other):
        return True if self.line > other.line else (False if self.line < other.line else (True if self.column > other.column else False));
        if self.line > other.line:
            return True
        elif self.line <= other.line:
            return False
        if self.column > other.column:
            return True
        return False

    def __le__(self, other):
        if self.line >= other.line:
            return False
        elif self.line < other.line:
            return True
        if self.column >= other.column:
            return False
        return True

    def __eq__(self, other):
        return self.line == other.line and self.column == other.column;

def getSourceFileNames():
    global all_file_names
    return all_file_names

def report(token, err_mess, other_err_mess=""):
    global reports

    if type(token) == type(" "):
        token = Token(" ", 0, err_mess, "", token)
        err_mess = other_err_mess
    # if line_number >= 0:
    # reports.append(file+":"+str(line_number)+": "+message+"\n")
    reports.append("__".join([
        str(token.file),
        str(token.line),
        str(token.column),
        str(err_mess) if len(err_mess) > 0 else "ERROR",
        str(len(token.value)),
    ]) + "\n")

def getAllLines(file_name):
    global files_lines
    if file_name not in files_lines:
        try:
            file = open(file_name)
            lines = file.read().split("\n")
            i = 0
            for line in lines:
                if len(line) > 0 and line[-1] == '\n':
                    line = line[:-1]
                lines[i] = line
                i += 1
            files_lines[file_name] = lines
            if len(files_lines[file_name]) == 0:
                files_lines[file_name] = [""]
            file.close()
        except:
            files_lines[file_name] = []
    return files_lines[file_name]

def getLineCount(file):
    return len(getAllLines(file))

def getEveryTokens(file_name):
    command = "./getTokens " + file_name + " 1 0 " + str(getLineCount(file_name) + 3) + " 0 > output"
    os.system(command)
    f = open("output", "r")
    lines = f.read().split("\2")
    f.close()
    tokens = {}
    for line in lines:
        fields = line.split("\1")
        if len(fields) == 4:
            if fields[3] not in tokens:
                tokens[fields[3]] = []
            new_token = Token(fields[0], int(fields[1]), int(fields[2]), fields[3], file_name)
            tokens[fields[3]].append(new_token)
    return tokens

def  smartGetTokens(file_name: str,
                    fromLine: int,
                    fromColumn: int,
                    toLine: int,
                    toColumn: int,
                    filters):
    line_count = getLineCount(file_name)
    command = "./getTokens " + file_name + " " + str(fromLine) + " " + str(fromColumn) + " " + str(toLine) + " " + str(toColumn) + " " + " ".join(filters) + " > output 2>&1"
    os.system(command)
    f = open("output", "r")
    lines = f.read().split("\2")
    f.close()
    tokens = []
    for line in lines:
        fields = line.split("\1")
        if len(fields) == 4:
            new_token = Token(fields[0], int(fields[1]), int(fields[2]), fields[3], file_name)
            tokens.append(new_token)
    return tokens

def myCount(tok_1, tok_list):
    count = 0
    for tok in tok_list:
        if tok_1.value == tok.value and tok_1.line == tok.line and tok_1.column == tok.column and tok_1.name == tok.name and tok_1.type == tok.type and tok_1.file == tok.file:
            count += 1
    return count

def tokenMatch(tok, fromLine, fromColumn, toLine, toColumn):
    line = tok.line
    column = tok.column

    if ((line > fromLine or (line == fromLine and column >= fromColumn)) and
    (toLine <= 0 or (line < toLine or (line == toLine and column < toColumn)))):
        return True
    return False

def loadTokens(rawTokens, fileName):
    global tokens_for_file
    lines = rawTokens.split("\2")
    tokens = {}
    for line in lines:
        fields = line.split("\1")
        if len(fields) >= 4:
            if fields[3] not in tokens:
                tokens[fields[3]] = []
            new_token = Token(fields[0], int(fields[2]), int(fields[1]), fields[3], fileName)
            tokens[fields[3]].append(new_token)
        # else:
        #     raise BaseException(fields)
    if "eof" not in tokens:
        tokens["eof"] = []
    tokens["eof"].append(Token(None, 0, getLineCount(fileName), "eof", fileName))
    tokens_for_file[fileName] = tokens

def getTokens(file_name: str,
              fromLine: int,
              fromColumn: int,
              toLine: int,
              toColumn: int,
              filters):

    global tokens_for_file
    tokens_to_load = tokens_for_file[file_name]

    tokens = []
    if len(filters) == 0:
        for tok_list in tokens_to_load.values():
            for tok in tok_list:
                line = tok.line
                column = tok.column
                if ((line > fromLine or (line == fromLine and column >= fromColumn)) and
                (toLine <= 0 or (line < toLine or (line == toLine and column < toColumn)))):
                    bisect.insort(tokens, tok)
    else:
        for filter in filters:
            if filter not in tokens_to_load:
                continue
            possible_tokens = tokens_to_load[filter]
            for tok in possible_tokens:
                if tokenMatch(tok, fromLine, fromColumn, toLine, toColumn):
                    bisect.insort(tokens, tok)

    # normal = smartGetTokens(file_name, fromLine, fromColumn, toLine, toColumn, filters)
    # for token in tokens:
    #     if myCount(token, tokens) != myCount(token, normal):
    #         # print("to much elem in my tokens:")
    #         exit(0)
    # for token in normal:
    #     if myCount(token, tokens) != myCount(token, normal):
    #         # print(fromLine, fromColumn, toLine, toColumn)
    #         # print("diff:", token.column, token.line, token.value)
    #         exit(0)
    # if len(tokens) != len(smartGetTokens(file_name, fromLine, fromColumn, toLine, toColumn, filters)):
    #     print("diff!", len(tokens), len(smartGetTokens(file_name, fromLine, fromColumn, toLine, toColumn, filters)))
    #     exit(0)
    return tokens

def getLine(file_name, line_number):
    lines = getAllLines(file_name)
    return lines[line_number - 1] if line_number - 1 < len(lines) else ""

def isBinary(file_name):
    textchars = bytearray({7,8,9,10,12,13,27} | set(range(0x20, 0x100)) - {0x7f})
    is_binary_string = lambda bytes: bool(bytes.translate(None, textchars))
    try:
        file = open(file_name)
        is_binary = is_binary_string(file.read(1024))
        file.close()
        return is_binary
    except:
        return False

def logReports():
    global reports
    f = open('logs.log', 'w+')
    f.writelines(reports)
    f.close()

atexit.register(logReports)
