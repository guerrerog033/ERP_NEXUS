from .widget_registry import WidgetRegistry

from .widget_factories import (
    CheckWidgetFactory,
    ComboWidgetFactory,
    PasswordWidgetFactory,
    TextWidgetFactory,
    TextAreaWidgetFactory,
    PhoneWidgetFactory,
    IntegerWidgetFactory,
    DecimalWidgetFactory,
    DateWidgetFactory,
    LookupWidgetFactory,
    DocumentoWidgetFactory,
)

# ==========================================================
# Registro de widgets
# ==========================================================

_REGISTRO_WIDGETS = {

    "text": TextWidgetFactory(),

    "textarea": TextAreaWidgetFactory(),

    "password": PasswordWidgetFactory(),

    "phone": PhoneWidgetFactory(),

    "integer": IntegerWidgetFactory(),

    "decimal": DecimalWidgetFactory(),

    "date": DateWidgetFactory(),

    "lookup": LookupWidgetFactory(),

    "combo": ComboWidgetFactory(),

    "check": CheckWidgetFactory(),

    "documento": DocumentoWidgetFactory(),

}

for nombre, factory in _REGISTRO_WIDGETS.items():

    WidgetRegistry.registrar(
        nombre,
        factory,
    )


# ==========================================================
# Factory principal
# ==========================================================

class WidgetFactory:

    @staticmethod
    def crear(
        field,
        context=None,
    ):

        factory = WidgetRegistry.obtener(
            field.widget
        )

        if factory is None:

            raise RuntimeError(

                f"No existe una fábrica registrada para el widget "
                f"'{field.widget}'."

            )

        return factory.crear(
            field,
            context,
        )