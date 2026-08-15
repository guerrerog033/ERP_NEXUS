from ..column_registry import ColumnRegistry

from .text_factory import TextColumnFactory
from .integer_factory import IntegerColumnFactory
from .decimal_factory import DecimalColumnFactory
from .date_factory import DateColumnFactory
from .check_factory import CheckColumnFactory
from .lookup_factory import LookupColumnFactory
from .status_factory import StatusColumnFactory


ColumnRegistry.registrar(
    "text",
    TextColumnFactory(),
)

ColumnRegistry.registrar(
    "integer",
    IntegerColumnFactory(),
)

ColumnRegistry.registrar(
    "decimal",
    DecimalColumnFactory(),
)

ColumnRegistry.registrar(
    "date",
    DateColumnFactory(),
)

ColumnRegistry.registrar(
    "check",
    CheckColumnFactory(),
)

ColumnRegistry.registrar(
    "lookup",
    LookupColumnFactory(),
)

ColumnRegistry.registrar(
    "status",
    StatusColumnFactory(),
)