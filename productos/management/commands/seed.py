from django.core.management.base import BaseCommand
from django.db import transaction

from categorias.models import (
    Categoria, Subcategoria,
    MedidaPrincipal, MedidaSecundaria,
    CodigoUno, CodigoDos, CodigoLibre,
)
from productos.models import Producto, ProductoCodigo


CATEGORIAS = ['TORNILLERIA', 'HERRAMIENTAS', 'TUBERIA']

SUBCATEGORIAS = [
    ('TORNILLERIA', 'PERNOS'),
    ('TORNILLERIA', 'TUERCAS'),
    ('TORNILLERIA', 'ARANDELAS'),
    ('HERRAMIENTAS', 'LLAVES'),
    ('HERRAMIENTAS', 'DESTORNILLADORES'),
    ('TUBERIA', 'PVC'),
]

MEDIDAS_PRINCIPALES = ['1/4', '3/8', '1/2', '3/4', '1']
MEDIDAS_SECUNDARIAS = ['1"', '2"', '3"', '5"']

# Prefijos: letras (A, B, C, AB, BB) + números (1, 2, 3) + D sin productos
CODIGOS_UNO = ['A', 'B', 'C', 'AB', 'BB', 'D', '1', '2', '3']
CODIGOS_DOS = ['1', '2', '3', '4', 'AB']

# (subcategoria_nombre, medida_principal, medida_secundaria_o_None, estado, prefijo, sufijo)
PRODUCTOS = [
    # ── Prefijo A (4 productos, orden por sufijo: AB, 1, 2, 3)
    ('PERNOS',          '1/4',  None,   'verde',    'A',  '1'),
    ('PERNOS',          '3/8',  None,   'amarillo', 'A',  '2'),
    ('PERNOS',          '1/2',  None,   'verde',    'A',  '3'),
    ('TUERCAS',         '1/4',  None,   'rojo',     'A',  'AB'),
    # ── Prefijo AB (2 productos)
    ('ARANDELAS',       '1/4',  None,   'verde',    'AB', '1'),
    ('ARANDELAS',       '3/8',  None,   'rojo',     'AB', '2'),
    # ── Prefijo B (4 productos)
    ('TUERCAS',         '3/8',  None,   'verde',    'B',  '1'),
    ('TUERCAS',         '1/2',  None,   'verde',    'B',  '2'),
    ('LLAVES',          '3/4',  None,   'amarillo', 'B',  '3'),
    ('LLAVES',          '1',    None,   'verde',    'B',  '4'),
    # ── Prefijo BB (1 producto)
    ('PERNOS',          '3/4',  '1"',   'verde',    'BB', '1'),
    # ── Prefijo C (1 producto)
    ('TUERCAS',         '3/4',  None,   'verde',    'C',  '1'),
    # ── Prefijo D: sin productos (solo existe el CodigoUno)
    # ── Prefijo 1 (2 productos)
    ('LLAVES',          '1/4',  '1"',   'verde',    '1',  '1'),
    ('LLAVES',          '3/8',  '2"',   'verde',    '1',  '2'),
    # ── Prefijo 2 (1 producto)
    ('PVC',             '3/4',  '3"',   'amarillo', '2',  '1'),
    # ── Prefijo 3 (1 producto)
    ('DESTORNILLADORES','1/2',  '5"',   'verde',    '3',  '1'),
]


