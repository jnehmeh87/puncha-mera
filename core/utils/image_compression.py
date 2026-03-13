import sys
import os
from io import BytesIO
from PIL import Image
from django.core.files.uploadedfile import InMemoryUploadedFile, TemporaryUploadedFile
from django.core.files.base import ContentFile

def compress_image(uploaded_image, max_size=(1920, 1080), quality=75):
    """
    Compresses an uploaded image to WebP format, resizing if necessary.
    Returns a new InMemoryUploadedFile. Returns original if not an upload or if error.
    """
    if not uploaded_image:
        return uploaded_image

    # Only compress if it's an uploaded file directly from memory or temp
    file_obj = getattr(uploaded_image, 'file', None)
    if not isinstance(file_obj, (InMemoryUploadedFile, TemporaryUploadedFile)):
        return uploaded_image

    try:
        # Open image using Pillow
        img = Image.open(uploaded_image)
        
        # Convert to RGB if it's RGBA or P to avoid issues with WebP/JPEG saving sometimes
        if img.mode != "RGB":
            # For receipts and simple images, RGB is fine and drops alpha transparency
            img = img.convert("RGB")
            
        # Resize keeping aspect ratio
        img.thumbnail(max_size, Image.Resampling.LANCZOS)
        
        # Save to BytesIO
        output = BytesIO()
        img.save(output, format='WebP', quality=quality)
        output_size = output.tell()
        output.seek(0)
        
        # Determine new filename
        base_name = os.path.splitext(uploaded_image.name)[0]
        new_name = f"{base_name}.webp"
        
        # Create new InMemoryUploadedFile
        compressed_image = InMemoryUploadedFile(
            file=output,
            field_name=getattr(uploaded_image, 'field_name', 'image'),
            name=new_name,
            content_type='image/webp',
            size=output_size,
            charset=None
        )
        return compressed_image
    except Exception as e:
        print(f"Error compressing image: {e}")
        return uploaded_image
