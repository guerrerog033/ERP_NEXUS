from ..accessor_registry import AccessorRegistry

from .text_accessor import TextAccessor
from .textarea_accessor import TextAreaAccessor
from .password_accessor import PasswordAccessor
from .phone_accessor import PhoneAccessor
from .integer_accessor import IntegerAccessor
from .decimal_accessor import DecimalAccessor
from .date_accessor import DateAccessor
from .check_accessor import CheckAccessor
from .combo_accessor import ComboAccessor
from .lookup_accessor import LookupAccessor
from .documento_accessor import DocumentoAccessor


AccessorRegistry.registrar(
    "text",
    TextAccessor(),
)

AccessorRegistry.registrar(
    "textarea",
    TextAreaAccessor(),
)

AccessorRegistry.registrar(
    "password",
    PasswordAccessor(),
)

AccessorRegistry.registrar(
    "phone",
    PhoneAccessor(),
)

AccessorRegistry.registrar(
    "integer",
    IntegerAccessor(),
)

AccessorRegistry.registrar(
    "decimal",
    DecimalAccessor(),
)

AccessorRegistry.registrar(
    "date",
    DateAccessor(),
)

AccessorRegistry.registrar(
    "check",
    CheckAccessor(),
)

AccessorRegistry.registrar(
    "combo",
    ComboAccessor(),
)

AccessorRegistry.registrar(
    "lookup",
    LookupAccessor(),
)

AccessorRegistry.registrar(
    "documento",
    DocumentoAccessor(),
)
