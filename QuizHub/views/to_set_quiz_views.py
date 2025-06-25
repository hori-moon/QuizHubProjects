import os
from django.shortcuts import render, redirect
from django.conf import settings
from django.views.decorators.http import require_http_methods
from ..services.supabase_client import supabase
import re


@require_http_methods(["GET", "POST"])
def to_set_quiz(request):
    print("to_set_quiz called")
    if request.method == "POST":
        print("POST request received in to_set_quiz")
        # user_idをPOSTから取得し、形式を検証
        user_id = request.POST.get("user_id", "")
        uuid_pattern = r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$"
        if not re.match(uuid_pattern, user_id):
            user_id = "11111111-1111-1111-1111-111111111111"
        else:
            user_id = str(user_id)

        # OCR結果と問題数が送信されてきた場合（問題設定の初期表示）
        question_num = request.POST.get("question_num")
        ocr_result = request.POST.get("ocr_result")
        if question_num:
            question_num_int = int(question_num)
            # 画面にOCR結果・問題数・問題の範囲を渡してフォームを再表示
            return render(request, 'to_set_quiz.html', {
                'ocr_result': ocr_result,
                'question_num': question_num_int,
                'question_range': range(1, question_num_int + 1)
            })

        # 複数問題の処理を開始
        question_count = int(request.POST.get("question-count", 0))
        print("question_count:", question_count)

        # 問題数分ループして一問ずつ処理
        for i in range(1, question_count + 1):
            # 問題文、回答、選択肢タイプを取得
            question_text = request.POST.get(f"question_{i}")
            answer_text = request.POST.get(f"answer_{i}")
            check_answer = request.POST.get(f"is_answer_{i}") == "on"
            choice_type = request.POST.get(f"choice_type_{i}")

            options = []  # 選択肢を格納するリスト

            if choice_type == "text":
                # テキスト選択肢の場合、選択肢数を取得し、それだけPOSTから複数の選択肢を取得
                num_choices = int(request.POST.get(f"text_num_choices_{i}", 0))
                options = request.POST.getlist(f"choices_{i}")  # 同名textareaの複数選択肢をリストで取得

            elif choice_type == "image":
                # 画像選択肢の場合、選択肢数を取得
                num_choices = int(request.POST.get(f"image_num_choices_{i}", 0))
                # ファイルはrequest.FILESで複数アップロードされたものを取得
                for j in range(num_choices):
                    image = request.FILES.getlist(f"image_choices_{i}")[j]  # 同名inputからj番目のファイルを取得
                    if image:
                        # supabaseストレージの 'quiz_images' バケットにアップロード
                        file_path = f"quiz_images/{image.name}"
                        supabase.storage.from_("quiz_images").upload(file_path, image)
                        # 公開URLを取得して選択肢リストに追加
                        public_url = supabase.storage.from_("quiz_images").get_public_url(file_path)
                        options.append(public_url)

            # answer_textは「1,3」のような選択肢番号の文字列か、記述式回答の文字列
            # supabaseのanswersテーブルに挿入するデータ構造を作成
            answer_data = {
                "correct": [answer_text],       # 正答はリストとして格納
                "options": options,             # 選択肢のリスト
                "complete_answer": check_answer # 完全回答かどうか
            }

            print("answer_data:", answer_data)

            # 回答データをanswersテーブルに挿入し、結果を取得
            answer_res = supabase.table("answers").insert(answer_data).execute()
            # 挿入したanswerのIDを取得（以降のquestionsテーブルの外部キーとして使用）
            answer_id = answer_res.data[0]["answer_id"]

            # 問題テーブルに挿入するデータを作成
            question_data = {
                "content": question_text,
                "answer_id": answer_id,
                "user_id": user_id
            }
            # questionsテーブルに問題データを挿入
            supabase.table("questions").insert(question_data).execute()

        # 全問題の挿入が終わったら、一覧表示画面へリダイレクト
        return redirect("to_set_folder")

    # GETリクエスト時は問題登録フォームを表示
    return render(request, "to_set_quiz.html")
