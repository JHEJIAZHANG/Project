import os
from typing import Dict


def ocr_image_bytes(data: bytes) -> Dict:
    """Perform OCR on image bytes.

    Priority:
    1) Google Cloud Vision if GOOGLE_APPLICATION_CREDENTIALS is set and library available.
    2) pytesseract if available and TESSERACT_CMD provided (optional).
    3) Fallback: return empty text.
    """
    # Try Google Vision first
    try:
        if os.getenv("GOOGLE_APPLICATION_CREDENTIALS"):
            from google.cloud import vision  # type: ignore
            client = vision.ImageAnnotatorClient()
            image = vision.Image(content=data)
            resp = client.text_detection(image=image)
            text = (resp.full_text_annotation.text or "").strip()
            return {"engine": "gcv", "text": text}
    except Exception:
        pass

    # Try pytesseract
    try:
        import pytesseract  # type: ignore
        from PIL import Image  # type: ignore
        import io
        if os.getenv("TESSERACT_CMD"):
            pytesseract.pytesseract.tesseract_cmd = os.getenv("TESSERACT_CMD")
        img = Image.open(io.BytesIO(data))
        text = pytesseract.image_to_string(img)
        return {"engine": "tesseract", "text": (text or "").strip()}
    except Exception:
        pass

    return {"engine": "none", "text": ""}


