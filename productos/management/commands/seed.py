import random
from django.core.management.base import BaseCommand
from categorias.models import Categoria, Subcategoria, MedidaPrincipal, MedidaSecundaria, CodigoUno, CodigoDos
from productos.models import Producto


CATEGORIAS = {
    'TORNILLERIA': ['TORNILLO GRADO 2', 'TORNILLO GRADO 5', 'TORNILLO GRADO 8', 'TORNILLO INOXIDABLE', 'TORNILLO GALVANIZADO'],
    'TUERCAS': ['TUERCA HEXAGONAL', 'TUERCA AUTOBLOCANTE', 'TUERCA MARIPOSA', 'TUERCA CIEGA'],
    'ARANDELAS': ['ARANDELA PLANA', 'ARANDELA DE PRESION', 'ARANDELA DENTADA'],
    'PERNOS': ['PERNO CARROCERO', 'PERNO ANCLA', 'PERNO ESPARRAGO'],
    'CLAVOS': ['CLAVO LISO', 'CLAVO GALVANIZADO', 'CLAVO PUNTA PARIS'],
    'VARILLAS': ['VARILLA ROSCADA', 'VARILLA LISA', 'VARILLA CORRUGADA'],
    'CABLES': ['CABLE ACERO', 'CABLE GALVANIZADO', 'CABLE INOXIDABLE'],
    'CADENAS': ['CADENA SIMPLE', 'CADENA DOBLE', 'CADENA GALVANIZADA'],
}

MEDIDAS_PRINCIPALES = [
    '1/4', '5/16', '3/8', '7/16', '1/2', '9/16', '5/8', '3/4',
    '7/8', '1', '1 1/8', '1 1/4', '1 3/8', '1 1/2', '1 3/4', '2',
    'M6', 'M8', 'M10', 'M12', 'M14', 'M16', 'M20', 'M24',
]

MEDIDAS_SECUNDARIAS = [
    '1/2', '3/4', '1', '1 1/4', '1 1/2', '2', '2 1/2', '3',
    '3 1/2', '4', '4 1/2', '5', '6', '8', '10', '12',
    '20MM', '25MM', '30MM', '40MM', '50MM', '60MM', '75MM', '100MM',
]

PREFIJOS = ['EB', 'GB', 'HB', 'AB', 'CB', 'DB', 'FB', 'IB', 'JB', 'KB']

SUFIJOS = [str(n) for n in range(10, 200, 5)]


class Command(BaseCommand):
    help = 'Genera datos de prueba: catalogos y ~1000 productos'

    def handle(self, *args, **options):
        self.stdout.write('Creando catalogos...')

        subcats = []
        for cat_nombre, sub_nombres in CATEGORIAS.items():
            cat, _ = Categoria.objects.get_or_create(nombre=cat_nombre)
            for sub_nombre in sub_nombres:
                sub, _ = Subcategoria.objects.get_or_create(categoria=cat, nombre=sub_nombre)
                subcats.append(sub)

        meds_p = [MedidaPrincipal.objects.get_or_create(valor=v)[0] for v in MEDIDAS_PRINCIPALES]
        meds_s = [MedidaSecundaria.objects.get_or_create(valor=v)[0] for v in MEDIDAS_SECUNDARIAS]
        cod_uno = [CodigoUno.objects.get_or_create(valor=v)[0] for v in PREFIJOS]
        cod_dos = [CodigoDos.objects.get_or_create(valor=v)[0] for v in SUFIJOS]

        self.stdout.write('Creando productos...')

        estados = ['verde', 'amarillo', 'rojo']
        creados = 0
        omitidos = 0

        codigos_disponibles = [(c1, c2) for c1 in cod_uno for c2 in cod_dos]
        random.shuffle(codigos_disponibles)
        codigo_idx = 0

        for sub in subcats:
            for mp in meds_p:
                for ms in meds_s:
                    if creados >= 1000:
                        break

                    c1, c2 = None, None
                    if random.random() < 0.7 and codigo_idx < len(codigos_disponibles):
                        c1, c2 = codigos_disponibles[codigo_idx]
                        codigo_idx += 1

                    try:
                        Producto.objects.create(
                            subcategoria=sub,
                            medida_principal=mp,
                            medida_secundaria=ms,
                            codigo_uno=c1,
                            codigo_dos=c2,
                            estado=random.choice(estados),
                        )
                        creados += 1
                        if creados % 100 == 0:
                            self.stdout.write(f'  {creados} productos creados...')
                    except Exception:
                        omitidos += 1

                if creados >= 1000:
                    break
            if creados >= 1000:
                break

        self.stdout.write(self.style.SUCCESS(
            f'Listo. {creados} productos creados, {omitidos} omitidos por duplicados.'
        ))
