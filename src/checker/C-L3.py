from typing import List

import vera
from utils import PARENTHESIS_TOKENS, KEYWORDS_TOKENS, BINARY_OPERATORS_TOKENS, IDENTIFIERS_TOKENS, \
    UNARY_OPERATORS_TOKENS, TYPES_TOKENS, SQUARE_BRACKETS_TOKENS
from utils import is_source_file, is_header_file, Token, get_prev_token_index

SEPARATOR_TOKENS = [
    'comma',
    'semicolon'
]

SPACES_TOKENS = [
    'space',
    'newline'
]


def __report(token):
    vera.report(token, "MINOR:C-L3")


def __get_token(tokens: List[Token], index: int):
    return tokens[index] if 0 <= index < len(tokens) else None


def _is_invalid_space(tokens: List[Token], i: int):
    # If there is a new line or a single space the space is always valid
    if tokens[i].name == 'newline' or tokens[i].value == ' ':
        return False
    # If there is multiple spaces but theses spaces was preceded by a new line this is valid
    if i > 0 and tokens[i].name == 'space' and tokens[i - 1].name == 'newline':
        return False
    # Elsewhere the space is invalid
    return True


def check_space_around_operators(file):
    tokens = vera.getTokens(
        file, 1, 0, -1, -1,
        BINARY_OPERATORS_TOKENS +
        UNARY_OPERATORS_TOKENS +
        SPACES_TOKENS +
        IDENTIFIERS_TOKENS +
        TYPES_TOKENS +
        PARENTHESIS_TOKENS +
        SEPARATOR_TOKENS +
        SQUARE_BRACKETS_TOKENS +
        ['case', 'default']
    )
    for i, token in enumerate(tokens):
        if token.name in BINARY_OPERATORS_TOKENS or token.name in UNARY_OPERATORS_TOKENS:
            prev_case_token_index = get_prev_token_index(tokens, i, ['case', 'default'])
            prev_separator_token_index = get_prev_token_index(tokens, i, ['comma', 'semicolon', 'leftbrace'])

            if token.name not in UNARY_OPERATORS_TOKENS:
                if i > 0:
                    if (prev_case_token_index < prev_separator_token_index or prev_case_token_index < 0) and _is_invalid_space(tokens, i - 1):
                        __report(token)
                        continue
                if i + 1 < len(tokens):
                    if (prev_case_token_index < prev_separator_token_index or prev_case_token_index < 0) and _is_invalid_space(tokens, i + 1):
                        __report(token)
                        continue
            elif i > 0 and i + 1 < len(tokens):
                operator_separators_tokens = SPACES_TOKENS + PARENTHESIS_TOKENS + SQUARE_BRACKETS_TOKENS + [token.name]
                allowed_previous_tokens = ['not', 'and']

                if (
                        tokens[i - 1].name not in allowed_previous_tokens and
                        tokens[i - 1].name not in operator_separators_tokens and
                        tokens[i + 1].name not in operator_separators_tokens
                ):
                    __report(token)


def check_space_after_keywords(file):
    keywords_needs_space = ['if', 'switch', 'case', 'for', 'do', 'while', 'return', 'comma', 'struct']
    tokens = vera.getTokens(file, 1, 0, -1, -1, [])

    for i, token in enumerate(tokens):
        if token.name in KEYWORDS_TOKENS and i + 1 < len(tokens):
            # "return" keyword is an exception,
            # where it needs to be immediately followed by either a space and something else than a semicolon,
            # or immediately by a semicolon without a space in between
            if token.name == 'return':
                if tokens[i + 1].name == 'semicolon':
                    continue
                if tokens[i + 1].name in SPACES_TOKENS:
                    if i + 2 >= len(tokens) or tokens[i + 2].name == 'semicolon' or _is_invalid_space(tokens, i + 1):
                        __report(token)
                else:
                    __report(token)
            # If the token needs to have a space, and that there is not space after it, it is an error
            elif token.name in keywords_needs_space and _is_invalid_space(tokens, i + 1):
                __report(token)
            # If the token does not need to have a space, and that there is a space after it, it is an error
            elif token.name not in keywords_needs_space and tokens[i + 1].name in SPACES_TOKENS:
                __report(token)


def check_spaces():
    for file in vera.getSourceFileNames():
        if not is_source_file(file) and not is_header_file(file):
            continue
        check_space_after_keywords(file)
        check_space_around_operators(file)


check_spaces()
