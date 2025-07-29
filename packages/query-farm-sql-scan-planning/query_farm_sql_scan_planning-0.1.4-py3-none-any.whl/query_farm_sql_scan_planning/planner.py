from collections.abc import Callable
from dataclasses import dataclass
from typing import Any, Generator
import duckdb
import pyarrow as pa
import sqlglot
import sqlglot.expressions
import sqlglot.optimizer.simplify


@dataclass
class BaseFieldInfo:
    """
    The base class for information about a field known for scan planning.
    """

    has_nulls: bool
    has_non_nulls: bool


@dataclass
class RangeFieldInfo(BaseFieldInfo):
    """
    Information about a field that has a min and max value.
    """

    min_value: pa.Scalar
    max_value: pa.Scalar


@dataclass
class SetFieldInfo(BaseFieldInfo):
    """
    Information about a field where the set of values are known.
    The information about what values that are contained can produce
    false positives.
    """

    values: set[
        pa.Scalar
    ]  # Set of values that are known to be present in the field, false positives are okay.


AnyFieldInfo = SetFieldInfo | RangeFieldInfo


def _scalar_value_op(
    a: pa.Scalar, b: pa.Scalar, op: Callable[[Any, Any], bool]
) -> bool:
    """
    Perform a scalar value operation on two scalars.
    """
    assert not pa.types.is_null(a.type), (
        f"Expected a non-null scalar value, got {a} of type {a.type}"
    )
    assert not pa.types.is_null(b.type), (
        f"Expected a non-null scalar value, got {b} of type {b.type}"
    )

    # If we have integers or floats we can do that comparision regardless of their types.
    if pa.types.is_integer(a.type) and pa.types.is_integer(b.type):
        return op(a.as_py(), b.as_py())

    if pa.types.is_floating(a.type) and pa.types.is_floating(b.type):
        return op(a.as_py(), b.as_py())

    if pa.types.is_string(a.type) and pa.types.is_string(b.type):
        return op(a.as_py(), b.as_py())

    if pa.types.is_boolean(a.type) and pa.types.is_boolean(b.type):
        return op(a.as_py(), b.as_py())

    if pa.types.is_decimal(a.type) and pa.types.is_decimal(b.type):
        return op(a.as_py(), b.as_py())

    assert type(a) is type(b), (
        f"Expected same type for comparison, got {type(a)} and {type(b)}"
    )

    return op(a.as_py(), b.as_py())


def _sv_lte(a: pa.Scalar, b: pa.Scalar) -> bool:
    return _scalar_value_op(a, b, lambda x, y: x <= y)


def _sv_lt(a: pa.Scalar, b: pa.Scalar) -> bool:
    return _scalar_value_op(a, b, lambda x, y: x < y)


def _sv_gt(a: pa.Scalar, b: pa.Scalar) -> bool:
    return _scalar_value_op(a, b, lambda x, y: x > y)


def _sv_gte(a: pa.Scalar, b: pa.Scalar) -> bool:
    return _scalar_value_op(a, b, lambda x, y: x >= y)


def _sv_eq(a: pa.Scalar, b: pa.Scalar) -> bool:
    return _scalar_value_op(a, b, lambda x, y: x == y)


FileFieldInfo = dict[str, AnyFieldInfo]

# When bailing out we should know why we bailed out if we couldn't evaluate the expression.


