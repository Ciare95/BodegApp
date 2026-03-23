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
    estado = models.CharField(max_length=10, choices=ESTADO_CHOICES, default='verde')
    orden = models.PositiveIntegerField(default=0)
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)
    actualizado_por = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, blank=True, related_name='productos_actualizados')

    class Meta:
        unique_together = [
            ['subcategoria', 'medida_principal', 'medida_secundaria'],  # nombre único
        ]
        ordering = ['subcategoria__categoria', 'orden', 'id']

    @property
    def nombre_completo(self):
        partes = [
            self.subcategoria.categoria.nombre,
            self.subcategoria.nombre,
            self.medida_principal.valor,
        ]
        if self.medida_secundaria:
            partes.append(f"X {self.medida_secundaria.valor}")
        return ' '.join(partes)

    @property
    def codigo_completo(self):
        """Retorna el primer código como representación principal."""
        primer = self.codigos.order_by('id').first()
        if primer:
            return f"{primer.codigo_uno.valor}-{primer.codigo_dos.valor}"
        return '—'

    @property
    def codigos_lista(self):
        return [
            f"{c.codigo_uno.valor}-{c.codigo_dos.valor}"
            for c in self.codigos.select_related('codigo_uno', 'codigo_dos').order_by('id')
        ]

    def __str__(self):
        return f"{self.codigo_completo} — {self.nombre_completo}"


class ProductoCodigo(models.Model):
    """Código identificatorio de un producto. Un producto puede tener varios."""
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name='codigos')
    codigo_uno = models.ForeignKey(CodigoUno, on_delete=models.PROTECT, related_name='producto_codigos')
    codigo_dos = models.ForeignKey(CodigoDos, on_delete=models.PROTECT, related_name='producto_codigos')

    class Meta:
        unique_together = [['codigo_uno', 'codigo_dos']]  # código único globalmente

    def __str__(self):
        return f"{self.codigo_uno.valor}-{self.codigo_dos.valor}"


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
