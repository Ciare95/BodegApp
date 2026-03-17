from django.core.exceptions import ValidationError
from django.db.models import ProtectedError


def eliminar_valor_catalogo(instancia) -> None:
    """
    Elimina un valor de catálogo validando que no esté referenciado
    por ningún producto activo.

    Django ya protege a nivel de base de datos con on_delete=PROTECT,
    pero esta función intercepta el error y lanza un ValidationError
    con un mensaje claro en español.

    Args:
        instancia: Instancia de cualquier modelo de catálogo
                   (Categoria, Subcategoria, MedidaPrincipal, etc.)

    Raises:
        ValidationError: si el valor está referenciado por al menos un producto.
    """
    try:
        instancia.delete()
    except ProtectedError:
        raise ValidationError(
            f"No se puede eliminar '{instancia}' porque está siendo "
            f"utilizado por uno o más productos. "
            f"Reasigna o elimina esos productos primero."
        )
