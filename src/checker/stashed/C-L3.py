from typing import List

from utils import PARENTHESIS_TOKENS, KEYWORDS_TOKENS, BINARY_OPERATORS_TOKENS, IDENTIFIERS_TOKENS, \
    UNARY_OPERATORS_TOKENS, TYPES_TOKENS, PREPROCESSOR_TOKENS
from utils import is_source_file, is_header_file, Token, get_next_token_index, get_prev_token_index

import vera

SEPARATOR_TOKENS = [
    'comma',
    'semicolon'
]

SPACES_TOKENS = [
    'space'
]


def __report(token):
    #traceback.print_stack()
    vera.report(token, "MINOR:C-L3")


def __get_token(tokens: List[Token], index: int):
    return tokens[index] if 0 <= index < len(tokens) else None


def is_unary_operator(file, searchedToken):
    separators_tokens = ['semicolon', 'leftbrace', 'rightbrace', 'colon', 'leftparen'] + PREPROCESSOR_TOKENS
    tokens = vera.getTokens(file, 1, 0, -1, -1, IDENTIFIERS_TOKENS + separators_tokens + BINARY_OPERATORS_TOKENS + TYPES_TOKENS + UNARY_OPERATORS_TOKENS + PARENTHESIS_TOKENS)

    if searchedToken.name not in UNARY_OPERATORS_TOKENS:
        return False
    for i, token in enumerate(tokens):
        if token.name != searchedToken.name or token.line != searchedToken.line or token.column != searchedToken.column:
            continue
        if i == 0:
            return True
        if i + 1 < len(tokens) and tokens[i + 1].name in UNARY_OPERATORS_TOKENS + BINARY_OPERATORS_TOKENS:
            return True
        if tokens[i - 1].name in BINARY_OPERATORS_TOKENS + UNARY_OPERATORS_TOKENS + separators_tokens + TYPES_TOKENS:
            return True
        prev_operator_i = get_prev_token_index(tokens, i - 1, BINARY_OPERATORS_TOKENS + UNARY_OPERATORS_TOKENS)
        prev_separator_i = get_prev_token_index(tokens, i - 1, separators_tokens)
        if (
            i > 2 and i + 1 < len(tokens) and
            tokens[i + 1].name in ["identifier"] and
            tokens[i - 1].name in ["identifier"] and
            prev_separator_i > prev_operator_i > -1
        ):
            print(f'VRE {prev_separator_i=}, {prev_operator_i=}, {tokens[i + 1].name=}, {tokens[i - 1].name=}')
            return True
        return False


def check_space_after_function_name(file):
    tokens = vera.getTokens(file, 1, 0, -1, -1, ['identifier'] + PARENTHESIS_TOKENS + SPACES_TOKENS + SEPARATOR_TOKENS + ['comma'] + BINARY_OPERATORS_TOKENS + TYPES_TOKENS)

    for i, token in enumerate(tokens):
        if token.name == 'identifier':
            next_separator_index = get_next_token_index(tokens, i, SEPARATOR_TOKENS)
            next_space_index = get_next_token_index(tokens, i, SPACES_TOKENS)
            next_parenthesis_index = get_next_token_index(tokens, i, PARENTHESIS_TOKENS)
            next_operator_index = get_next_token_index(tokens, i, BINARY_OPERATORS_TOKENS)
            prev_type_index = get_prev_token_index(tokens, i, TYPES_TOKENS)
            prev_separator_index = get_prev_token_index(tokens, i, SEPARATOR_TOKENS + ['comma'])
            prev_identifier_index = get_prev_token_index(tokens, i, IDENTIFIERS_TOKENS)
            prev_operator_index = get_prev_token_index(tokens, i, BINARY_OPERATORS_TOKENS)

            if next_separator_index < next_parenthesis_index:
                continue
            if next_operator_index < next_parenthesis_index:
                continue
            if prev_identifier_index > 0 and (prev_operator_index >= prev_identifier_index or prev_type_index >= prev_identifier_index or prev_separator_index <= prev_identifier_index):
                continue
            if next_parenthesis_index < 0 or next_parenthesis_index > next_separator_index:
                continue
            if next_space_index < next_parenthesis_index:
                __report(token)


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
        ['case']
    )

    for i, token in enumerate(tokens):
        if token.name in BINARY_OPERATORS_TOKENS or token.name in UNARY_OPERATORS_TOKENS:
            is_unary = is_unary_operator(file, token)
            if not is_unary:
                prev_case_token = get_prev_token_index(tokens, i, ['case'])
                prev_separator_token = get_prev_token_index(tokens, i, ['comma', 'semicolon', 'leftbrace'])
                if (i == 0 or tokens[i - 1].name not in SPACES_TOKENS) and (prev_case_token < prev_separator_token or prev_case_token < 0):
                    __report(token)
                if i + 1 >= len(tokens) or tokens[i + 1].name not in SPACES_TOKENS:
                    __report(token)
            else:
                if i + 1 < len(tokens) and tokens[i + 1].name in SPACES_TOKENS:
                    if token.name == 'star':
                        # pylint: disable=W0511
                        vera.report(token, 'MINOR:C-V3')  # FIXME: Separate this part of code in a new rule file
                    else:
                        print(f'{token.name=}, {token.line}:{token.column}')
                        __report(token)


def check_space_after_keywords(file):
    separators_tokens = ['semicolon', 'rightparen', 'leftbrace', 'rightbrace']
    keywords_needs_space = ['if', 'switch', 'case', 'for', 'do', 'while', 'return', 'comma', 'struct']
    tokens = vera.getTokens(file, 1, 0, -1, -1, keywords_needs_space + KEYWORDS_TOKENS + SPACES_TOKENS + UNARY_OPERATORS_TOKENS + separators_tokens + ['colon'])

    for i, token in enumerate(tokens):
        if token.name in KEYWORDS_TOKENS:
            is_unary = is_unary_operator(file, token)
            if is_unary:
                continue
            if i + 1 < len(tokens):
                if token.name in keywords_needs_space and tokens[i + 1].name not in SPACES_TOKENS:
                    __report(token)
                elif token.name not in keywords_needs_space and tokens[i + 1].name in SPACES_TOKENS:
                    __report(token)


def check_spaces():
    for file in vera.getSourceFileNames():
        if not is_source_file(file) and not is_header_file(file):
            continue
        check_space_after_keywords(file)
        check_space_around_operators(file)
        check_space_after_function_name(file)


check_spaces()
