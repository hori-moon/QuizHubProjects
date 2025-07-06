from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.urls import reverse
from ..services.supabase_client import supabase
from datetime import datetime
import random
import pytz
from django.core.paginator import Paginator

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

        # folder_idをURLに付与してリダイレクト
        return redirect(f"{reverse('view_questions')}?question_id={random_ids[0]}&folder_id={folder_id}")
    return redirect('view_folder')

@csrf_exempt
@login_required
def view_questions(request):
    question_id_raw = request.GET.get('question_id') or request.POST.get('question_id')

    questions = []
    answers_map = {}

    result_message = None
    answered_question_id = None

    question_id_raw = request.GET.get('question_id')
    try:
        current_qid = int(question_id_raw)
    except (TypeError, ValueError):
        current_qid = None

    try:
        last_answered_id = int(request.session.get('answered_question_id'))
    except (TypeError, ValueError):
        last_answered_id = None

    if current_qid != last_answered_id:
        request.session.pop('result_message', None)
        request.session.pop('answered_question_id', None)
    else:
        result_message = request.session.get('result_message', None)
        answered_question_id = last_answered_id

    prev_question_id = None
    next_question_id = None

    # folder_id を GET→セッション の順に取得し、整数変換＆0以下は無効化
    folder_id_str = request.GET.get("folder_id")
    if folder_id_str is None:
        folder_id_str = request.session.get("quiz_folder_id")

    try:
        folder_id_value = int(folder_id_str)
        if folder_id_value <= 0:
            raise ValueError("Invalid folder id")
    except (TypeError, ValueError):
        # 不正な folder_id はリダイレクト
        return redirect('view_folder')  # トップページなど適宜変更可

    # セッションから問題リスト取得
    question_list = request.session.get("quiz_questions")

    # question_id が無い場合は問題リストの最初を使う
    if not question_id_raw:
        if not question_list:
            # 問題リストがなければフォルダー画面へ戻す
            return redirect("view_folder", folder_id=folder_id_value)
        question_id = question_list[0]
    else:
        try:
            question_id = int(question_id_raw)
        except (TypeError, ValueError):
            return redirect("view_folder", folder_id=folder_id_value)

    # DBから該当問題を取得
    response = supabase.table('questions') \
        .select('question_id, content, folder_id, answer_id') \
        .eq('question_id', question_id).execute()
    questions = response.data if response.data else []

    if not questions:
        # 問題が見つからなければフォルダー画面へ
        return redirect("view_folder", folder_id=folder_id_value)

    question = questions[0]

    # フォルダーIDの再保存（セッション維持）
    request.session['quiz_folder_id'] = folder_id_value

    # セッションに問題リストがない場合はフォルダー内問題を全取得してセット
    if not question_list:
        pg_array_str = list_to_pg_array([folder_id_value])
        all_questions_resp = supabase.table('questions') \
            .select('question_id') \
            .filter("folder_id", "cs", pg_array_str) \
            .order('question_id', desc=False) \
            .execute()
        question_list = [q['question_id'] for q in all_questions_resp.data]
        request.session['quiz_questions'] = question_list

    # 現在の問題の前後IDを決定
    if question_id in question_list:
        idx = question_list.index(question_id)
        if idx > 0:
            prev_question_id = question_list[idx - 1]
        if idx < len(question_list) - 1:
            next_question_id = question_list[idx + 1]

    # 解答を取得
    answer_resp = supabase.table('answers') \
        .select('answer_id, correct, options') \
        .eq('answer_id', question['answer_id']) \
        .execute()
    answers = answer_resp.data if answer_resp.data else []

    for a in answers:
        correct_list = a.get('correct')
        if correct_list and len(correct_list) == 1 and ',' in correct_list[0]:
            a['correct'] = [c.strip() for c in correct_list[0].split(',')]

    answers_map = {a['answer_id']: a for a in answers}

    # POST時（解答送信時）の処理
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

            # 回答履歴登録
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

            # セッションに結果をセットしてリダイレクト（PRGパターン）
            request.session['result_message'] = result_message
            request.session['answered_question_id'] = question['question_id']
            return redirect(f"{request.path}?question_id={question['question_id']}&folder_id={folder_id_value}")

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

    selected_folder_id = request.GET.get("folder_id")

    # 全履歴を取得（folder_list 用にも使用）
    full_response = supabase.table("answers_history") \
        .select("question_id, answered_contents, is_correct, answered_at, folder_id") \
        .eq("user_id", str(supabase_user_id)) \
        .order("answered_at", desc=True) \
        .execute()
    full_records = full_response.data

    # フィルタ処理：選択されたフォルダで絞り込む
    if selected_folder_id:
        filtered_records = [r for r in full_records if str(r["folder_id"]) == selected_folder_id]
    else:
        filtered_records = full_records

    # ページネーション
    paginator = Paginator(filtered_records, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    paginated_records = page_obj.object_list

    # 問題文取得
    question_ids = [r["question_id"] for r in paginated_records]
    question_map = {}
    if question_ids:
        questions_response = supabase.table("questions") \
            .select("question_id, content") \
            .in_("question_id", question_ids).execute()
        question_map = {q["question_id"]: q["content"] for q in questions_response.data}

    # 全体の folder_id から map を作成
    all_folder_ids = list({r["folder_id"] for r in full_records})
    folder_map = {}
    if all_folder_ids:
        folders_response = supabase.table("question_folders") \
            .select("folder_id, folder_name") \
            .in_("folder_id", all_folder_ids).execute()
        folder_map = {f["folder_id"]: f["folder_name"] for f in folders_response.data}

    # 各レコードに追加
    for r in paginated_records:
        r["question_content"] = question_map.get(r["question_id"], "（不明）")
        r["folder_name"] = folder_map.get(r["folder_id"], "（不明）")
    
        # 🆕 answered_at を datetime 型に変換
        if isinstance(r["answered_at"], str):
            try:
                # ISO 8601形式を datetime に変換
                r["answered_at"] = datetime.fromisoformat(r["answered_at"])
            except Exception:
                r["answered_at"] = None

    # フォルダセレクトボックス用リスト（絞り込み前の全体から）
    folder_list = [
        {"folder_id": fid, "folder_name": folder_map.get(fid, "（不明）")}
        for fid in all_folder_ids
    ]

    return render(request, "quiz_result.html", {
        "records": paginated_records,
        "page_obj": page_obj,
        "folder_list": folder_list,
        "selected_folder_id": selected_folder_id,
    })
    