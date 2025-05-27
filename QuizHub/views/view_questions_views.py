from django.shortcuts import render
from ..services.supabase_client import supabase

def view_questions(request):
    question_id = request.GET.get('question_id')

    if question_id:
        response = supabase.table('questions').select('question_id, content, folder_id').eq('question_id', question_id).execute()
        questions = response.data if response.data else []
    else:
        questions = []

    folder_id = questions[0]['folder_id'] if questions else None

    return render(request, 'view_questions.html', {
        'questions': questions,
        'folder_id': folder_id
    })