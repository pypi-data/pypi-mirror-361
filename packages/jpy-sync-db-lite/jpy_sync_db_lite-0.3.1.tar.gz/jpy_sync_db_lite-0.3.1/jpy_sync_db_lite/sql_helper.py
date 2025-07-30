"""
SQL Helper utilities for parsing and cleaning SQL statements.

Copyright (c) 2025, Jim Schilling

Please keep this header when you use this code.

This module is licensed under the MIT License.
"""

from pathlib import Path
import sqlparse
from sqlparse.tokens import Comment, DML
from sqlparse.sql import Statement, Token

# Private constants for SQL statement types
_FETCH_STATEMENT_TYPES: tuple[str, ...] = (
    "SELECT",
    "VALUES",
    "SHOW",
    "EXPLAIN",
    "PRAGMA",
    "DESC",
    "DESCRIBE",
)
_DML_STATEMENT_TYPES: tuple[str, ...] = ("SELECT", "INSERT", "UPDATE", "DELETE")
_DESCRIBE_STATEMENT_TYPES: tuple[str, ...] = ("DESC", "DESCRIBE")
_MODIFY_DML_TYPES: tuple[str, ...] = ("INSERT", "UPDATE", "DELETE")

# Private constants for SQL keywords and symbols
_WITH_KEYWORD: str = "WITH"
_AS_KEYWORD: str = "AS"
_SELECT_KEYWORD: str = "SELECT"
_SEMICOLON: str = ";"
_COMMA: str = ","
_PAREN_OPEN: str = "("
_PAREN_CLOSE: str = ")"

# Public constants for statement type return values
EXECUTE_STATEMENT: str = "execute"
FETCH_STATEMENT: str = "fetch"
ERROR_STATEMENT: str = "error"


def remove_sql_comments(sql_text: str) -> str:
    """
    Remove SQL comments from a SQL string using sqlparse.
    Handles:
    - Single-line comments (-- comment)
    - Multi-line comments (/* comment */)
    - Preserves comments within string literals

    Args:
        sql_text: SQL string that may contain comments
    Returns:
        SQL string with comments removed
    """
    if not sql_text:
        return sql_text

    result = sqlparse.format(sql_text, strip_comments=True)
    return str(result) if result is not None else ""


def _is_fetch_statement(statement_type: str) -> bool:
    """
    Determine if a statement type returns rows (fetch) or not (execute).

    Args:
        statement_type: The SQL statement type (e.g., 'SELECT', 'INSERT', 'VALUES')
    Returns:
        True if statement returns rows, False otherwise
    """
    return statement_type in _FETCH_STATEMENT_TYPES


def _is_dml_statement(statement_type: str) -> bool:
    """
    Determine if a statement type is a DML (Data Manipulation Language) statement.

    Args:
        statement_type: The SQL statement type (e.g., 'SELECT', 'CREATE', 'DROP')
    Returns:
        True if statement is DML, False otherwise
    """
    return statement_type in _DML_STATEMENT_TYPES


def _find_first_dml_keyword_top_level(tokens: list[Token]) -> str | None:
    """
    Find first DML/Keyword at the top level after WITH (do not recurse into groups).

    Args:
        tokens: List of sqlparse tokens to analyze
    Returns:
        The first DML/Keyword token value (e.g., 'SELECT', 'INSERT') or None if not found
    """
    for token in tokens:
        if token.is_group:
            continue  # skip CTE definitions
        if not token.is_whitespace and token.ttype not in Comment:
            token_value = str(token.value).strip().upper()
            if token_value == _AS_KEYWORD:
                continue
            if _is_dml_statement(token_value) or _is_fetch_statement(token_value):
                return token_value
    return None