class Planner:
    """
    Filter files based on their min/max ranges using AST-parsed expressions.
    """

    def __init__(self, files: list[tuple[str, FileFieldInfo]]):
        """
        Initialize with list of (filename, min_value, max_value) tuples.

        Args:
            file_ranges: List of tuples containing (filename, min_val, max_val)
        """
        self.files = files
        self.connection = duckdb.connect(":memory:")

    def _eval_predicate(
        self,
        file_info: FileFieldInfo,
        node: sqlglot.expressions.Predicate,
    ) -> bool | None:
        """
        Check if a file's range could satisfy a single condition.

        For a file to potentially contain data satisfying the condition,
        there must be some overlap between the file's range and the condition's range.
        """
        assert isinstance(node, sqlglot.expressions.Predicate)
        assert isinstance(node, sqlglot.expressions.Binary), (
            f"Expected a binary predicate but got {node} {type(node)}"
        )

        if isinstance(node, sqlglot.expressions.Is):
            return self._evaluate_node_is(node, file_info)

        # Handle comparison operations
        if not isinstance(node.left, sqlglot.expressions.Column):
            return None

        if node.right.find(sqlglot.expressions.Column) is not None:
            # Can't evaluate this since it has a right hand column ref, ideally
            # this should be removed further up.
            return None

        # The thing on the right side should be something that can be evaluated against a range.
        # ideally, its going to be a
        value_result = self.connection.execute(
            f"select {node.right.sql('duckdb')}"
        ).arrow()
        assert value_result.num_rows == 1, (
            f"Expected a single row result from cast, got {value_result.num_rows} rows"
        )
        assert value_result.num_columns == 1, (
            f"Expected a single column result from cast, got {value_result.num_columns} columns"
        )

        right_val = value_result.column(0)[0]
        # This is an interesting behavior, null is returned with an int32 type.
        if type(right_val) is pa.Int32Scalar and right_val.as_py() is None:
            right_val = pa.scalar(None, type=pa.null())

        left_val = node.left
        assert isinstance(left_val, sqlglot.expressions.Column), (
            f"Expected a column on left side of {node}, got {left_val}"
        )
        assert isinstance(left_val.this, sqlglot.expressions.Identifier), (
            f"Expected an identifier on left side of {node}, got {left_val.this}"
        )
        referenced_field_name = left_val.this.this

        field_info = file_info.get(referenced_field_name)

        # Right now if the field is not present in the file,
        # just note that we couldn't evaluate the expression.
        if field_info is None:
            return None

        if isinstance(field_info, SetFieldInfo):
            match type(node):
                case sqlglot.expressions.EQ:
                    if pa.types.is_null(right_val.type):
                        return False
                    return right_val in field_info.values
                case sqlglot.expressions.NEQ:
                    if pa.types.is_null(right_val.type):
                        return False
                    return right_val not in field_info.values
                case _:
                    raise ValueError(
                        f"Unsupported operator type for SetFieldInfo: {type(node)}"
                    )

        if type(node) is sqlglot.expressions.NullSafeNEQ:
            if (
                not pa.types.is_null(right_val.type)
                and field_info.has_non_nulls is False
            ):
                return True

            if pa.types.is_null(right_val.type):
                return field_info.has_non_nulls

            return not (
                _sv_eq(field_info.min_value, field_info.max_value)
                and _sv_eq(field_info.min_value, right_val)
            )

        elif type(node) is sqlglot.expressions.NullSafeEQ:
            if pa.types.is_null(right_val.type) and field_info.has_non_nulls:
                return True
            if field_info.min_value is None or field_info.max_value is None:
                return False
            assert not pa.types.is_null(right_val.type)
            return _sv_lte(field_info.min_value, right_val) and _sv_lte(
                right_val, field_info.max_value
            )

        if field_info.min_value is None or field_info.max_value is None:
            return False

        if pa.types.is_null(right_val.type):
            return False

        match type(node):
            case sqlglot.expressions.EQ:
                return _sv_lte(field_info.min_value, right_val) and _sv_lte(
                    right_val, field_info.max_value
                )
            case sqlglot.expressions.NEQ:
                return not (
                    _sv_eq(field_info.min_value, field_info.max_value)
                    and _sv_eq(field_info.min_value, right_val)
                )
            case sqlglot.expressions.LT:
                return _sv_lt(field_info.min_value, right_val)
            case sqlglot.expressions.LTE:
                return _sv_lte(field_info.min_value, right_val)
            case sqlglot.expressions.GT:
                return _sv_gt(field_info.max_value, right_val)
            case sqlglot.expressions.GTE:
                return _sv_gte(field_info.max_value, right_val)
            case sqlglot.expressions.NullSafeEQ:
                if pa.types.is_null(right_val.type) and field_info.has_non_nulls:
                    return True
                return _sv_lte(field_info.min_value, right_val) and _sv_lte(
                    right_val, field_info.max_value
                )
            case sqlglot.expressions.NullSafeNEQ:
                if (
                    not pa.types.is_null(right_val.type)
                    and field_info.has_non_nulls is False
                ):
                    return True
                return not (
                    _sv_eq(field_info.min_value, field_info.max_value)
                    and _sv_eq(field_info.min_value, right_val)
                )
            case _:
                raise ValueError(f"Unsupported operator type: {type(node)}")

    def _evaluate_node_connector(
        self, node: sqlglot.Expression, file_info: FileFieldInfo
    ) -> bool | None:
        """
        Evaluate a connector node (AND, OR, XOR) against a file's field info.

        Returns True, False, or None if the expression cannot be evaluated.
        """
        assert isinstance(node, sqlglot.expressions.Connector), (
            f"Expected a connector node, got {node} of type {type(node)}"
        )
        match type(node):
            case sqlglot.expressions.And:
                return self._evaluate_sql_node(
                    node.left, file_info
                ) and self._evaluate_sql_node(node.right, file_info)
            case sqlglot.expressions.Or:
                return self._evaluate_sql_node(
                    node.left, file_info
                ) or self._evaluate_sql_node(node.right, file_info)
            case sqlglot.expressions.Xor:
                raise ValueError("Unsupported XOR operation in SQL expression.")
                # return self._evaluate_sql_node(
                #     node.left, file_info
                # ) ^ self._evaluate_sql_node(node.right, file_info)
            case _:
                # If we reach here, it means the node is not a recognized connector type.
                assert False, f"Unexpected connector type: {type(node)}"

        raise ValueError(f"Unsupported connector type: {type(node)}")

    def _evaluate_node_in(
        self, node: sqlglot.expressions.In, file_info: FileFieldInfo
    ) -> bool | None:
        """
        Evaluate an IN predicate against a file's field info.
        Returns True if the left side is in the set of values on the right side,
        False if it is not, and None if the left side cannot be evaluated.
        """
        in_val = node.this

        # If the left side is a NULL, then it can't be in anything.
        if isinstance(in_val, sqlglot.expressions.Null):
            return False

        # So the left side should be a column, but if its not just kind of give up.
        if not isinstance(in_val, sqlglot.expressions.Column):
            # FIXME: this could be improved because if the left side is a literal, we could
            # do a little better job of checking if we have set presence for that literal.
            return None

        assert isinstance(in_val, sqlglot.expressions.Column), (
            f"Expected a column on left side of {node}, got {in_val}"
        )
        assert isinstance(in_val.this, sqlglot.expressions.Identifier), (
            f"Expected an identifier on left side of {node}, got {in_val.this}"
        )

        if len(node.expressions) == 0:
            return False

        for in_exp in node.expressions:
            if self._eval_predicate(
                file_info,
                sqlglot.expressions.EQ(this=in_val, expression=in_exp),
            ):
                return True
        return False

    def _evaluate_node_not_in(
        self, node: sqlglot.expressions.In, file_info: FileFieldInfo
    ) -> bool | None:
        """
        Evaluate a NOT IN predicate against a file's field info.
        Returns True if the left side is not in the set of values on the right side,
        False if it is, and None if the left side cannot be evaluated.
        """
        in_val = node.this

        if isinstance(in_val, sqlglot.expressions.Null):
            return False

        if not isinstance(in_val, sqlglot.expressions.Column):
            return None
        assert isinstance(in_val, sqlglot.expressions.Column), (
            f"Expected a column on left side of {node}, got {in_val}"
        )
        assert isinstance(in_val.this, sqlglot.expressions.Identifier), (
            f"Expected an identifier on left side of {node}, got {in_val.this}"
        )

        if len(node.expressions) == 0:
            return True

        for in_exp in node.expressions:
            assert isinstance(
                in_exp, sqlglot.expressions.Literal | sqlglot.expressions.Neg
            ), (
                f"Expected a literal in in side of {node}, got {in_exp} type {type(in_exp)}"
            )
            if self._eval_predicate(
                file_info,
                sqlglot.expressions.NEQ(this=in_val, expression=in_exp),
            ):
                return True
        return False

    def _evaluate_node_is(
        self, node: sqlglot.expressions.Is, file_info: FileFieldInfo
    ) -> bool:
        """
        Evaluate an IS NULL or IS NOT NULL predicate against a file's field info.
        Returns True if the left side is NULL or NOT NULL, False otherwise.
        """
        in_val = node.left
        assert isinstance(in_val, sqlglot.expressions.Column), (
            f"Expected a column on left side of {node}, got {in_val}"
        )
        assert isinstance(in_val.this, sqlglot.expressions.Identifier), (
            f"Expected an identifier on left side of {node}, got {in_val.this}"
        )
        assert isinstance(node.right, sqlglot.expressions.Null), (
            f"Expected a NULL literal on right side of {node}, got {node.right}"
        )
        target_field_name = in_val.this.this
        target_field_info = file_info.get(target_field_name)
        if target_field_info is None:
            raise ValueError(f"Unsupported variable name: {target_field_name}.")
        return target_field_info.has_nulls

    def _evaluate_node_predicate(
        self, node: sqlglot.Expression, file_info: FileFieldInfo
    ) -> bool | None:
        """
        Evaluate a predicate node against a file's field info.
        Returns True, False, or None if the expression cannot be evaluated.
        """
        if isinstance(node, sqlglot.expressions.In):
            return self._evaluate_node_in(node, file_info)

        assert isinstance(node, sqlglot.expressions.Predicate)
        assert isinstance(node, sqlglot.expressions.Binary), (
            f"Expected a binary predicate but got {node} {type(node)}"
        )

        if isinstance(node, sqlglot.expressions.Is):
            return self._evaluate_node_is(node, file_info)

        return self._eval_predicate(file_info, node)

    def _evaluate_node_case(
        self, node: sqlglot.expressions.Case, file_info: FileFieldInfo
    ) -> bool | None:
        """
        Evaluate a CASE statement against a file's field info.
        """
        for if_statement in node.args["ifs"]:
            assert isinstance(if_statement, sqlglot.expressions.If), (
                f"Expected an If statement in Case but got {if_statement}"
            )
            assert isinstance(if_statement.this, sqlglot.expressions.Predicate), (
                f"Expected a Predicate in If statement but got {if_statement.this}"
            )
            clause_result = self._evaluate_sql_node(if_statement.this, file_info)
            if clause_result is None:
                return None
            if clause_result:
                return self._evaluate_sql_node(if_statement.args["true"], file_info)
        if "default" in node.args:
            return self._evaluate_sql_node(node.args["default"], file_info)
        # the default is null, so don't return the file.
        return False

    def _evaluate_sql_node(
        self, node: sqlglot.Expression, file_info: FileFieldInfo
    ) -> bool | None:
        """
        Evaluate a SQL node against a file's field info.
        Returns True, False, or None if the expression cannot be evaluated.
        """
        match node:
            case sqlglot.expressions.Connector():
                return self._evaluate_node_connector(node, file_info)

            case sqlglot.expressions.Predicate():
                return self._evaluate_node_predicate(node, file_info)

            case sqlglot.expressions.Not():
                match node.this:
                    case sqlglot.expressions.In():
                        # Handle 'not in' operations
                        return self._evaluate_node_not_in(node.this, file_info)
                    case _:
                        # Handle general 'not' operations
                        inner_result = self._evaluate_sql_node(node.this, file_info)
                        return None if inner_result is None else not inner_result

            case sqlglot.expressions.Boolean():
                return node.to_py()

            case sqlglot.expressions.Case():
                return self._evaluate_node_case(node, file_info)

            case sqlglot.expressions.Null():
                return False

            case _:
                raise ValueError(
                    f"Unsupported node type: {type(node).__name__}. "
                    f"Supported types: Connector, Predicate, Not, Boolean, Case, Null"
                )

    def get_matching_files(
        self, exp: sqlglot.expressions.Expression | str, *, dialect: str = "duckdb"
    ) -> Generator[str, None, None]:
        """
        Get a set of files that match the given SQL expression.
        Args:
            expression: The SQL expression to evaluate.
            dialect: The SQL dialect to use for parsing the expression.
            Returns:
                A set of filenames that match the expression.
        """
        if isinstance(exp, str):
            # Parse the expression if it is a string.
            expression = sqlglot.parse_one(exp, dialect=dialect)
        else:
            expression = exp

        if not isinstance(expression, sqlglot.expressions.Expression):
            raise ValueError(f"Expected a sqlglot expression, got {type(expression)}")

        # Simplify the parsed expression, move all of the literals to the right side
        expression = sqlglot.optimizer.simplify.simplify(expression)

        for filename, file_info in self.files:
            eval_result = self._evaluate_sql_node(expression, file_info)
            if eval_result is None or eval_result is True:
                # If the expression evaluates to True or cannot be evaluated, add the file
                # to the result set since the caller will be able to filter the rows further.
                yield filename
