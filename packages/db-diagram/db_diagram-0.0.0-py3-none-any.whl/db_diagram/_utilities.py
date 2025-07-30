from __future__ import annotations

import functools
import os
from itertools import chain
from typing import TYPE_CHECKING, Any

from sqlalchemy import URL, Column, Connection, Engine, MetaData, create_engine
from sqlalchemy.sql.schema import Constraint, ForeignKeyConstraint, Table
from sqlalchemy.types import TypeDecorator, TypeEngine

if TYPE_CHECKING:
    from collections.abc import (
        Callable,
        Iterable,
    )

any_lru_cache: Callable[..., Callable[..., Callable[..., Any]]] = (
    functools.lru_cache
)  # type: ignore
str_lru_cache: Callable[..., Callable[..., Callable[..., str]]] = (
    functools.lru_cache
)  # type: ignore

cache: Callable[[Callable], Callable]
try:
    from functools import cache  # type: ignore
except ImportError:
    from functools import lru_cache

    cache = lru_cache(maxsize=None)


def as_tuple(
    user_function: Callable[..., Iterable[Any]],
) -> Callable[..., tuple[Any, ...]]:
    """
    This is a decorator which will return an iterable as a tuple.
    """

    def wrapper(*args: Any, **kwargs: Any) -> tuple[Any, ...]:
        return tuple(user_function(*args, **kwargs) or ())

    return functools.update_wrapper(wrapper, user_function)


def as_cached_tuple(
    maxsize: int | None = None, *, typed: bool = False
) -> Callable[[Callable[..., Iterable[Any]]], Callable[..., tuple[Any, ...]]]:
    """
    This is a decorator which will return an iterable as a tuple,
    and cache that tuple.

    Parameters:

    - maxsize (int|None) = None: The maximum number of items to cache.
    - typed (bool) = False: For class methods, should the cache be distinct for
      sub-classes?
    """
    return functools.lru_cache(maxsize=maxsize, typed=typed)(as_tuple)


def iter_referenced_tables(
    table: Table,
    exclude: Iterable[str] = (),
    depth: int | None = None,
) -> Iterable[Table]:
    """
    Yield all tables referenced by the given table, to a specified depth.

    Parameters:
        table:
        exclude: One or more table names to exclude
        depth: If provided, and greater than 1, recursive references
            will be included
    """
    if not isinstance(exclude, set):
        exclude = set(exclude)
    constraint: Constraint
    foreign_key_constraint: ForeignKeyConstraint
    for foreign_key_constraint in filter(  # type: ignore
        lambda constraint: isinstance(constraint, ForeignKeyConstraint),
        table.constraints or (),
    ):
        if TYPE_CHECKING:
            assert isinstance(foreign_key_constraint.referred_table, Table)
        key: str = str(foreign_key_constraint.referred_table.key)
        if (not exclude) or (key not in exclude):
            exclude.add(key)
            yield foreign_key_constraint.referred_table
            if (depth is None) or (depth > 1):
                yield from iter_referenced_tables(
                    foreign_key_constraint.referred_table,
                    exclude,
                    (None if depth is None else depth - 1),
                )


def get_column_type_name(column: Column) -> str:
    column_type: (
        type[TypeEngine | TypeDecorator] | TypeEngine | TypeDecorator
    ) = column.type
    if not isinstance(column_type, type):
        column_type = type(column_type)
    if issubclass(column_type, TypeDecorator):
        column_type = column_type.impl
        if not isinstance(column_type, type):
            column_type = type(column_type)
    visit_name: str = getattr(column_type, "__visit_name__", "") or ""
    return visit_name


@cache
def get_metadata_tables_referenced(
    metadata: MetaData,
) -> dict[Table, set[Table]]:
    """
    Obtain and cache a mapping of tables to the tables which they directly
    reference
    """
    tables_references: dict[Table, set[Table]] = {}
    table: Table
    for table in metadata.sorted_tables:
        if table not in tables_references:
            tables_references[table] = set()
        reference: Table
        for reference in iter_referenced_tables(table, depth=1):
            tables_references[table].add(reference)
    return tables_references


@cache
def get_metadata_tables_references(
    metadata: MetaData,
) -> dict[Table, set[Table]]:
    """
    Obtain and cache a mapping of tables to the other tables which directly
    referenced the table
    """
    references_tables: dict[Table, set[Table]] = {}
    table: Table
    references: set[Table]
    for table, references in get_metadata_tables_referenced(metadata).items():
        for reference in references:
            if reference not in references_tables:
                references_tables[reference] = set()
            references_tables[reference].add(table)
    return references_tables


def iter_related_tables(
    table: Table,
    depth: int | None = None,
    _used: Iterable[Table] = (),
) -> Iterable[Table]:
    """
    Yield all related tables up to the specified depth.
    """
    if not isinstance(_used, set):
        _used = set(_used)
    _used.add(table)
    related_table: Table
    for related_table in sorted(
        chain(
            get_metadata_tables_referenced(table.metadata).get(table, ()),
            get_metadata_tables_references(table.metadata).get(table, ()),
        ),
        key=lambda related_table: related_table.key,
    ):
        if related_table not in _used:
            yield related_table
            _used.add(related_table)
            if (depth is None) or (depth > 1):
                yield from iter_related_tables(
                    related_table,
                    depth=None if depth is None else depth - 1,
                    _used=_used,
                )


@cache
def is_ci() -> bool:
    return bool(
        # Github Actions
        ("CI" in os.environ and (os.environ["CI"].lower() == "true"))
        # Jenkins
        or ("HUDSON_URL" in os.environ)
    )


def get_table_primary_key_and_column_names(
    table: Table,
) -> tuple[tuple[str, ...], tuple[str, ...]]:
    """
    Return a 2-item tuple containing the primary key column names first,
    then the other column names.
    """
    primary_key_column_names: list[str] = []
    other_column_names: list[str] = []
    column: Column
    for column in table.columns:
        if column.primary_key:
            primary_key_column_names.append(column.name)
        else:
            other_column_names.append(column.name)
    return tuple(primary_key_column_names), tuple(other_column_names)


def get_bind_metadata(bind: str | URL | Engine | Connection) -> MetaData:
    """
    Get SQLAlchemy metadata for a connection string, engine, or connection.
    """
    if isinstance(bind, (str, URL)):
        bind = create_engine(bind)
    metadata: MetaData = MetaData()
    metadata.reflect(bind=bind, views=True, resolve_fks=True)
    return metadata