def _find_main_statement_after_ctes(tokens: list[Token]) -> str | None:
    """
    Find the main statement after CTE definitions by looking for the first DML after all CTE groups.

    Args:
        tokens: List of sqlparse tokens to analyze
    Returns:
        The main statement type (e.g., 'SELECT', 'INSERT') or None if not found
    """
    in_cte_definition = False
    paren_level = 0
    i = 0
    n = len(tokens)
    while i < n:
        token = tokens[i]
        token_value = str(token.value).strip().upper()
        if token.is_whitespace or token.ttype in Comment:
            i += 1
            continue
        # Start of a new CTE definition
        if not in_cte_definition and token_value == _AS_KEYWORD:
            in_cte_definition = True
            # Expect next non-whitespace token to be '('
            i += 1
            while i < n and (tokens[i].is_whitespace or tokens[i].ttype in Comment):
                i += 1
            if i < n and tokens[i].ttype == sqlparse.tokens.Punctuation and tokens[i].value == _PAREN_OPEN:
                paren_level = 1
                i += 1
                # Now skip until paren_level returns to 0
                while i < n and paren_level > 0:
                    t = tokens[i]
                    if t.ttype == sqlparse.tokens.Punctuation:
                        if t.value == _PAREN_OPEN:
                            paren_level += 1
                        elif t.value == _PAREN_CLOSE:
                            paren_level -= 1
                    i += 1
                in_cte_definition = False
                # After closing parens, check for comma (another CTE) or main statement
                while i < n and (tokens[i].is_whitespace or tokens[i].ttype in Comment):
                    i += 1
                if i < n and tokens[i].ttype == sqlparse.tokens.Punctuation and tokens[i].value == _COMMA:
                    i += 1
                    continue  # Another CTE definition
                # Otherwise, break to look for main statement
                break
            else:
                # Malformed CTE, just break
                break
        else:
            i += 1
    # Now, i points to the first token after all CTE definitions
    if i >= n:
        return None
    # Skip whitespace and comments to find the main statement
    while i < n and (tokens[i].is_whitespace or tokens[i].ttype in Comment):
        i += 1
    if i >= n:
        return None
    # Check if the next token is a DML/fetch statement
    token = tokens[i]
    token_value = str(token.value).strip().upper()
    if _is_dml_statement(token_value) or _is_fetch_statement(token_value):
        return token_value
    return None


def _next_non_ws_comment_token(
    tokens: list[Token],
    *,
    start: int = 0,
) -> tuple[int | None, Token | None]:
    """
    Find the next non-whitespace, non-comment token.

    Args:
        tokens: List of sqlparse tokens to search through
        start: Starting index to search from (default: 0)
    Returns:
        Tuple of (index, token) or (None, None) if no non-whitespace/non-comment token found
    """
    for i in range(start, len(tokens)):
        token = tokens[i]
        if not token.is_whitespace and token.ttype not in Comment:
            return i, token
    return None, None


def _is_with_keyword(token: Token) -> bool:
    """
    Check if a token represents the 'WITH' keyword.

    Args:
        token: sqlparse token to check
    Returns:
        True if token is the 'WITH' keyword, False otherwise
    """
    try:
        return (
            token.value.strip().upper() == _WITH_KEYWORD
            if hasattr(token, "value") and token.value
            else False
        )
    except (AttributeError, TypeError):
        return False


def _find_with_keyword_index(tokens: list[Token]) -> int | None:
    """
    Find the index of the WITH keyword in a list of tokens.

    Args:
        tokens: List of sqlparse tokens to search
    Returns:
        Index of the WITH keyword or None if not found
    """
    for i, token in enumerate(tokens):
        if _is_with_keyword(token):
            return i
    return None


def _extract_tokens_after_with(stmt: Statement) -> list[Token]:
    """
    Extract all tokens that come after the WITH keyword in a statement.

    Args:
        stmt: sqlparse Statement object
    Returns:
        List of tokens that come after the WITH keyword
    """
    top_tokens: list[Token] = list(stmt.flatten())
    with_index = _find_with_keyword_index(top_tokens)

    if with_index is None:
        return []

    # Return all tokens after the WITH keyword
    return top_tokens[with_index + 1 :]


