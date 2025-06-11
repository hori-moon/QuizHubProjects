from django.http import HttpResponse
from django.shortcuts import render

def to_text(request):
    return render(request, 'to_text.html')

def view_questions(request):
    return render(request, 'view_questions.html')

def create_room(request):
    return render(request, 'create_room.html')

def create_account(request):
    return render(request, 'create_account.html')

def join_room(request):
    return render(request, 'join_room.html')

def login_view(request):
    return render(request, 'login.html')

def logout_view(request):
    return render(request, 'logout.html')

def to_set_quiz(request):
    if request.method == 'POST':
        ocr_result = request.POST.get('ocr_result')
        question_num = request.POST.get('question_num')
        return render(request, 'to_set_quiz.html', {'ocr_result': ocr_result, 'question_num': question_num})
    return render(request, 'to_text.html')
