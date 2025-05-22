from django.shortcuts import render, redirect
from django.contrib import messages
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
        request.session['room_name'] = room_name
        request.session['is_editable'] = room['is_editable']

        return redirect('inside_room')

    return render(request, 'join_room.html')

def inside_room(request):
    room_name = request.session.get('room_name')
    if not room_name:
        return redirect('join_room')

    return render(request, 'inside_room.html', {'room_name': room_name})

# ルーム退出
from django.contrib import messages  # メッセージ機能を使うためにインポート

def leave_room(request):
    # セッションからルーム関連情報を削除
    request.session.pop('room_name', None)
    request.session.pop('is_editable', None)

    messages.info(request, "ルームを退出しました。")
    return redirect('join_room')
