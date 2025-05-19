######## OCR処理 ########
import base64
import io
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from PIL import Image
import pytesseract
import json

@csrf_exempt
def ocr_image(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        image_data = data['image'].split(',')[1]
        image_bytes = base64.b64decode(image_data)
        image = Image.open(io.BytesIO(image_bytes))
        text = pytesseract.image_to_string(image, lang='jpn')  # 日本語に対応
        return JsonResponse({'text': text})
    return JsonResponse({'error': 'Invalid request'}, status=400)

# Tesseract のパスを指定
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# 例: 画像から日本語をOCR
def run_ocr(image_path):
    image = Image.open(image_path)
    text = pytesseract.image_to_string(image, lang='jpn')  # 'jpn' は日本語OCR用
    return text
