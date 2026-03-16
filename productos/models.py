from django.db import models
from categorias.models import Subcategoria, MedidaPrincipal, MedidaSecundaria, CodigoUno, CodigoDos
from usuarios.models import Usuario


class Producto(models.Model):
    ESTADO_CHOICES = [
        ('verde', 'Verde'),
        ('amarillo', 'Amarillo'),
        ('rojo', 'Rojo'),
    ]

    subcategoria = models.ForeignKey(Subcategoria, on_delete=models.PROTECT, related_name='productos')
    medida_principal = models.ForeignKey(MedidaPrincipal, on_delete=models.PROTECT, related_name='productos')
    medida_secundaria = models.ForeignKey(MedidaSecundaria, on_delete=models.PROTECT, related_name='productos', null=True, blank=True)
    codigo_uno = models.ForeignKey(CodigoUno, on_delete=models.PROTECT, related_name='productos')
    codigo_dos = models.ForeignKey(CodigoDos, on_delete=models.PROTECT, related_name='productos')
    estado = models.CharField(max_length=10, choices=ESTADO_CHOICES, default='verde')
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)
    actualizado_por = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, blank=True, related_name='productos_actualizados')

    class Meta:
        unique_together = ['subcategoria', 'medida_principal', 'medida_secundaria', 'codigo_uno', 'codigo_dos']

    @property
    def nombre_completo(self):
        partes = [self.subcategoria.nombre, self.medida_principal.valor]
        if self.medida_secundaria:
            partes.append(f"X {self.medida_secundaria.valor}")
        return ' '.join(partes)

    @property
    def codigo_completo(self):
        return f"{self.codigo_uno.valor}-{self.codigo_dos.valor}"

    def __str__(self):
        return f"{self.codigo_completo} — {self.nombre_completo}"


class Historial(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name='historial')
    usuario = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, related_name='historial')
    campo_modificado = models.CharField(max_length=50)
    valor_anterior = models.CharField(max_length=255)
    valor_nuevo = models.CharField(max_length=255)
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-fecha']

    def __str__(self):
        return f"{self.producto} | {self.campo_modificado}: {self.valor_anterior} → {self.valor_nuevo}"
