from django.db import models


class Categoria(models.Model):
    nombre = models.CharField(max_length=100, unique=True)

    def save(self, *args, **kwargs):
        self.nombre = self.nombre.upper().strip()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.nombre


class Subcategoria(models.Model):
    categoria = models.ForeignKey(Categoria, on_delete=models.PROTECT, related_name='subcategorias')
    nombre = models.CharField(max_length=100)

    def save(self, *args, **kwargs):
        self.nombre = self.nombre.upper().strip()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.categoria.nombre} > {self.nombre}"


class MedidaPrincipal(models.Model):
    valor = models.CharField(max_length=20, unique=True)

    def save(self, *args, **kwargs):
        self.valor = self.valor.upper().strip()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.valor


class MedidaSecundaria(models.Model):
    valor = models.CharField(max_length=20, unique=True)

    def save(self, *args, **kwargs):
        self.valor = self.valor.upper().strip()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.valor


class CodigoUno(models.Model):
    valor = models.CharField(max_length=10, unique=True)

    def save(self, *args, **kwargs):
        self.valor = self.valor.upper().strip()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.valor


class CodigoDos(models.Model):
    valor = models.CharField(max_length=10, unique=True)

    def save(self, *args, **kwargs):
        self.valor = self.valor.upper().strip()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.valor
