import base64
import io
import segno

def generate_epc_qr_code(name, iban, amount, reference):
    """
    Generates a SEPA EPC QR code and returns it as a base64 encoded PNG string.
    """
    sepa_payment = segno.helpers.make_epc_data(
        name=name,
        iban=iban,
        amount=amount,
        reference=reference
    )
    
    buffer = io.BytesIO()
    segno.make(sepa_payment, error='h').save(buffer, kind='png', scale=5)
    
    # Reset buffer position to the beginning
    buffer.seek(0)
    
    # Encode the PNG image to base64
    base64_png = base64.b64encode(buffer.read()).decode('utf-8')
    
    return f'data:image/png;base64,{base64_png}'
