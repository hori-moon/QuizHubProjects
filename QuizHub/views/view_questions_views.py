from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from ..services.supabase_client import supabase

@csrf_exempt
def view_questions(request):
    question_id = request.GET.get('question_id') or request.POST.get('question_id')

    questions = []
    answers_map = {}
    folder_id = None
    result_message = None
    answered_question_id = None
    prev_question_id = None
    next_question_id = None

    if question_id:
        # 現在の問題取得
        response = supabase.table('questions') \
            .select('question_id, content, folder_id, answer_id') \
            .eq('question_id', question_id).execute()
        questions = response.data if response.data else []

        if questions:
            question = questions[0]
            folder_id = question['folder_id']
            answer_ids = [q['answer_id'] for q in questions]

            # フォルダー内のすべての問題（昇順）を取得
            all_questions = supabase.table('questions') \
                .select('question_id') \
                .eq('folder_id', folder_id) \
                .order('question_id', desc=False) \
                .execute()
            question_list = [q['question_id'] for q in all_questions.data]

            # 現在のインデックスを取得
            current_index = question_list.index(int(question_id))

            # 前・次の question_id を計算
            if current_index > 0:
                prev_question_id = question_list[current_index - 1]
            if current_index < len(question_list) - 1:
                next_question_id = question_list[current_index + 1]

            # 解答取得
            answer_response = supabase.table('answers') \
                .select('answer_id, correct, options') \
                .in_('answer_id', answer_ids).execute()
            answers = answer_response.data if answer_response.data else []
            answers_map = {a['answer_id']: a for a in answers}

            # 正誤判定
            if request.method == 'POST':
                answer = answers_map.get(question['answer_id'])
                if answer:
                    correct_set = set(answer['correct'])
                    is_correct = False

                    if answer.get('options'):
                        user_answers = request.POST.getlist('answer')
                        is_correct = set(user_answers) == correct_set
                    else:
                        input_answer = request.POST.get('answer', '').strip().lower()
                        is_correct = input_answer in [c.strip().lower() for c in answer['correct']]

                    result_message = "正解です！" if is_correct else "不正解です。"
                    answered_question_id = question['question_id']

    return render(request, 'view_questions.html', {
        'questions': questions,
        'answers_map': answers_map,
        'folder_id': folder_id,
        'result_message': result_message,
        'answered_question_id': str(answered_question_id) if answered_question_id else None,
        'prev_question_id': prev_question_id,
        'next_question_id': next_question_id,
    })
