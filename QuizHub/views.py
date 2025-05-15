from django.http import HttpResponse
from django.shortcuts import render

def to_text(request):
    return render(request, 'to_text.html')

def view_questions(request):
    return render(request, 'view_questions.html')

def create_room(request):
    return render(request, 'create_room.html')

def join_room(request):
    return render(request, 'join_room.html')

def login_view(request):
    return render(request, 'login.html')

def logout_view(request):
    return render(request, 'logout.html')

def to_set_quiz(request):
    if request.method == 'POST':
        ocr_result = request.POST.get('ocr_result')
        return render(request, 'to_set_quiz.html', {'ocr_result': ocr_result})
    return render(request, 'to_set_quiz.html')


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

import pytesseract
from PIL import Image

# Tesseract のパスを指定
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# 例: 画像から日本語をOCR
def run_ocr(image_path):
    image = Image.open(image_path)
    text = pytesseract.image_to_string(image, lang='jpn')  # 'jpn' は日本語OCR用
    return text


# Supabaseのクライアントを作成

from django.http import JsonResponse
from .services.quiz_service import insert_quiz_to_supabase

def insert_quiz(request):
    if request.method == "POST":
        question = request.POST.get("question")
        answer = request.POST.get("answer")
        result = insert_quiz_to_supabase(question, answer)
        return JsonResponse({"result": result.data})
    return JsonResponse({"error": "Only POST allowed"})


