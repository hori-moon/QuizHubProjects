from django.shortcuts import render, redirect
from ..services.supabase_client import supabase
from django.contrib import messages

def create_room(request):
    if request.method == 'POST':
        room_name = request.POST.get('room_name')
        room_password = request.POST.get('room_password', '')

        # DBに追加
        data = {'room_name': room_name, 'room_password': room_password}
        try:
            response = supabase.table('rooms').insert(data).execute()
            print(f"[DEBUG] insert response: {response}")
        except Exception as e:
            messages.error(request, f"Supabase登録中に例外が発生しました: {e}")
            return render(request, 'create_room.html')

        # ルーム参加ページへリダイレクト（'join_room'はurls.pyのnameに合わせてください）
        return redirect('join_room')

    return render(request, 'create_room.html')