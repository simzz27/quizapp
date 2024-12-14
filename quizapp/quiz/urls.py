from django.urls import path,include
from . import views

app_name = 'quiz'

from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),  # Home page
    path('start/', views.start_quiz, name='start_quiz'),  # Start quiz
    path('quiz/<int:session_id>/', views.quiz_page, name='quiz_page'),
    path('result/<int:session_id>/', views.quiz_result, name='quiz_result'),
]
