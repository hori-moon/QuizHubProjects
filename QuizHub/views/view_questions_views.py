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

    if question_id:
        # 問題取得
        response = supabase.table('questions') \
            .select('question_id, content, folder_id, answer_id') \
            .eq('question_id', question_id).execute()
        questions = response.data if response.data else []

        if questions:
            folder_id = questions[0]['folder_id']
            answer_ids = [q['answer_id'] for q in questions]

            # 解答取得
            answer_response = supabase.table('answers') \
                .select('answer_id, correct, options') \
                .in_('answer_id', answer_ids).execute()
            answers = answer_response.data if answer_response.data else []
            answers_map = {a['answer_id']: a for a in answers}

            # 正誤判定処理
            if request.method == 'POST':
                # POSTされた質問IDに対応する情報を取得
                question = questions[0]
                answer = answers_map.get(question['answer_id'])

                if answer:
                    correct_set = set(answer['correct'])  # 正解一覧（文字列のセット）

                    if answer.get('options'):
                        # 選択肢がある → ラジオ or チェックボックス
                        user_answers = request.POST.getlist('answer')  # リストで取得
                        user_set = set(user_answers)

                        is_correct = user_set == correct_set
                    else:
                        # テキスト入力 → 大文字小文字・前後空白を無視して一致判定
                        answer_input = request.POST.get('answer', '').strip().lower()
                        is_correct = answer_input in [c.strip().lower() for c in answer['correct']]

                    result_message = "正解です！" if is_correct else "不正解です。"

    return render(request, 'view_questions.html', {
        'questions': questions,
        'answers_map': answers_map,
        'folder_id': folder_id,
        'result_message': result_message,
    })
