from rest_framework.permissions import BasePermission


class EsSoloAdmin(BasePermission):
    """
    Permite acceso únicamente a usuarios con rol 'admin'.
    """
    message = 'Solo los administradores pueden realizar esta acción.'

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.rol == 'admin'
        )


class EsAdminOEmpleado(BasePermission):
    """
    Permite acceso a usuarios con rol 'admin' o 'empleado'.
    Equivale a cualquier usuario autenticado con rol válido.
    """
    message = 'Debes estar autenticado con un rol válido.'

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.rol in ('admin', 'empleado')
        )
