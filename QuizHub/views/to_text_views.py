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
            logger.debug("リクエスト受信")
            data = json.loads(request.body)
            logger.debug("JSON読み込み成功")

            if 'image' not in data:
                logger.warning("画像データがありません")
                return JsonResponse({'error': '画像データがありません'}, status=400)

            image_data = data['image'].split(',')[1]
            logger.debug(f"Base64画像サイズ: {len(image_data)}")

            image_bytes = base64.b64decode(image_data)
            logger.debug("Base64デコード成功")

            image = Image.open(io.BytesIO(image_bytes))
            logger.debug("画像読み込み成功")

            text = pytesseract.image_to_string(image, lang='jpn')
            logger.debug("OCR処理成功")

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

