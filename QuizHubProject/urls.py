"""
URL configuration for QuizHubProject project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from QuizHub import views

urlpatterns = [
    path('', views.login_view, name='login'),
    path('login/', views.login_view, name='login'),
    path('create_account/', views.create_account, name='create_account'),
    path('to_text/', views.to_text, name='to_text'),
    path("ocr/", views.ocr_image, name="ocr_image"),
    path('to_set_quiz/', views.to_set_quiz, name='to_set_quiz'),
    path('to_set_folder/', views.to_set_folder, name='to_set_folder'),
    path('delete_folder/', views.delete_folder, name='delete_folder'),
    path('create_room/', views.create_room, name='create_room'),
    path('join_room/', views.join_room, name='join_room'),
    path('inside_room/', views.inside_room, name='inside_room'),
    path('view_questions/', views.view_questions, name='view_questions'),
    path('get_user_folders/', views.get_user_folders, name='get_user_folders'),
    path('connect_folder_to_room/', views.connect_folder_to_room, name='connect_folder_to_room'),
    path('disconnect_folder_from_room/', views.disconnect_folder_from_room, name='disconnect_folder_from_room'),
    path('view_folder/<int:folder_id>/', views.view_folder, name='view_folder'),
    path('start_random_quiz/', views.start_random_quiz, name='start_random_quiz'),
    path('quiz_result/', views.quiz_result, name='quiz_result'),
    path('leave_room/', views.leave_room, name='leave_room'),
    path('logout/', views.logout_view, name='logout'),
]
