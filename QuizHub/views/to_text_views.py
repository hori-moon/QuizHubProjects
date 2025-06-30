from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import requests
import io

@csrf_exempt
def ocr_image(request):
    if request.method == 'POST':
        uploaded_file = request.FILES.get("image")
        if not uploaded_file:
            return JsonResponse({'error': 'ファイルがありません'}, status=400)

        try:
            image_data = uploaded_file.read()
            endpoint = settings.AZURE_OCR_ENDPOINT.rstrip("/") + "/vision/v3.2/ocr"
            headers = {
                "Ocp-Apim-Subscription-Key": settings.AZURE_OCR_KEY,
                "Content-Type": "application/octet-stream"
            }

            response = requests.post(endpoint, headers=headers, data=image_data)
            if response.status_code != 200:
                return JsonResponse({'error': response.text}, status=response.status_code)

            result = response.json()
            extracted_text = ""

            # テキスト抽出（日本語対応）
            for region in result.get("regions", []):
                for line in region.get("lines", []):
                    line_text = " ".join([word["text"] for word in line.get("words", [])])
                    extracted_text += line_text + "\n"

            return JsonResponse({'text': extracted_text.strip()})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'POSTメソッドのみ対応'}, status=405)
