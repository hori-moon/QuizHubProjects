from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.urls import reverse
from ..services.supabase_client import supabase
from datetime import datetime
import random
import pytz

def list_to_pg_array(lst):
    return "{" + ",".join(str(x) for x in lst) + "}"

def start_random_quiz(request):
    if request.method == 'POST':
        folder_id = int(request.POST.get('folder_id'))  # 文字列から整数へ変換
        pg_array_str = list_to_pg_array([folder_id])    # 配列として変換
        num_questions = int(request.POST.get('num_questions', 0))

        all_questions = supabase.table('questions') \
            .select('question_id') \
            .filter("folder_id", "cs", pg_array_str)  \
            .execute().data

        all_ids = [q['question_id'] for q in all_questions]
        random_ids = random.sample(all_ids, min(num_questions, len(all_ids)))

        request.session['quiz_questions'] = random_ids
        request.session['quiz_folder_id'] = folder_id  # 整数として保存

        return redirect(f"{reverse('view_questions')}?question_id={random_ids[0]}")
    return redirect('view_folder')

@csrf_exempt
@login_required
def view_questions(request):
    question_id_raw = request.GET.get('question_id') or request.POST.get('question_id')

    questions = []
    answers_map = {}
    result_message = request.session.pop('result_message', None)
    answered_question_id = request.session.pop('answered_question_id', None)
    prev_question_id = None
    next_question_id = None

    # quiz_questions, folder_id をセッションから取得
    question_list = request.session.get("quiz_questions")
    folder_id = request.GET.get("folder_id") or request.session.get("quiz_folder_id")

    # folder_id の正規化（list型やNoneに対応）
    if folder_id is None:
        folder_id_value = 0
    elif isinstance(folder_id, list):
        folder_id_value = folder_id[0]
    else:
        folder_id_value = folder_id

    # question_id がない場合：セッションから取得するルート
    if not question_id_raw:
        if not question_list or folder_id is None:
            return redirect("view_folder", folder_id=folder_id_value)

        index = int(request.GET.get("index", 0))
        if index >= len(question_list):
            return redirect("quiz_result")

        question_id = question_list[index]
    else:
        # ここで型変換＆バリデーション
        try:
            question_id = int(question_id_raw)
        except (TypeError, ValueError):
            return redirect("view_folder", folder_id=folder_id_value)

    # 該当の質問を取得
    response = supabase.table('questions') \
        .select('question_id, content, folder_id, answer_id') \
        .eq('question_id', question_id).execute()
    questions = response.data if response.data else []

    if questions:
        question = questions[0]
        question_folder_ids = question.get('folder_id', [])
        request.session['quiz_folder_id'] = folder_id_value  # 使用中フォルダを再保存

        answer_ids = [q['answer_id'] for q in questions]

        # クイズリストがセッションにない場合は取得
        if not question_list:
            pg_array_str = list_to_pg_array([int(folder_id_value)])
            all_questions = supabase.table('questions') \
                .select('question_id') \
                .filter("folder_id", "cs", pg_array_str)  \
                .order('question_id', desc=False) \
                .execute()
            question_list = [q['question_id'] for q in all_questions.data]
            request.session['quiz_questions'] = question_list

        # 前後のナビゲーションID
        if question_id in question_list:
            index = question_list.index(question_id)
            if index > 0:
                prev_question_id = question_list[index - 1]
            if index < len(question_list) - 1:
                next_question_id = question_list[index + 1]

        # 解答を取得
        answer_response = supabase.table('answers') \
            .select('answer_id, correct, options') \
            .in_('answer_id', answer_ids).execute()
        answers = answer_response.data if answer_response.data else []
        answers_map = {a['answer_id']: a for a in answers}

        # POST時の判定処理
        if request.method == 'POST':
            answer = answers_map.get(question['answer_id'])
            if answer:
                correct_set = set(answer['correct'])
                is_correct = False
                user_answers = []

                if answer.get('options'):
                    user_answers = request.POST.getlist('answer')
                    is_correct = set(user_answers) == correct_set
                else:
                    input_answer = request.POST.get('answer', '').strip().lower()
                    user_answers = [input_answer]
                    is_correct = input_answer in [c.strip().lower() for c in answer['correct']]

                result_message = "正解です！" if is_correct else "不正解です。"
                answered_question_id = question['question_id']

                # 履歴記録
                supabase_user_id = getattr(request.user, 'supabase_user_id', None)
                if supabase_user_id:
                    supabase.table("answers_history").insert({
                        "user_id": str(supabase_user_id),
                        "question_id": question['question_id'],
                        "answered_contents": user_answers,
                        "is_correct": is_correct,
                        "answered_at": datetime.now(pytz.UTC).isoformat(),
                        "folder_id": folder_id_value,
                    }).execute()

                request.session['result_message'] = result_message
                request.session['answered_question_id'] = question['question_id']
                return redirect(f"{request.path}?question_id={question['question_id']}")

    return render(request, 'view_questions.html', {
        'questions': questions,
        'answers_map': answers_map,
        'folder_id': folder_id_value,
        'result_message': result_message,
        'answered_question_id': str(answered_question_id) if answered_question_id else None,
        'prev_question_id': prev_question_id,
        'next_question_id': next_question_id,
    })


@csrf_exempt
@login_required
def quiz_result(request):
    supabase_user_id = getattr(request.user, 'supabase_user_id', None)
    if not supabase_user_id:
        return redirect('login')

    request.session.pop('quiz_questions', None)
    request.session.pop('quiz_folder_id', None)

    response = supabase.table("answers_history") \
        .select("question_id, answered_contents, is_correct") \
        .eq("user_id", str(supabase_user_id)) \
        .order("answered_at", desc=True) \
        .limit(10).execute()

    records = response.data

    question_ids = [r["question_id"] for r in records]
    questions = supabase.table("questions") \
        .select("question_id, content") \
        .in_("question_id", question_ids).execute().data
    question_map = {q["question_id"]: q["content"] for q in questions}

    for r in records:
        r["question_content"] = question_map.get(r["question_id"], "（不明）")

    return render(request, "quiz_result.html", {"records": records})
