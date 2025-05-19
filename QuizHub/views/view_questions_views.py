from django.shortcuts import render
from .services.supabase_client import supabase

def view_questions(request):
    # Supabaseからquestionsテーブルのデータを取得
    response = supabase.table('questions').select('question_id, content').execute()

    # エラー処理も追加したほうが安全（省略可）
    questions = response.data if response.data else []

    return render(request, 'view_questions.html', {'questions': questions})
