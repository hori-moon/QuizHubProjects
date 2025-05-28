from django.shortcuts import render
from ..services.supabase_client import supabase

def view_questions(request):
    question_id = request.GET.get('question_id')

    questions = []
    answers_map = {}
    folder_id = None

    if question_id:
        # 質問取得
        response = supabase.table('questions').select('question_id, content, folder_id, answer_id').eq('question_id', question_id).execute()
        questions = response.data if response.data else []

        if questions:
            folder_id = questions[0]['folder_id']
            answer_ids = [q['answer_id'] for q in questions]

            # 解答取得
            answer_response = supabase.table('answers').select('answer_id, correct, options').in_('answer_id', answer_ids).execute()
            answers = answer_response.data if answer_response.data else []

            # answer_id をキーに辞書化
            answers_map = {a['answer_id']: a for a in answers}

    return render(request, 'view_questions.html', {
        'questions': questions,
        'answers_map': answers_map,
        'folder_id': folder_id
    })
