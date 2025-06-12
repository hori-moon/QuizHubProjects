from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.contrib.auth.hashers import check_password
from ..services.supabase_client import supabase

def login_view(request):
    if request.method == 'POST':
        action = request.POST.get('action')
        name = request.POST.get('name')
        password = request.POST.get('password')

        print(f"[DEBUG] POST received with action={action}, name={name}")

        if action == 'create':
            print("[DEBUG] Create action triggered.")
            return redirect('create_account')  # あれば

        # Supabaseでユーザー取得
        response = supabase.table('users').select('name, password').eq('name', name).execute()
        print(f"[DEBUG] Supabase response: {response.data}")

        users = response.data
        if not users:
            print("[DEBUG] User not found.")
            messages.error(request, 'ユーザーが見つかりません。')
            return render(request, 'login.html')

        user_data = users[0]
        if check_password(password, user_data['password']):
            print("[DEBUG] Password match. Logging in user.")
            django_user, _ = User.objects.get_or_create(username=name)
            login(request, django_user)
            return redirect('to_text')
        else:
            print("[DEBUG] Password mismatch.")
            messages.error(request, 'パスワードが違います。')
            return render(request, 'login.html')

    print("[DEBUG] GET request received.")
    return render(request, 'login.html')
