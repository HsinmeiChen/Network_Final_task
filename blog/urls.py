from django.urls import path
from django.contrib.auth import views as auth_views
from blog import views
from blog.authForm import CustomAuthenticationForm

urlpatterns = [
    path('', views.edu_step_view, name='edu_step_view'),
    path('login/',views.login_view, name='login'),  # 登入,
    path('logout/', views.logout_view, name='logout'),
    path('test-gpt/', views.test_gpt, name='test-gpt'),  # ChatGPT 聊天功能
    path('chat/', views.chat_view, name='chat'),
    path('edu_step/', views.edu_step_view, name='edu_step'),
    path('remove-teaching-session/', views.remove_teaching_session, name='remove_teaching_session'),
]

