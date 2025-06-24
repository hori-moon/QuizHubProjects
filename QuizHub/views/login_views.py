from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.contrib.auth.hashers import check_password
from ..services.supabase_client import supabase

def login_view(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        password = request.POST.get('password')

        #メッセージ表示
        try:
            response = supabase.table('users').select('name, password').eq('name', name).execute()
            print(f"[DEBUG] Supabase response: {response.data}")

            users = response.data
            if not users:
                print("[DEBUG] User not found.")
                messages.error(request,'ユーザーが見つかりません。')
                return render(request, 'login.html')

            user_data = users[0]
            if check_password(password, user_data['password']):
                print("[DEBUG] Password match. Logging in user.")
                django_user, _ = User.objects.get_or_create(username=name)
                login(request, django_user)
                return redirect('to_text')
            else:
                print("[DEBUG] Password mismatch.")
                messages.error(request,'パスワードが違います。')
                return render(request, 'login.html')

        except Exception as e:
            print(f"[DEBUG] Exception during login: {e}")
            messages.error(request,f"ログイン中にエラーが発生しました: {e}")
            return render(request, 'login.html')

    # GET の場合
    return render(request, 'login.html')