######## OCR処理 ########
import base64
import io
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from PIL import Image
import pytesseract
import json

import logging
logger = logging.getLogger(__name__)

@csrf_exempt
def ocr_image(request):
    if request.method == 'POST':
        try:
            image_file = request.FILES.get('image')  # ← FormData からのファイル取得
            if not image_file:
                return JsonResponse({'error': '画像ファイルがありません'}, status=400)

            image = Image.open(image_file)  # PILで画像オープン
            text = pytesseract.image_to_string(image, lang='jpn')  # OCR処理

            return JsonResponse({'text': text})
        except Exception as e:
            logger.exception("OCR処理中に例外が発生")
            return JsonResponse({'error': str(e)}, status=400)
    return JsonResponse({'error': 'Invalid request'}, status=400)




# Tesseract のパスを指定
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# 例: 画像から日本語をOCR
def run_ocr(image_path):
    image = Image.open(image_path)
    text = pytesseract.image_to_string(image, lang='jpn')  # 'jpn' は日本語OCR用
    return text