class Command(BaseCommand):
    help = 'Carga datos de prueba para testear la funcionalidad de Revisión de Bodega.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--flush',
            action='store_true',
            help='Elimina productos, códigos y catálogos existentes antes de crear los datos.',
        )

    @transaction.atomic
    def handle(self, *args, **options):
        if options['flush']:
            ProductoCodigo.objects.all().delete()
            Producto.objects.all().delete()
            CodigoDos.objects.all().delete()
            CodigoUno.objects.all().delete()
            MedidaSecundaria.objects.all().delete()
            MedidaPrincipal.objects.all().delete()
            Subcategoria.objects.all().delete()
            Categoria.objects.all().delete()
            self.stdout.write(self.style.WARNING('  Datos anteriores eliminados.'))

        # Categorías
        cats = {}
        for nombre in CATEGORIAS:
            obj, created = Categoria.objects.get_or_create(nombre=nombre)
            cats[obj.nombre] = obj
            if created:
                self.stdout.write(f'  + Categoría: {obj.nombre}')

        # Subcategorías
        subs = {}
        for cat_nombre, sub_nombre in SUBCATEGORIAS:
            obj, created = Subcategoria.objects.get_or_create(
                categoria=cats[cat_nombre], nombre=sub_nombre
            )
            subs[obj.nombre] = obj
            if created:
                self.stdout.write(f'  + Subcategoría: {obj.nombre}')

        # Medidas principales
        mps = {}
        for valor in MEDIDAS_PRINCIPALES:
            obj, _ = MedidaPrincipal.objects.get_or_create(valor=valor)
            mps[obj.valor] = obj

        # Medidas secundarias
        mss = {}
        for valor in MEDIDAS_SECUNDARIAS:
            obj, _ = MedidaSecundaria.objects.get_or_create(valor=valor)
            mss[obj.valor] = obj

        # Prefijos (CodigoUno)
        cu = {}
        for valor in CODIGOS_UNO:
            obj, _ = CodigoUno.objects.get_or_create(valor=valor)
            cu[obj.valor] = obj

        # Sufijos (CodigoDos)
        cd = {}
        for valor in CODIGOS_DOS:
            obj, _ = CodigoDos.objects.get_or_create(valor=valor)
            cd[obj.valor] = obj

        # Productos y sus códigos
        creados = 0
        existentes = 0
        for sub_n, mp_v, ms_v, estado, prefijo, sufijo in PRODUCTOS:
            ms_obj = mss.get(ms_v) if ms_v else None
            prod, created = Producto.objects.get_or_create(
                subcategoria=subs[sub_n],
                medida_principal=mps[mp_v],
                medida_secundaria=ms_obj,
                defaults={'estado': estado},
            )
            if created:
                creados += 1
            else:
                existentes += 1

            ProductoCodigo.objects.get_or_create(
                codigo_uno=cu[prefijo],
                codigo_dos=cd[sufijo],
                defaults={'producto': prod},
            )
            codigo = f'{prefijo}-{sufijo}'
            if created:
                self.stdout.write(f'  + {codigo}: {prod.nombre_completo} [{estado}]')

        # Códigos libres: pares sin producto asignado para testear la funcionalidad
        # Usan prefijos/sufijos ya existentes en los catálogos
        CODIGOS_LIBRES = [
            ('B', 'AB'),   # testea: letra antes que número en sufijo
            ('C', '2'),
            ('C', '3'),
            ('D', '1'),    # prefijo D: sin productos, aquí sí tiene código libre
            ('D', '2'),
            ('1', 'AB'),
            ('2', '2'),
            ('3', '2'),
        ]
        libres_creados = 0
        for prefijo_cl, sufijo_cl in CODIGOS_LIBRES:
            # Saltar si este par ya está asignado a un producto
            if ProductoCodigo.objects.filter(
                codigo_uno=cu[prefijo_cl], codigo_dos=cd[sufijo_cl]
            ).exists():
                continue
            _, cl_created = CodigoLibre.objects.get_or_create(
                codigo_uno=cu[prefijo_cl],
                codigo_dos=cd[sufijo_cl],
            )
            if cl_created:
                libres_creados += 1
                self.stdout.write(f'  + Libre: {prefijo_cl}-{sufijo_cl}')

        self.stdout.write(self.style.SUCCESS(
            f'\nSeed completado: {creados} productos creados, {existentes} ya existian.\n'
            f'{libres_creados} codigos libres creados.\n'
            f'Prefijos cargados: {", ".join(CODIGOS_UNO)}\n'
            f'  - D no tiene productos (testea "Sin productos" en Revision)\n'
            f'  - A tiene sufijo "AB" (testea letras-antes-numeros en detalle)\n'
            f'  - B-AB y D-1/D-2 testean Codigo libre\n'
            f'  - Varios estados verde/amarillo/rojo para testear cambio de estado'
        ))
