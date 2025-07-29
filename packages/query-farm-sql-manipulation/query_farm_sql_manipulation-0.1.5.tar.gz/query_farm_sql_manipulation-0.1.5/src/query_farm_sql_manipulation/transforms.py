from collections.abc import Callable

import sqlglot
import sqlglot.expressions
import sqlglot.optimizer.simplify


def remove_expression_part(child: sqlglot.Expression) -> None:
    """
    Remove the specified expression from its parent, respecting the logical structure.
    """
    parent = child.parent
    if parent is None:
        raise ValueError("Cannot remove child from parent because it has no parent")

    if isinstance(parent, sqlglot.expressions.And | sqlglot.expressions.Or):
        # Ands have a .this and .expression
        parent.replace(parent.expression if parent.this == child else parent.this)
    elif isinstance(parent, sqlglot.expressions.Where):
        # If we're in an and, we should just be a tru
        grandparent = parent.parent
        assert grandparent is not None
        grandparent.set("where", None)
    elif isinstance(parent, sqlglot.expressions.Paren):
        remove_expression_part(parent)
    elif isinstance(parent, sqlglot.expressions.Not):
        # This could happen if we're in a statement like
        # x not in (1, 2, 3, 4, 5))
        #
        # Which becomes:
        # not (x in (1, 2, 3, 4, 5))
        #
        # Leaving an empty not isn't valid so just remove it.
        remove_expression_part(parent)
    elif isinstance(parent, sqlglot.expressions.If):
        # If we're in a case statement, we could remove this branch.
        # If the case statement is empty remove everything.

        # The If statement, has the comparision which is stored
        # in this .this

        # Otherwise the child could be in the true
        # or false branches.

        if parent.this == child:
            grandparent = parent.parent
            assert grandparent is not None
            if isinstance(grandparent, sqlglot.expressions.Case):
                ifs = grandparent.args["ifs"]
                assert parent in ifs
                ifs = [x for x in ifs if x != parent]
                if len(ifs) == 0:
                    remove_expression_part(grandparent)
                else:
                    grandparent.set("ifs", ifs)
            else:
                raise ValueError(
                    f"Cannot remove If child from parent of type {type(grandparent)} {grandparent.sql()}"
                )
        else:
            # we are in one of the two value branches.
            raise ValueError(
                f"Cannot remove child because its present in a true or false branch from parent of type {type(parent)} {parent.sql()}"
            )
    else:
        raise ValueError(f"Cannot remove child from parent of type {type(parent)} {parent.sql()}")


def where_clause_contents(
    statement: sqlglot.expressions.Expression,
) -> sqlglot.expressions.Expression | None:
    """
    Extract the contents of the WHERE clause from a SQLGlot expression.
    Args:
        statement: The SQLGlot expression to extract from
    Returns:
        The contents of the WHERE clause, or None if no WHERE clause exists
    """
    where_clause = statement.find(sqlglot.expressions.Where)
    if where_clause is None:
        return None
    return where_clause.this


def filter_predicates_with_right_side_column_references(
    statement: sqlglot.expressions.Expression,
) -> sqlglot.Expression:
    # Need to simplify the statement to move the column references to the
    # left side by default.
    statement = sqlglot.optimizer.simplify.simplify(statement)

    # If there's no WHERE clause, nothing to filter
    where_clause = statement.find(sqlglot.expressions.Where)
    if where_clause is None:
        return statement
    assert where_clause is not None

    for predicate in where_clause.find_all(sqlglot.expressions.Predicate):
        assert predicate is not None
        if predicate.right.find(sqlglot.expressions.Column):
            remove_expression_part(predicate)

    return statement


def filter_column_references(
    *,
    statement: sqlglot.expressions.Expression,
    selector: Callable[[sqlglot.expressions.Column], bool],
) -> sqlglot.Expression:
    """
    Filter SQL statement to remove predicates with columns not in allowed_column_names.

    Args:
        sql: The SQL statement to filter
        selector: A callable that determines if a column should be preserved.
                  It should return True for columns that are allowed, and False for those to be removed.

    Returns:
        Filtered SQLGlot expression with non-allowed columns removed

    Raises:
        ValueError: If a column can't be cleanly removed due to interactions with allowed columns
    """
    # If there's no WHERE clause, nothing to filter
    where_clause = statement.find(sqlglot.expressions.Where)
    if where_clause is None:
        return statement

    # Find all column references not in allowed_column_names
    column_refs_to_remove = [
        col for col in where_clause.find_all(sqlglot.expressions.Column) if not selector(col)
    ]

    # Process each column reference that needs to be removed
    for column_ref in column_refs_to_remove:
        # Find the closest expression containing this column that's a direct child of
        # a logical connector (AND/OR) or the WHERE clause itself
        closest_expression = _find_closest_removable_expression(column_ref)

        # Check if removing this expression would affect allowed columns
        if _can_safely_remove_expression(closest_expression, selector):
            remove_expression_part(closest_expression)
        else:
            raise ValueError(
                f"Column '{column_ref.name}' is involved with allowed columns that cannot be eliminated: "
                f"'{closest_expression.sql()}'"
            )

    return statement


def _find_closest_removable_expression(
    column_ref: sqlglot.expressions.Column,
) -> sqlglot.expressions.Expression:
    """Find the closest parent expression that can be safely removed as a unit."""
    current: sqlglot.expressions.Expression = column_ref
    while current.parent is not None and not isinstance(
        current.parent, sqlglot.expressions.And | sqlglot.expressions.Or | sqlglot.expressions.Where
    ):
        current = current.parent

    if current.parent is None:
        raise ValueError(f"Could not find removable parent for column {column_ref.name}")

    return current


def _can_safely_remove_expression(
    expression: sqlglot.expressions.Expression,
    selector: Callable[[sqlglot.expressions.Column], bool],
) -> bool:
    """
    Check if an expression can be safely removed without affecting allowed columns.

    Args:
        expression: The expression to check
        selector: A callable that determines if a column should be preserved.
                  It should return True for columns that are allowed, and False for those to be removed.

    Returns:
        True if the expression can be safely removed, False otherwise
    """
    # If the parent isn't a supported type, we can't safely remove it
    if not isinstance(
        expression.parent,
        sqlglot.expressions.Predicate
        | sqlglot.expressions.DPipe
        | sqlglot.expressions.Array
        | sqlglot.expressions.PropertyEQ
        | sqlglot.expressions.Binary
        | sqlglot.expressions.Condition
        | sqlglot.expressions.And
        | sqlglot.expressions.Or
        | sqlglot.expressions.Where,
    ):
        return False

    # Check if this expression references any allowed columns
    allowed_columns_referenced = [
        col.name for col in expression.find_all(sqlglot.expressions.Column) if selector(col)
    ]

    # If there are no allowed columns referenced, it's safe to remove
    return len(allowed_columns_referenced) == 0
