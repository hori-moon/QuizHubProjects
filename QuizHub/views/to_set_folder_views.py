from ..services.supabase_client import supabase
from django.shortcuts import render
from django.http import Http404
import re

def to_set_folder(request):
    # フォルダー情報取得
    folder_data = supabase.table("question_folders").select("*").execute().data
    if not folder_data:
        raise Http404("フォルダーが見つかりません")
    # folder = folder_data[0]

    # user_idをPOSTから取得し、形式を検証
    user_id = request.POST.get("user_id", "")
    uuid_pattern = r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$"
    if not re.match(uuid_pattern, user_id):
        user_id = "11111111-1111-1111-1111-111111111111"
    # 問題取得
    questions_data = supabase.table("questions").select("*").eq("user_id", user_id).order("question_id", desc=True).execute().data
    if not questions_data:
        raise Http404("問題が見つかりません")

    return render(request, 'to_set_folder.html', {
        'folders': folder_data,
        'questions': questions_data,
    })
