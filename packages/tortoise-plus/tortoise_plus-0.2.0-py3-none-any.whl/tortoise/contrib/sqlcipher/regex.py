from __future__ import annotations

import enum
import re
from typing import cast

import aiosqlcipher
from pypika_tortoise.enums import SqlTypes
from pypika_tortoise.functions import Cast, Coalesce
from pypika_tortoise.terms import BasicCriterion, Term


class SQLcipherRegexMatching(enum.Enum):
    POSIX_REGEX = " REGEXP "
    IPOSIX_REGEX = " MATCH "


def posix_sqlite_regexp(field: Term, value: str):
    term = cast(Term, field.wrap_constant(value))
    return BasicCriterion(SQLcipherRegexMatching.POSIX_REGEX, Coalesce(Cast(field, SqlTypes.VARCHAR), ""), term)


def insensitive_posix_sqlite_regexp(field: Term, value: str):
    term = cast(Term, field.wrap_constant(value))
    return BasicCriterion(SQLcipherRegexMatching.IPOSIX_REGEX, Coalesce(Cast(field, SqlTypes.VARCHAR), ""), term)


async def install_regexp_functions(connection: aiosqlcipher.Connection):
    def regexp(expr, item):
        if not expr or not item:
            return False
        return re.search(expr, item) is not None

    def iregexp(expr, item):
        return re.search(expr, item, re.IGNORECASE) is not None

    await connection.create_function("regexp", 2, regexp)
    await connection.create_function("match", 2, iregexp)
