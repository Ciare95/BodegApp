from django.contrib import admin
from categorias.models import (
    Categoria,
    Subcategoria,
    MedidaPrincipal,
    MedidaSecundaria,
    CodigoUno,
    CodigoDos,
)

admin.site.register(Categoria)
admin.site.register(Subcategoria)
admin.site.register(MedidaPrincipal)
admin.site.register(MedidaSecundaria)
admin.site.register(CodigoUno)
admin.site.register(CodigoDos)
