from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.hashers import check_password
from django.contrib.auth import get_user_model
from ..services.supabase_client import supabase

User = get_user_model()  # 拡張ユーザーモデルを取得

def login_view(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        password = request.POST.get('password')

        try:
            # Supabaseでユーザー取得
            response = supabase.table('users') \
                .select('user_id, name, password') \
                .eq('name', name) \
                .execute()

            print(f"[DEBUG] Supabase response: {response.data}")
            users = response.data

            if not users:
                print("[DEBUG] User not found.")
                messages.error(request, 'ユーザーが見つかりません。')
                return render(request, 'login.html')

            user_data = users[0]
            supabase_user_id = user_data.get('user_id')

            if check_password(password, user_data['password']):
                print("[DEBUG] Password match. Logging in user.")
                
                # Djangoユーザー作成または取得
                django_user, created = User.objects.get_or_create(username=name)

                # Supabase ID を保存（カスタムフィールドがある場合）
                if created or not getattr(django_user, 'supabase_user_id', None):
                    django_user.supabase_user_id = supabase_user_id
                    django_user.save()

                login(request, django_user)
                return redirect('to_text')

            else:
                print("[DEBUG] Password mismatch.")
                messages.error(request, 'パスワードが違います。')
                return render(request, 'login.html')

        except Exception as e:
            print(f"[DEBUG] Exception during login: {e}")
            messages.error(request, f"ログイン中にエラーが発生しました: {e}")
            return render(request, 'login.html')

    print("[DEBUG] GET request received.")
    return render(request, 'login.html')
