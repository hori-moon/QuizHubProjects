from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_protect
from ..services.supabase_client import supabase
from supabase import create_client
# ルーム参加
def join_room(request):
    if request.method == 'POST':
        room_name = request.POST.get('room_name')
        room_password = request.POST.get('room_password', '')

        # Supabase からルーム情報を取得
        response = supabase.table("rooms").select("*").eq("room_name", room_name).execute()
        data = response.data

        if not data:
            messages.error(request, "ルームIDが存在しません。")
            return redirect('join_room')

        room = data[0]

        # パスワードが設定されている場合、照合
        if room['room_password'] and room['room_password'] != room_password:
            messages.error(request, "ルームパスワードが間違っています。")
            return redirect('join_room')

        # セッションに保存
        request.session['room_id'] = room['room_id']
        request.session['room_name'] = room_name
        request.session['room_password'] = room_password
        request.session['is_editable'] = room['is_editable']
        request.session['room_master_id'] = room['user_id']

        return redirect('inside_room')

    return render(request, 'join_room.html')

# ルーム退出
def leave_room(request):
    # セッションからルーム関連情報を削除
    request.session.pop('room_name', None)
    request.session.pop('is_editable', None)

    messages.info(request, "ルームを退出しました。")
    return redirect('join_room')

# ルーム内の処理
def inside_room(request):
    room_id = request.session.get('room_id')
    room_name = request.session.get('room_name')
    room_password = request.session.get('room_password')
    room_master_id = request.session.get('room_master_id')
    user_id = getattr(request.user, 'supabase_user_id')

    if not room_id:
        return redirect('join_room')

    # ルームに紐づくフォルダー一覧を取得
    room_folders = supabase.table("room_folders").select("*").eq("room_id", room_id).execute().data
    folder_ids = [rf["folder_id"] for rf in room_folders]

    folders = []
    if folder_ids:
        folders_response = supabase.table("question_folders").select("*").in_("folder_id", folder_ids).execute()
        folders = folders_response.data

    # 自作のフォルダー一覧
    my_folders = supabase.table("question_folders").select("*").eq("user_id", user_id).execute().data

    # ルーム未接続のものだけを抽出
    addable_folders = [f for f in my_folders if f["folder_id"] not in folder_ids]

    return render(request, 'inside_room.html', {
        'room_name': room_name,
        'room_password': room_password,
        'folders': folders,
        'addable_folders': addable_folders,
        'room_master_id': str(room_master_id),
        'joined_user_id': str(user_id),
    })

def get_user_folders(request):
    user_id = getattr(request.user, 'supabase_user_id')
    room_id = request.session.get('room_id')

    if not user_id or not room_id:
        return JsonResponse({'folders': []})

    # 全自作フォルダー取得
    all_folders = supabase.table("question_folders").select("*").eq("user_id", user_id).execute().data
    for folder in all_folders:
        print(f"Folder ID: {folder['folder_id']}")

    # すでにルームに追加済みのfolder_id取得
    room_folder_ids = supabase.table("room_folders").select("folder_id").eq("room_id", room_id).execute().data
    for rf in room_folder_ids:
        print(f"Room Folder ID: {rf['folder_id']}")
    added_folder_ids = {rf["folder_id"] for rf in room_folder_ids}
    print(f"Added Folder IDs: {added_folder_ids}")

    # 未追加のものだけ抽出
    available_folders = [f for f in all_folders if f["folder_id"] not in added_folder_ids]
    print(f"Available Folders: {available_folders}")

    return JsonResponse({'folders': available_folders})

@csrf_protect
def connect_folder_to_room(request):
    if request.method == 'POST':
        folder_id = request.POST.get('folder_id')
        room_id = request.session.get('room_id')
        print(f"Connecting Folder ID: {folder_id} to Room ID: {room_id}")

        if folder_id and room_id:
            supabase.table("room_folders").insert({
                "folder_id": int(folder_id),
                "room_id": int(room_id)
            }).execute()

    return redirect('inside_room')

@csrf_protect
def disconnect_folder_from_room(request):
    if request.method == 'POST':
        folder_id = request.POST.get('folder_id')
        room_id = request.session.get('room_id')

        if folder_id and room_id:
            # folder_id と room_id の一致で削除
            supabase.table("room_folders").delete().match({
                "folder_id": int(folder_id),
                "room_id": int(room_id)
            }).execute()

    return redirect('inside_room')
