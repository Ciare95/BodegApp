import io
import base64
import qrcode
from qrcode.image.pil import PilImage


def generar_qr(producto_id: int) -> str:
    """
    Genera un código QR con el ID del producto y lo retorna en base64.

    Args:
        producto_id: ID del producto a codificar en el QR.

    Returns:
        str: Imagen PNG codificada en base64 (sin prefijo data URI).
    """
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=4,
    )
    qr.add_data(str(producto_id))
    qr.make(fit=True)

    imagen: PilImage = qr.make_image(fill_color='black', back_color='white')

    buffer = io.BytesIO()
    imagen.save(buffer, format='PNG')
    buffer.seek(0)

    return base64.b64encode(buffer.read()).decode('utf-8')


def generar_qr_bytes(producto_id: int) -> bytes:
    """
    Genera un código QR con el ID del producto y lo retorna como bytes PNG.
    Usado para la descarga directa del archivo.

    Args:
        producto_id: ID del producto a codificar en el QR.

    Returns:
        bytes: Imagen PNG en bytes.
    """
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=4,
    )
    qr.add_data(str(producto_id))
    qr.make(fit=True)

    imagen: PilImage = qr.make_image(fill_color='black', back_color='white')

    buffer = io.BytesIO()
    imagen.save(buffer, format='PNG')
    buffer.seek(0)

    return buffer.read()
