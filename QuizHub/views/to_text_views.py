from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from pdf2image import convert_from_bytes
import pytesseract
from PIL import Image
import io
import numpy as np
import cv2

# Tesseractのパス
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

def preprocess_image(pil_image):
    cv_image = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
    gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (3, 3), 0)
    _, thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return Image.fromarray(thresh)

@csrf_exempt
def ocr_image(request):
    if request.method == 'POST':
        try:
            uploaded_file = request.FILES.get("image")
            if not uploaded_file:
                return JsonResponse({'error': 'ファイルがありません'}, status=400)

            file_bytes = uploaded_file.read()
            content_type = uploaded_file.content_type

            extracted_text = ""

            if content_type == 'application/pdf':
                images = convert_from_bytes(file_bytes, dpi=400)
            else:
                image = Image.open(io.BytesIO(file_bytes))
                images = [image]

            for img in images:
                processed_img = preprocess_image(img)
                text = pytesseract.image_to_string(
                    processed_img,
                    config='--oem 3 --psm 6',
                    lang='jpn'
                )
                extracted_text += text + "\n"

            return JsonResponse({'text': extracted_text.strip()})

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    else:
        return JsonResponse({'error': 'POSTメソッドのみ対応'}, status=405)
