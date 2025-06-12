from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.hashers import make_password
from ..services.supabase_client import supabase

def create_account(request):
    if request.method == 'POST':
        name = request.POST.get('user_name')
        password = request.POST.get('user_password')
        

        print(f"[DEBUG] POST: name={name}, password={'*' * len(password)}")

        if not name or not password:
            messages.error(request, '全ての項目を入力してください。')
            return render(request, 'create_account.html')

        # Supabase重複チェック
        try:
            existing_user = supabase.table('users').select('name').eq('name', name).execute()
            print(f"[DEBUG] existing_user: {existing_user}")

            # if existing_user.error is not None:
            #     messages.error(request, f"ユーザー確認中にエラーが発生しました: {existing_user.error.message}")
            #     return render(request, 'create_account.html')

            if existing_user.data and len(existing_user.data) > 0:
                messages.error(request, 'このユーザー名は既に使われています。')
                return render(request, 'create_account.html')

        except Exception as e:
            messages.error(request, f"ユーザー確認中に例外が発生しました: {e}")
            return render(request, 'create_account.html')

        # Supabaseに新規登録（パスワードをハッシュ化）
        hashed_password = make_password(password)
        data = {'name': name, 'password': hashed_password}
        try:
            response = supabase.table('users').insert(data).execute()
            print(f"[DEBUG] insert response: {response}")
        except Exception as e:
            messages.error(request, f"Supabase登録中に例外が発生しました: {e}")
            return render(request, 'create_account.html')

        return redirect('to_text')  # URL名にリダイレクト

    # GETの場合はアカウント作成ページを表示
    return render(request, 'create_account.html')
