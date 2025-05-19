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

