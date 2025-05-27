from ..services.supabase_client import supabase
from django.shortcuts import render

def view_folder(request, folder_id):
    # フォルダー情報取得（例：問題一覧）
    folder = supabase.table("question_folders").select("*").eq("folder_id", folder_id).execute().data[0]

    questions = supabase.table("questions").select("*").eq("folder_id", folder_id).execute().data

    return render(request, 'view_folder.html', {
        'folder': folder,
        'questions': questions,
    })
