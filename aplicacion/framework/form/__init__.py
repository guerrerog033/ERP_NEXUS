from __future__ import annotations

# ==========================================================
# Registro automático
# ==========================================================

from . import widget_factory
from . import accessors

# ==========================================================
# Núcleo
# ==========================================================

from .builder import FormBuilder
from .binding import FormBinding
from .engine import FormEngine
from .events import FormEvents
from .widget_factory import WidgetFactory

# ==========================================================
# Definiciones
# ==========================================================

from .form_definition import FormDefinition
from .field import Field
from .field_group import FieldGroup
from .form_layout import FormLayout

# ==========================================================
# Campos
# ==========================================================

from .text_field import TextField
from .textarea_field import TextAreaField
from .email_field import EmailField
from .password_field import PasswordField
from .phone_field import PhoneField
from .integer_field import IntegerField
from .decimal_field import DecimalField
from .date_field import DateField
from .check_field import CheckField
from .combo_field import ComboField
from .lookup_field import LookupField

__all__ = [
    "FormDefinition",
    "Field",
    "FieldGroup",
    "FormLayout",
    "FormBuilder",
    "FormBinding",
    "FormEngine",
    "FormEvents",
    "WidgetFactory",
    "TextField",
    "TextAreaField",
    "EmailField",
    "PasswordField",
    "PhoneField",
    "IntegerField",
    "DecimalField",
    "DateField",
    "CheckField",
    "ComboField",
    "LookupField",
]