def detect_statement_type(sql: str) -> str:
    """
    Detect if a SQL statement returns rows using sqlparse.
    Handles:
    - SELECT statements
    - CTEs (WITH ... SELECT)
    - VALUES statements
    - SHOW statements (some databases)
    - DESCRIBE/DESC statements (some databases)
    - EXPLAIN statements (some databases)

    Args:
        sql: SQL statement string
    Returns:
        'fetch' if statement returns rows, 'execute' otherwise
    """
    if not sql or not sql.strip():
        return EXECUTE_STATEMENT

    parsed = sqlparse.parse(sql.strip())
    if not parsed:
        return EXECUTE_STATEMENT

    stmt = parsed[0]
    tokens = list(stmt.flatten())
    if not tokens:
        return EXECUTE_STATEMENT

    _, first_token = _next_non_ws_comment_token(tokens)
    if first_token is None:
        return EXECUTE_STATEMENT

    token_value = first_token.value.strip().upper()

    # DESC/DESCRIBE detection (regardless of token type)
    if token_value in _DESCRIBE_STATEMENT_TYPES:
        return FETCH_STATEMENT

    # CTE detection: WITH ...
    if token_value == _WITH_KEYWORD:
        after_with_tokens = _extract_tokens_after_with(stmt)

        # Try the more sophisticated approach first
        main_stmt = _find_main_statement_after_ctes(after_with_tokens)
        if main_stmt is None:
            # Fallback to the simpler approach
            main_stmt = _find_first_dml_keyword_top_level(after_with_tokens)

        # If no main statement found after CTE, return execute
        if main_stmt is None:
            return EXECUTE_STATEMENT

        if main_stmt == _SELECT_KEYWORD:
            return FETCH_STATEMENT
        if main_stmt in _MODIFY_DML_TYPES:
            return EXECUTE_STATEMENT
        if main_stmt is not None and _is_fetch_statement(main_stmt):
            return FETCH_STATEMENT
        return EXECUTE_STATEMENT

    # SELECT
    if first_token.ttype is DML and token_value == _SELECT_KEYWORD:
        return FETCH_STATEMENT

    # VALUES, SHOW, EXPLAIN, PRAGMA
    if _is_fetch_statement(token_value):
        return FETCH_STATEMENT

    # All other statements (INSERT, UPDATE, DELETE, CREATE, ALTER, DROP, etc.)
    return EXECUTE_STATEMENT


def parse_sql_statements(
    sql_text: str,
    *,
    strip_semicolon: bool = False,
) -> list[str]:
    """
    Parse a SQL string containing multiple statements into a list of individual statements using sqlparse.
    Handles:
    - Statements separated by semicolons
    - Preserves semicolons within string literals
    - Removes comments before parsing
    - Trims whitespace from individual statements
    - Filters out empty statements and statements that are only comments

    Args:
        sql_text: SQL string that may contain multiple statements
        strip_semicolon: If True, strip trailing semicolons in statements (default: False)
    Returns:
        List of individual SQL statements (with or without trailing semicolons based on parameter)
    """
    if not sql_text:
        return []

    # Remove comments first
    clean_sql = remove_sql_comments(sql_text)

    # Use sqlparse to split statements
    parsed_statements = sqlparse.parse(clean_sql)
    filtered_stmts: list[str] = []

    for stmt in parsed_statements:
        stmt_str = str(stmt).strip()
        if not stmt_str:
            continue

        # Tokenize and check if all tokens are comments or whitespace
        tokens = list(stmt.flatten())
        if not tokens:
            continue
        if all(t.is_whitespace or t.ttype in Comment for t in tokens):
            continue

        # Filter out statements that are just semicolons
        if stmt_str == _SEMICOLON:
            continue

        # Apply semicolon stripping based on parameter
        if strip_semicolon:
            stmt_str = stmt_str.rstrip(";").strip()

        filtered_stmts.append(stmt_str)

    return filtered_stmts


def split_sql_file(
    file_path: str | Path,
    *,
    strip_semicolon: bool = False,
) -> list[str]:
    """
    Read a SQL file and split it into individual statements.

    Args:
        file_path: Path to the SQL file
        strip_semicolon: If True, strip trailing semicolons in statements (default: False)
    Returns:
        List of individual SQL statements
    Raises:
        FileNotFoundError: If the file doesn't exist
        OSError: If there's an error reading the file
        ValueError: If file_path is empty or invalid
    """
    if file_path is None:
        raise ValueError("file_path cannot be None")

    if not isinstance(file_path, (str, Path)):
        raise ValueError("file_path must be a string or Path object")

    if not file_path:
        raise ValueError("file_path cannot be empty")

    try:
        with open(file_path, encoding="utf-8") as f:
            sql_content = f.read()
        return parse_sql_statements(sql_content, strip_semicolon=strip_semicolon)
    except FileNotFoundError:
        raise FileNotFoundError(f"SQL file not found: {file_path}") from None
    except OSError as e:
        raise OSError(f"Error reading SQL file {file_path}: {e}") from e
