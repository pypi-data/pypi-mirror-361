import random
import re
from datetime import datetime, date, timedelta

from pyparsing import (
    Word, alphas, alphanums, quotedString, removeQuotes,
    delimitedList, Literal, CaselessKeyword, Group, ParserElement, oneOf,
    Suppress,    nums, infixNotation, opAssoc,
    Keyword, QuotedString, Forward, Optional, ParseResults, Combine
)
from .helpers import generate_value_matching_regex

# Enable packrat parsing once
ParserElement.enablePackrat()

class CheckConstraintEvaluator:
    """
    SQL CHECK Constraint Evaluator for Data Validation.

    This class parses and evaluates SQL CHECK constraints against row data.
    It supports functions like EXTRACT and DATE, various operators (including BETWEEN),
    and provides helper functions for operand unification.
    """

    def __init__(self, schema_columns=None) -> None:
        """
        Initialize the CheckConstraintEvaluator.

        This constructor sets up the evaluator by creating a pyparsing expression parser for SQL CHECK constraints
        and initializing an optional list of schema column names.

        Parameters
        ----------
        schema_columns : list, optional
            List of column names in the schema.

        Returns
        -------
        None
        """
        self.expression_parser = self._create_expression_parser()
        self.schema_columns = schema_columns or []
        self.parsed_constraint_cache = {}

    def _create_expression_parser(self) -> ParserElement:
        """
        Create and configure the pyparsing parser for SQL CHECK constraints.

        This method enables packrat parsing and defines the grammar for parsing SQL CHECK constraints,
        including basic elements (numbers, strings, identifiers), arithmetic, comparison, and boolean operators,
        as well as support for function calls (EXTRACT, DATE) and parenthesized lists.

        Parameters
        ----------
        None

        Returns
        -------
        ParserElement
            The configured expression parser.
        """
        ParserElement.enablePackrat()

        # Basic elements
        integer = Word(nums)
        real = Combine(Word(nums) + '.' + Word(nums))
        number = real | integer
        string = QuotedString("'", escChar='\\', unquoteResults=False, multiline=True)
        identifier = Word(alphanums, alphanums + "_$").setName("identifier")

        # Define operators
        arith_op = oneOf('+ - * /')
        comp_op = oneOf('= != <> < > <= >= IN NOT IN LIKE NOT LIKE IS IS NOT BETWEEN', caseless=True)
        bool_op = oneOf('AND OR', caseless=True)
        not_op = Keyword('NOT', caseless=True)

        lpar = Suppress('(')
        rpar = Suppress(')')

        expr = Forward()

        # Function call parsing (unchanged)
        func_call = Group(identifier('func_name') + lpar + Optional(delimitedList(expr))('args') + rpar)
        extract_func = Group(
            Keyword('EXTRACT', caseless=True)('func_name') + lpar +
            (identifier | string)('field') +
            Keyword('FROM', caseless=True).suppress() +
            expr('source') + rpar
        )
        date_func = Group(
            Keyword('DATE', caseless=True)('func_name') + lpar + expr('args') + rpar
        )

        # -- NEW: define a parenthesized list of strings/numbers. --
        list_content = delimitedList(string ^ number)  # allows `'M','F'` or numeric
        list_atom = Group(lpar + list_content("list_values") + rpar)("list_atom")

        # Now define the 'atom' so it includes list_atom:
        atom = (
                extract_func
                | func_call
                | date_func
                | list_atom
                | number
                | string
                | identifier
                | Group(lpar + expr + rpar)
        )

        expr <<= infixNotation(
            atom,
            [
                (not_op, 1, opAssoc.RIGHT),
                (arith_op, 2, opAssoc.LEFT),
                (comp_op, 2, opAssoc.LEFT),
                (bool_op, 2, opAssoc.LEFT),
            ]
        )

        return expr

    def _get_parsed_expression(self, check_expression: str) -> ParseResults:
        """
        Parse and cache the SQL CHECK constraint expression.

        If the given check expression is not cached, this method parses it using the expression parser and
        stores the result for future evaluations.

        Parameters
        ----------
        check_expression : str
            The SQL CHECK constraint expression to parse.

        Returns
        -------
        ParseResults
            The parsed expression.
        """
        if check_expression not in self.parsed_constraint_cache:
            parsed_expr = self.expression_parser.parseString(check_expression, parseAll=True)[0]
            self.parsed_constraint_cache[check_expression] = parsed_expr
        return self.parsed_constraint_cache[check_expression]

    def extract_conditions(self, check_expression: str) -> dict:
        """
        Extract conditions from a SQL CHECK constraint.

        Parses the given CHECK constraint expression and returns a dictionary mapping column names
        to lists of condition dictionaries (each containing an operator and a value).

        Parameters
        ----------
        check_expression : str
            The SQL CHECK constraint expression.

        Returns
        -------
        dict
            A dictionary mapping column names to lists of condition dictionaries.
        """

        try:
            parsed_expr = self._get_parsed_expression(check_expression)
            return self._extract_conditions_recursive(parsed_expr)
        except Exception as e:
            print(f"Error parsing check constraint: {e}")
            return {}

    def _extract_conditions_recursive(self, parsed_expr) -> dict:
        """
        Recursively extract conditions from a parsed expression.

        Traverses the parsed expression tree (ParseResults) to collect conditions for each column.
        Each condition is stored as a dictionary with keys 'operator' and 'value'.

        Parameters
        ----------
        parsed_expr : ParseResults
            The parsed expression obtained from the expression parser.

        Returns
        -------
        dict
            A dictionary mapping column names to condition lists.
        """
        conditions = {}
        if isinstance(parsed_expr, ParseResults):
            if len(parsed_expr) == 3:
                left = parsed_expr[0]
                operator = str(parsed_expr[1]).upper()
                right = parsed_expr[2]
                if isinstance(left, str):
                    col_name = left
                    value = self._evaluate_literal(right, treat_as_identifier=True)
                    conditions.setdefault(col_name, []).append({'operator': operator, 'value': value})
                else:
                    left_cond = self._extract_conditions_recursive(left)
                    right_cond = self._extract_conditions_recursive(right)
                    for col, conds in left_cond.items():
                        conditions.setdefault(col, []).extend(conds)
                    for col, conds in right_cond.items():
                        conditions.setdefault(col, []).extend(conds)
            elif len(parsed_expr) == 2:
                operator = str(parsed_expr[0]).upper()
                operand = parsed_expr[1]
                operand_cond = self._extract_conditions_recursive(operand)
                if operator == 'NOT':
                    for col, conds in operand_cond.items():
                        for cond in conds:
                            cond['operator'] = 'NOT ' + cond['operator']
                    conditions.update(operand_cond)
            else:
                for elem in parsed_expr:
                    sub_cond = self._extract_conditions_recursive(elem)
                    for col, conds in sub_cond.items():
                        conditions.setdefault(col, []).extend(conds)
        return conditions

    def _evaluate_literal(self, value, treat_as_identifier: bool = False) -> any:
        """
        Evaluate a literal value from an expression.

        Handles literal values from ParseResults, strings, and numbers. Special tokens such as 'CURRENT_DATE'
        are converted appropriately. If treat_as_identifier is True and the value is among the schema columns,
        it is returned unchanged.

        Parameters
        ----------
        value : any
            The literal value to evaluate.
        treat_as_identifier : bool, optional
            Whether to treat the value as an identifier.

        Returns
        -------
        any
            The evaluated literal value.
        """
        if isinstance(value, (ParseResults, list)):
            return self._evaluate_expression(value, {})
        if isinstance(value, str):
            token = value.upper()
            if treat_as_identifier and (value in self.schema_columns or token in self.schema_columns):
                return value
            if token == 'CURRENT_DATE':
                return date.today()
            if value.startswith("'") and value.endswith("'"):
                return value.strip("'")
            if re.match(r'^\d+(\.\d+)?$', value):
                return float(value) if '.' in value else int(value)
            return value
        return value

    def evaluate(self, check_expression: str, row: dict) -> tuple:
        """
        Evaluate a SQL CHECK constraint against a row of data.

        Parses the given CHECK constraint and evaluates it against the provided row.
        Returns a tuple (result, candidate) where result is a boolean indicating whether the constraint
        is satisfied and candidate is a proposed value if the constraint fails.

        Parameters
        ----------
        check_expression : str
            The SQL CHECK constraint expression.
        row : dict
            A dictionary representing a row of data.

        Returns
        -------
        tuple
            (result, candidate) where result is a boolean and candidate is a proposed adjustment if needed.
        """
        try:
            parsed_expr = self.expression_parser.parseString(check_expression, parseAll=True)[0]
            result, candidate = self._evaluate_expression(parsed_expr, row)
            return bool(result), candidate
        except Exception as e:
            import traceback
            traceback.print_exc()
            print(f"Error evaluating check constraint: {e}")
            print(f"Constraint: {check_expression}")
            return False, None

    def _flatten(self, expr):
        """
        Recursively flatten a nested expression (list or ParseResults) into a flat list of tokens.
        """
        if not isinstance(expr, (list, ParseResults)):
            return [expr]
        flat_list = []
        for item in expr:
            flat_list.extend(self._flatten(item))
        return flat_list

    def _handle_between(self, tokens_str: str, row: dict):
        """
        Look for a BETWEEN clause in the token string and, if found,
        re-parse the value, lower, and upper parts to evaluate them.
        Returns a tuple (result, candidate) where candidate is proposed if the condition fails.
        If no BETWEEN clause is detected, returns (None, None).
        """
        pattern = re.compile(r'(.+?)\s+BETWEEN\s+(.+?)\s+AND\s+(.+)', re.IGNORECASE)
        match = pattern.search(tokens_str)
        if match:
            value_str = match.group(1).strip()
            lower_str = match.group(2).strip()
            upper_str = match.group(3).strip()
            val = self._evaluate_expression(value_str, row)
            low = self._evaluate_expression(lower_str, row)
            high = self._evaluate_expression(upper_str, row)
            if 'date' in tokens_str.lower():
                try:
                    val = self.date_func(val)
                    low = self.date_func(low)
                    high = self.date_func(high)
                except ValueError:
                    pass
            result = low <= val <= high
            if result:
                return True, None
            else:
                candidate = low if val < low else high
                return False, candidate
        return None, None

    def _is_plain_function(self, s: str) -> bool:
        """Return True if the string looks like a plain-text function call (e.g. 'EXTRACT YEAR CURRENT_DATE')."""
        tokens = s.strip().split()
        return bool(tokens) and tokens[0].upper() in ("EXTRACT", "DATE")

    def _evaluate_plain_function(self, s: str, row: dict):
        """
        Evaluate a plain-text function call such as:
          EXTRACT YEAR CURRENT_DATE
          DATE '2020-01-01'
        """
        tokens = s.strip().split()
        func = tokens[0].upper()
        if func == "EXTRACT":
            # Expected syntax: EXTRACT <field> <source>
            if len(tokens) >= 3:
                field = tokens[1]
                source_str = " ".join(tokens[2:])
                return self.extract(field, self._evaluate_expression(source_str, row))
        elif func == "DATE":
            # Expected syntax: DATE <arg>
            if len(tokens) >= 2:
                arg_str = " ".join(tokens[1:])
                return self.date_func(self._evaluate_expression(arg_str, row))
        raise ValueError(f"Unsupported plain function call: {s}")

    def _evaluate_function_call(self, expr, row: dict) -> any:
        """
        Evaluate a structured function call from a parsed expression.

        Supports SQL functions such as EXTRACT, DATE, UPPER, LOWER, LENGTH, SUBSTRING, ROUND, ABS, COALESCE,
        POWER, MOD, TRIM, INITCAP, CONCAT, and REGEXP_LIKE.

        Parameters
        ----------
        expr : ParseResults
            The parsed function call expression, which includes 'func_name' and arguments.
        row : dict
            The row of data used for evaluation.

        Returns
        -------
        any
            The result of the function call.
        """
        func_name = str(expr['func_name']).upper()
        if func_name == 'EXTRACT':
            field = self._evaluate_expression(expr['field'], row)
            source = self._evaluate_expression(expr['source'], row)
            return self.extract(field, source)
        elif func_name == 'DATE':
            arg = self._evaluate_expression(expr['args'], row)
            return self.date_func(arg)
        # For all other functions, fallback to the series of if/elif as before.
        elif func_name == 'UPPER':
            arg = self._evaluate_expression(expr['args'], row)
            return str(arg).upper()
        elif func_name == 'LOWER':
            arg = self._evaluate_expression(expr['args'], row)
            return str(arg).lower()
        elif func_name == 'LENGTH':
            arg = self._evaluate_expression(expr['args'], row)
            return len(arg) if arg is not None else 0
        elif func_name in ('SUBSTRING', 'SUBSTR'):
            args = [self._evaluate_expression(a, row) for a in expr.get('args', [])]
            if len(args) == 2:
                s, start = args
                return s[max(0, start - 1):]
            elif len(args) >= 3:
                s, start, length = args[0], args[1], args[2]
                return s[max(0, start - 1):max(0, start - 1) + length]
            else:
                raise ValueError(f"{func_name} requires at least 2 arguments")
        elif func_name == 'ROUND':
            args = [self._evaluate_expression(a, row) for a in expr.get('args', [])]
            if len(args) == 1:
                return round(args[0])
            elif len(args) >= 2:
                return round(args[0], int(args[1]))
            else:
                raise ValueError("ROUND requires at least one argument")
        elif func_name == 'ABS':
            arg = self._evaluate_expression(expr['args'], row)
            return abs(arg)
        elif func_name == 'COALESCE':
            args = [self._evaluate_expression(a, row) for a in expr.get('args', [])]
            for a in args:
                if a is not None:
                    return a
            return None
        elif func_name == 'POWER':
            args = [self._evaluate_expression(a, row) for a in expr.get('args', [])]
            if len(args) >= 2:
                return args[0] ** args[1]
            else:
                raise ValueError("POWER requires two arguments")
        elif func_name == 'MOD':
            args = [self._evaluate_expression(a, row) for a in expr.get('args', [])]
            if len(args) >= 2:
                return args[0] % args[1]
            else:
                raise ValueError("MOD requires two arguments")
        elif func_name == 'TRIM':
            arg = self._evaluate_expression(expr['args'], row)
            return arg.strip() if isinstance(arg, str) else arg
        elif func_name in ('INITCAP', 'PROPER'):
            arg = self._evaluate_expression(expr['args'], row)
            return arg.title() if isinstance(arg, str) else str(arg).title()
        elif func_name == 'CONCAT':
            args = [self._evaluate_expression(a, row) for a in expr.get('args', [])]
            return "".join(str(a) for a in args)
        elif func_name == 'REGEXP_LIKE':
            args = [self._evaluate_expression(a, row) for a in expr.get('args', [])]
            return self.regexp_like(*args)
        else:
            # Fallback: try to use a method with the lowercase func_name.
            args = [self._evaluate_expression(arg, row) for arg in expr.get('args', [])]
            func = getattr(self, func_name.lower(), None)
            if func:
                return func(*args)
            else:
                raise ValueError(f"Unsupported function '{func_name}' in CHECK constraint")

    def _evaluate_expression(self, expr, row: dict) -> any:
        """
        Recursively evaluate an expression against a row of data.

        Handles expressions provided as strings, lists, or ParseResults. This method processes nested expressions,
        function calls, and operators to compute a final value in the context of the given row.

        Parameters
        ----------
        expr : any
            The expression to evaluate.
        row : dict
            The row of data for evaluation.

        Returns
        -------
        any
            The evaluated result of the expression.
        """
        # If expr is a string, check for plain-text function calls.
        if isinstance(expr, str):
            expr = expr.strip()
            if self._is_plain_function(expr):
                return self._evaluate_plain_function(expr, row)
        # If expr is a list or ParseResults, process its elements.
        if isinstance(expr, (list, ParseResults)):
            if isinstance(expr, ParseResults) and 'func_name' in expr:
                return self._evaluate_function_call(expr, row)
            if len(expr) == 1:
                return self._evaluate_expression(expr[0], row)
            flat = self._flatten(expr)
            tokens_str = " ".join(str(tok) for tok in flat)
            between_result = self._handle_between(tokens_str, row)
            if between_result != (None, None):
                result, candidate = between_result
                return result, candidate
            if len(expr) == 3:
                left_val = self._evaluate_expression(expr[0], row)
                operator = str(expr[1]).upper()
                right_expr = expr[2]

                if operator in ('IN', 'NOT IN') and isinstance(right_expr, (list, ParseResults)):
                    # Each item inside right_expr might be a quoted string or a numeric literal
                    right_val = []
                    for item in right_expr:
                        # Evaluate each item so "'M'" -> "M"
                        val = self._evaluate_expression(item, row)
                        right_val.append(val)
                else:
                    # Otherwise, just do the normal evaluation
                    right_val = self._evaluate_expression(right_expr, row)

                result, candidate = self.apply_operator(left_val, operator, right_val)
                return result, candidate
            if len(expr) == 2:
                operator = str(expr[0]).upper()
                operand = self._evaluate_expression(expr[1], row)
                if operator == 'NOT':
                    return not operand
                else:
                    try:
                        return self._evaluate_literal(operator,treat_as_identifier=True), None
                    except Exception as e:
                        print(f"Error evaluating operator '{operator}': {e}")
                        return False, None
            result = None
            for item in expr:
                result = self._evaluate_expression(item, row)
            return result
        if isinstance(expr, str):
            token = expr.upper()
            if token == 'CURRENT_DATE':
                return date.today()
            if token in ('TRUE', 'FALSE'):
                return token == 'TRUE'
            if expr in row:
                return row[expr]
            if expr.startswith("'") and expr.endswith("'"):
                return expr.strip("'")
            if re.match(r'^\d+(\.\d+)?$', expr):
                return float(expr) if '.' in expr else int(expr)
            return expr
        return expr

    def apply_operator(self, left, operator: str, right) -> tuple:
        """
        Apply a binary operator to left and right operands.

        Supports standard arithmetic, comparison, logical, and SQL-specific operators (LIKE, IN, BETWEEN, etc.).
        If the operator condition is not met, a candidate value is proposed for the left operand.

        Parameters
        ----------
        left : any
            The left operand.
        operator : str
            The operator as a string.
        right : any
            The right operand.

        Returns
        -------
        tuple
            (result, candidate) where result is a boolean indicating whether the condition is satisfied,
            and candidate is a proposed value for the left operand if not.
        """
        op = operator.upper()

        # For comparison operators, unify operands first.
        if op in ('=', '==', '<>', '!=', '>', '<', '>=', '<='):
            left, right = self.unify_operands(left, right)

        # Define mapping for standard binary operators.
        op_map = {
            '=': lambda l, r: l == r,
            '==': lambda l, r: l == r,
            '<>': lambda l, r: l != r,
            '!=': lambda l, r: l != r,
            '>': lambda l, r: l > r,
            '<': lambda l, r: l < r,
            '>=': lambda l, r: l >= r,
            '<=': lambda l, r: l <= r,
            'AND': lambda l, r: bool(l) and bool(r),
            'OR': lambda l, r: bool(l) or bool(r),
            '+': lambda l, r: l + r,
            '-': lambda l, r: l - r,
            '*': lambda l, r: l * r,
            '/': lambda l, r: l / r,
        }
        if op in op_map:

            result = op_map[op](left, right)
            if result:
                return True, None
            else:
                candidate = self._propose_candidate(op, left)
                return False, candidate

        # Operators with custom handling.
        if op == 'LIKE':
            result = self.like(left, right)
            if result:
                return True, None
            else:
                candidate = self._propose_candidate('LIKE', left)
                return False, candidate
        elif op == 'NOT LIKE':
            result = self.not_like(left, right)
            if result:
                return True, None
            else:
                candidate = self._propose_candidate('NOT LIKE', left)
                return False, candidate
        elif op == 'IN':
            result = left in right
            if result:
                return True, None
            else:
                candidate = random.choice(right) if right else None
                return False, candidate
        elif op == 'NOT IN':
            result = left not in right
            if result:
                return True, None
            else:
                candidate = (left + 1 if isinstance(left, (int, float))
                             else left + "X" if isinstance(left, str)
                else None)
                return False, candidate
        elif op == 'IS':
            result = left is right
            return (True, None) if result else (False, right)
        elif op == 'IS NOT':
            result = left is not right
            if result:
                return True, None
            else:
                candidate = (not right if isinstance(right, bool)
                             else right + 1 if isinstance(right, (int, float))
                else right + "_diff" if isinstance(right, str)
                else None)
                return False, candidate
        elif op == 'BETWEEN':
            if not (isinstance(right, list) and len(right) == 2):
                raise ValueError("BETWEEN operator expects right side as [lower, upper]")
            lower, upper = right
            lower, _ = self.unify_operands(lower, lower)
            upper, _ = self.unify_operands(upper, upper)
            left, _ = self.unify_operands(left, left)
            result = lower <= left <= upper
            if result:
                return True, None
            else:
                candidate = lower if left < lower else upper
                return False, candidate

        raise ValueError(f"Unsupported operator '{operator}'")

    def _propose_candidate(self, op, left) -> any:
        """
        Propose a candidate for the left operand to satisfy a binary condition.

        Based solely on the current value of the left operand, this method calculates a candidate value
        by adjusting numeric values, dates, or strings as appropriate.

        Parameters
        ----------
        op : str
            The operator (e.g., '>', '<', 'LIKE').
        left : any
            The current value of the left operand.

        Returns
        -------
        any
            A candidate value intended to satisfy the condition.
        """
        op = op.upper()

        # For equality, we simply return the left value (since we cannot adjust it without external info).
        if op in ('=', '=='):
            return left

        # For greater-than operators, adjust left upward.
        if op in ('>', '>='):
            if isinstance(left, (int, float)):
                return left + 1  # A small fixed increase.
            elif isinstance(left, date):
                return left + timedelta(days=1)
            elif isinstance(left, str):
                return left + "a"  # Append a minimal character.

        # For less-than operators, adjust left downward.
        if op in ('<', '<='):
            if isinstance(left, (int, float)):
                return left - 1  # A small fixed decrease.
            elif isinstance(left, date):
                return left - timedelta(days=1)
            elif isinstance(left, str):
                return "a" + left  # Prepend a minimal character.

        # For LIKE conditions, modify left by appending a fixed suffix.
        if op == 'LIKE':
            if isinstance(left, str):
                return left + "_fix"
            else:
                return left

        # For NOT LIKE, modify left by appending a distinguishing suffix.
        if op == 'NOT LIKE':
            if isinstance(left, str):
                return left + "_diff"
            else:
                return left

        # For operators like IN, NOT IN, IS, IS NOT, or any unsupported operator,
        # simply return left as a fallback.
        return left

    def date_func(self, arg) -> date:
        """
        Simulate the SQL DATE function.

        Converts the input argument to a date object. If the argument is a string, it is parsed using
        the '%Y-%m-%d' format.

        Parameters
        ----------
        arg : any
            The value to convert to a date.

        Returns
        -------
        date
            The resulting date object.
        """
        if isinstance(arg, str):
            return datetime.strptime(arg, '%Y-%m-%d').date()
        elif isinstance(arg, datetime):
            return arg.date()
        elif isinstance(arg, date):
            return arg
        else:
            raise ValueError(f"Unsupported argument for DATE function: {arg}")

    def _as_date(self, val) -> any:
        """
        Convert a value to a date object if possible.

        Attempts to parse the input (if a string) using common date formats; if parsing fails,
        returns the original value.

        Parameters
        ----------
        val : any
            The value to convert.

        Returns
        -------
        any
            A date object if conversion is successful, or the original value otherwise.
        """
        if not isinstance(val, str):
            return val
        lit = val.strip("'")
        for fmt in ("%Y-%m-%d", "%m-%d-%Y", "%d-%m-%Y"):
            try:
                return datetime.strptime(lit, fmt).date()
            except ValueError:
                continue
        return val

    def _as_numeric(self, val) -> any:
        """
        Attempt to convert a value to a numeric type.

        Parses the input value as an integer or float if possible.

        Parameters
        ----------
        val : any
            The value to convert.

        Returns
        -------
        int or float or None
            The numeric value if conversion succeeds; otherwise, None.
        """

        if isinstance(val, (int, float)):
            return val
        if isinstance(val, str) and re.match(r'^\d+(\.\d+)?$', val):
            return float(val) if '.' in val else int(val)
        return None

    def unify_operands(self, left, right) -> tuple:
        """
        Coerce both operands to a common type if possible.

        Attempts to convert both operands to date or numeric types. If both can be converted,
        returns the converted values; otherwise, returns the original operands.

        Parameters
        ----------
        left : any
            The left operand.
        right : any
            The right operand.

        Returns
        -------
        tuple
            A tuple (left, right) with operands coerced to common types if possible.
        """

        left_d = self._as_date(left)
        right_d = self._as_date(right)
        if isinstance(left_d, date) and isinstance(right_d, date):
            return left_d, right_d
        left_n = self._as_numeric(left)
        right_n = self._as_numeric(right)
        if left_n is not None and right_n is not None:
            return left_n, right_n
        return left, right

    def convert_sql_expr_to_python(self, parsed_expr, row: dict) -> str:
        """
        Convert a parsed SQL expression into a Python expression string.

        Recursively converts literals, identifiers, and function calls from the parsed SQL expression
        into a corresponding Python expression string for evaluation.

        Parameters
        ----------
        parsed_expr : any
            The parsed SQL expression.
        row : dict
            The row of data used for context during conversion.

        Returns
        -------
        str
            The resulting Python expression string.
        """
        if isinstance(parsed_expr, str):
            token = parsed_expr.upper()
            if token == 'CURRENT_DATE':
                return "datetime.now().date()"
            elif token in ('TRUE', 'FALSE'):
                return token.capitalize()
            elif parsed_expr in row:
                value = row[parsed_expr]
                if isinstance(value, datetime):
                    return f"datetime.strptime('{value.strftime('%Y-%m-%d %H:%M:%S')}', '%Y-%m-%d %H:%M:%S')"
                elif isinstance(value, date):
                    return f"datetime.strptime('{value.strftime('%Y-%m-%d')}', '%Y-%m-%d').date()"
                elif isinstance(value, str):
                    escaped_value = value.replace("'", "\\'")
                    return f"'{escaped_value}'"
                else:
                    return str(value)
            elif re.match(r'^\d+(\.\d+)?$', parsed_expr):
                return parsed_expr
            elif parsed_expr.startswith("'") and parsed_expr.endswith("'"):
                return parsed_expr
            else:
                return f"'{parsed_expr}'"
        elif isinstance(parsed_expr, ParseResults):
            if 'func_name' in parsed_expr:
                func_name = str(parsed_expr['func_name']).upper()
                if func_name == 'EXTRACT':
                    field = self.convert_sql_expr_to_python(parsed_expr['field'], row)
                    source = self.convert_sql_expr_to_python(parsed_expr['source'], row)
                    return f"self.extract({field}, {source})"
                else:
                    args = parsed_expr.get('args', [])
                    args_expr = [self.convert_sql_expr_to_python(arg, row) for arg in args]
                    func_map = {'REGEXP_LIKE': 'self.regexp_like'}
                    if func_name in func_map:
                        return f"{func_map[func_name]}({', '.join(args_expr)})"
                    else:
                        raise ValueError(f"Unsupported function '{func_name}' in CHECK constraint")
            elif len(parsed_expr) == 1:
                return self.convert_sql_expr_to_python(parsed_expr[0], row)
            else:
                return self.handle_operator(parsed_expr, row)
        elif len(parsed_expr) == 1:
            return self.convert_sql_expr_to_python(parsed_expr[0], row)
        else:
            return self.handle_operator(parsed_expr, row)

    def handle_operator(self, parsed_expr, row: dict) -> str:
        """
        Convert an operator expression into a Python expression string.

        Maps SQL operators (e.g., '=', '<>', 'LIKE', 'IN') to their Python equivalents and constructs
        a corresponding expression string.

        Parameters
        ----------
        parsed_expr : ParseResults
            The parsed operator expression.
        row : dict
            The row of data used for context.

        Returns
        -------
        str
            A Python expression string representing the operator expression.
        """
        if len(parsed_expr) == 2:
            operator = parsed_expr[0]
            operand = self.convert_sql_expr_to_python(parsed_expr[1], row)
            if str(operator).upper() == 'NOT':
                return f"not ({operand})"
            else:
                raise ValueError(f"Unsupported unary operator '{operator}'")
        elif len(parsed_expr) == 3:
            left = self.convert_sql_expr_to_python(parsed_expr[0], row)
            operator = str(parsed_expr[1]).upper()
            right = self.convert_sql_expr_to_python(parsed_expr[2], row)
            if operator in ('IS', 'IS NOT'):
                if right.strip() == 'None':
                    python_operator = 'is' if operator == 'IS' else 'is not'
                    return f"({left} {python_operator} {right})"
                else:
                    python_operator = '==' if operator == 'IS' else '!='
                    return f"({left} {python_operator} {right})"
            else:
                operator_map = {
                    '=': '==', '<>': '!=', '!=': '!=', '>=': '>=',
                    '<=': '<=', '>': '>', '<': '<', 'AND': 'and', 'OR': 'or',
                    'LIKE': 'self.like', 'NOT LIKE': 'self.not_like',
                    'IN': 'in', 'NOT IN': 'not in'
                }
                python_operator = operator_map.get(operator)
                if python_operator is None:
                    raise ValueError(f"Unsupported operator '{operator}'")
                if 'LIKE' in operator:
                    return f"{python_operator}({left}, {right})"
                else:
                    return f"({left} {python_operator} {right})"
        else:
            raise ValueError(f"Unsupported expression structure: {parsed_expr}")

    def extract(self, field: str, source) -> int:
        """
        Simulate the SQL EXTRACT function.

        Extracts a specific component (year, month, or day) from a given date or datetime source.

        Parameters
        ----------
        field : str
            The field to extract (e.g., 'year', 'month', 'day').
        source : any
            The source date or datetime (or string representing a date).

        Returns
        -------
        int
            The extracted numeric value.
        """
        field = field.strip("'").lower()
        if isinstance(source, str):
            if source.upper() == 'CURRENT_DATE':
                source = date.today()
            else:
                try:
                    source = datetime.strptime(source, '%Y-%m-%d')
                except ValueError:
                    source = datetime.now()
        if isinstance(source, datetime):
            source = source.date()
        if field == 'year':
            return source.year
        elif field == 'month':
            return source.month
        elif field == 'day':
            return source.day
        else:
            raise ValueError(f"Unsupported field '{field}' for EXTRACT function")

    def regexp_like(self, value: str, pattern: str) -> tuple:
        """
        Simulate the SQL REGEXP_LIKE function.

        Checks whether the given value matches the specified regular expression pattern.
        If the value does not match, returns a candidate value that may satisfy the pattern.

        Parameters
        ----------
        value : str
            The value to test.
        pattern : str
            The regular expression pattern (optionally quoted).

        Returns
        -------
        tuple
            (result, candidate) where result is a boolean indicating a match and candidate is a proposed value if no match is found.
        """

        if pattern.startswith("'") and pattern.endswith("'"):
            pattern = pattern[1:-1]
        if not isinstance(value, str):
            value = str(value)
        try:
            result = re.match(pattern, value) is not None
        except re.error as e:
            print(f"Regex error: {e}")
            return False, ""
        if result:
            return True, None
        else:
            candidate = generate_value_matching_regex(pattern)
            return False, candidate

    def like(self, value: str, pattern: str) -> bool:
        """
        Simulate the SQL LIKE operator.

        Converts the SQL LIKE pattern (using '%' and '_') into a regular expression and checks whether
        the given value matches the pattern.

        Parameters
        ----------
        value : str
            The value to test.
        pattern : str
            The SQL LIKE pattern.

        Returns
        -------
        bool
            True if the value matches the pattern, otherwise False.
        """
        pattern = pattern.strip("'").replace('%', '.*').replace('_', '.')
        if not isinstance(value, str):
            value = str(value)
        return re.match(f'^{pattern}$', value) is not None

    def not_like(self, value: str, pattern: str) -> bool:
        """
        Simulate the SQL NOT LIKE operator.

        Returns the negation of the LIKE operator evaluation for the given value and pattern.

        Parameters
        ----------
        value : str
            The value to test.
        pattern : str
            The SQL LIKE pattern.

        Returns
        -------
        bool
            True if the value does not match the pattern, otherwise False.
        """
        return not self.like(value, pattern)
