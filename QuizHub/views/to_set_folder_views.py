from ..services.supabase_client import supabase
from django.shortcuts import render, redirect
from django.http import Http404
import re

def to_set_folder(request):
    # POSTリクエストかつ「作成ボタン」が押されたときだけフォルダー作成処理を実行
    if request.method == "POST" and "create-folder" in request.POST:
        print("Creating folder...")
        folder_name = request.POST.get("new-folder-name", "").strip()

        # 空欄チェック
        if folder_name:
            uuid_pattern = r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$"
            if request.user.is_authenticated:
                user_id = getattr(request.user, 'supabase_user_id')
                print("user_id:", user_id)
                if not re.match(uuid_pattern, str(user_id)):
                    user_id = "11111111-1111-1111-1111-111111111111"
                else:
                    user_id = str(user_id)
            print("Validated user_id:", user_id)

            print(f"Creating folder with name: {folder_name} for user_id: {user_id}")
            # Supabaseにフォルダー挿入
            supabase.table("question_folders").insert({
                "folder_name": folder_name,
                "user_id": user_id
            }).execute()
            print("Folder created successfully.")

            return redirect("to_set_folder")

    if request.method == "POST" and "insert-question" in request.POST:
        print("Inserting selected questions into folder...")

        folder_id = request.POST.get("selected-folder")
        if not folder_id:
            print("フォルダーが選択されていません。")
            return redirect("to_set_folder")

        question_ids = request.POST.getlist("question-ids")
        if not question_ids:
            print("問題が選択されていません。")
            return redirect("to_set_folder")

        print(f"選択されたフォルダーID: {folder_id}")
        print(f"選択された問題IDリスト: {question_ids}")

        folder_id_int = int(folder_id)

        for q_id in question_ids:
            q_id_int = int(q_id)

            # 対象の質問を取得（folder_id は配列）
            response = supabase.table("questions").select("folder_id").eq("question_id", q_id_int).execute()
            if not response.data:
                continue

            current_folders = response.data[0].get("folder_id") or []

            # 重複していなければ追加
            if folder_id_int not in current_folders:
                current_folders.append(folder_id_int)
                current_folders.sort()  # 昇順ソート

                supabase.table("questions").update({
                    "folder_id": current_folders
                }).eq("question_id", q_id_int).execute()

        print("選択された問題にフォルダーが追加されました。")
        return redirect("to_set_folder")



    # GET時の初期表示
    uuid_pattern = r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$"
    if request.user.is_authenticated:
        user_id = getattr(request.user, 'supabase_user_id')
        print("user_id:", user_id)
        if not re.match(uuid_pattern, str(user_id)):
            user_id = "11111111-1111-1111-1111-111111111111"
        else:
            user_id = str(user_id)

    folder_data = supabase.table("question_folders").select("*").eq("user_id", user_id).order("folder_id", desc=True).execute().data
    questions_data = supabase.table("questions").select("*").eq("user_id", user_id).order("question_id", desc=True).execute().data

    return render(request, 'to_set_folder.html', {
        'folders': folder_data,
        'questions': questions_data,
        'user_id': user_id,
    })

def delete_folder(request):
    print("Deleting folder...")
    if request.method == "POST":
        print("POST request received for folder deletion.")
        folder_id = request.POST.get("folder_id")
        if not folder_id:
            raise Http404("フォルダーIDが提供されていません。")

        print(f"Deleting folder with ID: {folder_id}")
        folder_id_int = int(folder_id)
        folder_id_str = str(folder_id_int)

        # folder_idを含む全質問を取得
        questions = supabase.table("questions") \
            .select("question_id", "folder_id") \
            .contains("folder_id", [folder_id_str]) \
            .execute().data

        # 各質問のfolder_idから該当のIDを除いて更新
        for q in questions:
            original_list = q.get("folder_id", [])
            updated_list = [fid for fid in original_list if fid != folder_id_int]
            supabase.table("questions").update({
                "folder_id": updated_list
            }).eq("question_id", q["question_id"]).execute()

        print(f"Removed folder ID {folder_id} from questions.")

        # フォルダーを削除（CASCADEにより他の依存も削除される）
        supabase.table("question_folders").delete().eq("folder_id", folder_id_int).execute()
        print(f"Deleted folder ID {folder_id} from question_folders.")

        return redirect("to_set_folder")

