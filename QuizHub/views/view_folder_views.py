from ..services.supabase_client import supabase
from django.core.paginator import Paginator
from django.shortcuts import render
from django.http import Http404

def view_folder(request, folder_id):
    # フォルダー情報取得
    folder_data = supabase.table("question_folders").select("*").eq("folder_id", folder_id).execute().data
    if not folder_data:
        raise Http404("フォルダーが見つかりません")
    folder = folder_data[0]

    # 問題取得
    questions_data = supabase.table("questions").select("*").filter("folder_id", "cs", f"{{{folder_id}}}").execute().data

    # ページネーション（1ページ10件）
    paginator = Paginator(questions_data, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(request, 'view_folder.html', {
        'folder': folder,
        'questions': page_obj,
        'page_obj': page_obj,
    })
