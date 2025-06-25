from ..services.supabase_client import supabase
from django.shortcuts import render, redirect
from django.http import Http404
import re

def to_set_folder(request):
    # POSTリクエストかつ「作成ボタン」が押されたときだけフォルダー作成処理を実行
    if request.method == "POST" and "create_folder" in request.POST:
        print("Creating folder...")
        folder_name = request.POST.get("new-folder-name", "").strip()
        print(f"Received folder name: '{folder_name}'")

        # 空欄チェック
        if folder_name:
            user_id = request.POST.get("user_id", "") or "11111111-1111-1111-1111-111111111111"
            print(f"Received user_id: '{user_id}'")

            # UUID形式チェック
            uuid_pattern = r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$"
            if not re.match(uuid_pattern, user_id):
                user_id = "11111111-1111-1111-1111-111111111111"
            else:
                user_id = str(user_id)
            print(f"Using user_id: {user_id}")

            print(f"Creating folder with name: {folder_name} for user_id: {user_id}")
            # Supabaseにフォルダー挿入
            supabase.table("question_folders").insert({
                "folder_name": folder_name,
                "user_id": user_id
            }).execute()
            print("Folder created successfully.")

            return redirect("to_set_folder")

    print("Invalid folder name or user_id format.")
    # GET時の初期表示
    folder_data = supabase.table("question_folders").select("*").execute().data

    user_id = request.POST.get("user_id", "") or "11111111-1111-1111-1111-111111111111"
    if not re.match(r"^[0-9a-fA-F\-]{36}$", user_id):
        user_id = "11111111-1111-1111-1111-111111111111"
    else:
        user_id = str(user_id)

    questions_data = supabase.table("questions").select("*").eq("user_id", user_id).order("question_id", desc=True).execute().data

    return render(request, 'to_set_folder.html', {
        'folders': folder_data,
        'questions': questions_data,
        'user_id': user_id,
    })
