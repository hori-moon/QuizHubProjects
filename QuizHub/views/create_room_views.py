from django.shortcuts import render, redirect
from ..services.supabase_client import supabase
from django.contrib import messages

def create_room(request):
    if request.method == 'POST':
        room_name = request.POST.get('room_name')
        room_password = request.POST.get('room_password', '')

        # ログインユーザーのIDを取得
        # user_id = request.user.id if request.user.is_authenticated else None

        # 仮でuser_idに1を入れる（本来はログインユーザーのIDを入れるべき）
        user_id = '11111111-1111-1111-1111-111111111111'  

        # DBに追加
        data = {'room_name': room_name, 'room_password': room_password, 'user_id': user_id}
        try:
            response = supabase.table('rooms').insert(data).execute()
            print(f"[DEBUG] insert response: {response}")
        except Exception as e:
            messages.error(request, f"ルームが既に存在しています ")
            return render(request, 'create_room.html')

        # ルーム参加ページへリダイレクト（情報は持たせない）
        return redirect('join_room')

    return render(request, 'create_room.html')