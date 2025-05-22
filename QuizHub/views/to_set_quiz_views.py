import os
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.shortcuts import render
from ..services.supabase_client import supabase

@csrf_exempt
def to_set_quiz(request):
    if request.method == "POST":
        user_id = request.user.id if request.user.is_authenticated else '11111111-1111-1111-1111-111111111111'  # 認証済みユーザー想定
        folder_id = request.POST.get("folder_id")  # 必要に応じて取得
        question = request.POST.get("question")
        answer = request.POST.get("answer")
        choice_type = request.POST.get("choice_type")
        question_num = request.POST.get("question_num")

        if question_num:
            ocr_result = request.POST.get('ocr_result')
            question_num_int = int(question_num)
            return render(request, 'to_set_quiz.html', {'ocr_result': ocr_result, 'question_num': question_num_int, 'question_range': range(1, question_num_int + 1)})

        # 選択肢の取得
        options = []
        if choice_type == "text":
            num_choices = int(request.POST.get("text_num_choices", 0))
            for i in range(num_choices):
                opt = request.POST.get(f"text_choice_{i+1}")
                if opt:
                    options.append(opt)
        elif choice_type == "image":
            num_choices = int(request.POST.get("image_num_choices", 0))
            for i in range(num_choices):
                file = request.FILES.get(f"image_choice_{i+1}")
                if file:
                    # 画像をSupabase Storage等にアップロードし、パスを取得
                    file_path = f"quiz_images/{file.name}"
                    supabase.storage.from_("quiz_images").upload(file_path, file)
                    public_url = supabase.storage.from_("quiz_images").get_public_url(file_path)
                    options.append(public_url)
        else:
            options = []

        # answersテーブルに挿入
        answer_data = {
            "correct": [answer],
            "options": options
        }
        answer_res = supabase.table("answers").insert(answer_data).execute()
        answer_id = answer_res.data[0]["answer_id"]

        # questionsテーブルに挿入
        question_data = {
            "content": question,
            "answer_id": answer_id,
            "user_id": user_id
        }
        supabase.table("questions").insert(question_data).execute()

        return redirect("to_set_quiz")

    return render(request, "to_set_quiz.html")