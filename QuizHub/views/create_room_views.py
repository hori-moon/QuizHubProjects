from django.shortcuts import render, redirect
from ..services.supabase_client import supabase
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
User = get_user_model()

@login_required
def create_room(request):
    if request.method == 'POST':
        room_name = request.POST.get('room_name')
        room_password = request.POST.get('room_password', None)
       # ログインユーザーのUUID型IDを取得（例: supabase_user_idフィールドがある場合）
        if request.user.is_authenticated:
            user_id = getattr(request.user, 'supabase_user_id', None)
            if user_id is not None:
                user_id = str(user_id)
        else:
            user_id = None
        
        if not user_id:
            messages.error(request, "ユーザー情報が取得できません。再ログインしてください。")
            return render(request, 'create_room.html')

        print(f"[DEBUG] room_name: {room_name}, room_password: {room_password}, user_id: {user_id}")
        # DBに追加
        data = {"room_name": room_name, "room_password": room_password, "user_id": user_id}
        try:
            response = supabase.table('rooms').insert(data).execute()
            print(f"[DEBUG] insert response: {response}")
        except Exception as e:
            messages.error(request, f"Supabase登録中に例外が発生しました: {e}")
            return render(request, 'create_room.html')

        # ルーム参加ページへリダイレクト（情報は持たせない）
        return redirect('join_room')

    return render(request, 'create_room.html')