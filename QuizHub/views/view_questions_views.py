from django.urls import reverse
import random
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from ..services.supabase_client import supabase
from datetime import datetime
import pytz
from django.contrib.auth.decorators import login_required

def start_random_quiz(request):
    if request.method == 'POST':
        folder_id = request.POST.get('folder_id')
        num_questions = int(request.POST.get('num_questions', 0))

        # 全問題取得
        all_questions = supabase.table('questions') \
            .select('question_id') \
            .eq('folder_id', folder_id) \
            .execute().data

        all_ids = [q['question_id'] for q in all_questions]
        random_ids = random.sample(all_ids, min(num_questions, len(all_ids)))

        # セッションに保存
        request.session['quiz_questions'] = random_ids
        request.session['quiz_folder_id'] = folder_id

        # 最初の問題へ
        return redirect(f"{reverse('view_questions')}?question_id={random_ids[0]}")
    return redirect('view_folder')


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

    if not question_id:
        # セッションから出題リスト取得
        question_list = request.session.get("quiz_questions")
        folder_id = request.session.get("quiz_folder_id")

        if not question_list or not folder_id:
            return redirect("view_folder", folder_id=folder_id or 0)

        index = int(request.GET.get("index", 0))
        if index >= len(question_list):
            return redirect("quiz_result")

        question_id = question_list[index]
    else:
        # ランダム出題でない場合も folder_id をセッションに保存
        folder_id = request.GET.get("folder_id") or request.session.get("quiz_folder_id")

    # 現在の問題取得
    response = supabase.table('questions') \
        .select('question_id, content, folder_id, answer_id') \
        .eq('question_id', question_id).execute()
    questions = response.data if response.data else []

    if questions:
        question = questions[0]
        folder_id = question['folder_id']
        request.session['quiz_folder_id'] = folder_id  # セッション保存

        answer_ids = [q['answer_id'] for q in questions]

        # フォルダー内のすべての問題を昇順で取得
        if 'quiz_questions' not in request.session:
            all_questions = supabase.table('questions') \
                .select('question_id') \
                .eq('folder_id', folder_id) \
                .order('question_id', desc=False) \
                .execute()
            request.session['quiz_questions'] = [q['question_id'] for q in all_questions.data]

        quiz_list = request.session['quiz_questions']
        index = quiz_list.index(int(question_id))

        # 前・次の index を計算
        if index > 0:
            prev_question_id = quiz_list[index - 1]
        if index < len(quiz_list) - 1:
            next_question_id = quiz_list[index + 1]

        # 解答取得
        answer_response = supabase.table('answers') \
            .select('answer_id, correct, options') \
            .in_('answer_id', answer_ids).execute()
        answers = answer_response.data if answer_response.data else []
        answers_map = {a['answer_id']: a for a in answers}

        # 正誤判定 + 履歴保存
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

                # 解答履歴を保存（ログインユーザー前提）
                supabase.table("answers_history").insert({
                    "user_id": "11111111-1111-1111-1111-111111111111",  # 仮のユーザーID
                    "question_id": question['question_id'],
                    "answered_contents": user_answers,
                    "is_correct": is_correct,
                    "answered_at": datetime.now(pytz.UTC).isoformat(),
                    "folder_id": folder_id,
                }).execute()

                # 最後の問題なら結果画面へ
                if index == len(quiz_list) - 1:
                    del request.session['quiz_questions']
                    del request.session['quiz_folder_id']
                    return redirect('quiz_result')
                else:
                    next_index = index + 1
                    return redirect(f"{request.path}?question_id={quiz_list[next_index]}")

    return render(request, 'view_questions.html', {
        'questions': questions,
        'answers_map': answers_map,
        'folder_id': folder_id,
        'result_message': result_message,
        'answered_question_id': str(answered_question_id) if answered_question_id else None,
        'prev_question_id': prev_question_id,
        'next_question_id': next_question_id,
    })


@login_required
def quiz_result(request):
    user_id = "11111111-1111-1111-1111-111111111111"  # 仮のユーザーID

    # 最新の履歴（今回のクイズ10件）を取得
    response = supabase.table("answers_history") \
        .select("question_id, answered_contents, is_correct") \
        .eq("user_id", user_id) \
        .order("answered_at", desc=True) \
        .limit(10).execute()

    records = response.data

    # 問題内容を取得
    question_ids = [r["question_id"] for r in records]
    questions = supabase.table("questions").select("question_id, content") \
        .in_("question_id", question_ids).execute().data
    question_map = {q["question_id"]: q["content"] for q in questions}

    for r in records:
        r["question_content"] = question_map.get(r["question_id"], "（不明）")

    return render(request, "quiz_result.html", {"records": records})