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

def create_account(request):
    return render(request, 'create_account.html')

def login_view(request):
    return render(request, 'login.html')

def logout_view(request):
    return render(request, 'logout.html')

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

from django.shortcuts import render
from .services.supabase_client import supabase

def view_questions(request):
    # Supabaseからquestionsテーブルのデータを取得
    response = supabase.table('questions').select('question_id, content').execute()

    # エラー処理も追加したほうが安全（省略可）
    questions = response.data if response.data else []

    return render(request, 'view_questions.html', {'questions': questions})
