from django.views.decorators.csrf import csrf_exempt
from ..services.supabase_client import supabase
from django.shortcuts import render

@csrf_exempt
def view_questions(request):
    question_id = request.GET.get('question_id') or request.POST.get('question_id')

    questions = []
    answers_map = {}
    folder_id = None
    result_message = None

    if question_id:
        # 問題取得
        response = supabase.table('questions').select('question_id, content, folder_id, answer_id').eq('question_id', question_id).execute()
        questions = response.data if response.data else []

        if questions:
            folder_id = questions[0]['folder_id']
            answer_ids = [q['answer_id'] for q in questions]

            # 解答取得
            answer_response = supabase.table('answers').select('answer_id, correct, options').in_('answer_id', answer_ids).execute()
            answers = answer_response.data if answer_response.data else []
            answers_map = {a['answer_id']: a for a in answers}

            # 正誤判定処理
            if request.method == 'POST':
                answer_input = request.POST.get('answer')
                question = questions[0]
                answer = answers_map.get(question['answer_id'])

                if answer:
                    if answer.get('options'):
                        try:
                            is_correct = answer_input in answer['correct']
                        except (ValueError, TypeError):
                            is_correct = False
                    else:
                        # テキスト解答 → 正解リストと一致するか（大文字小文字を無視）
                        is_correct = answer_input.strip().lower() in [c.strip().lower() for c in answer['correct']]

                    result_message = "正解です！" if is_correct else "不正解です。"

    return render(request, 'view_questions.html', {
        'questions': questions,
        'answers_map': answers_map,
        'folder_id': folder_id,
        'result_message': result_message
    })
