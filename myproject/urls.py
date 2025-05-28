from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views  # 引入 Django 預設的登入/登出視圖
from blog import views  # 確保導入你的 blog 應用視圖

urlpatterns = [
    path('admin/', admin.site.urls),  # Django 管理后台
    path('chat/', views.edu_step_view, name='edu_step_view'),  # 教學步驟視圖
    path('ask-chatgpt/', views.chat_view, name='chat_view'),  # ChatGPT 聊天功能
    #path('test-gpt/', views.test_gpt, name='test-gpt'),  # ChatGPT 聊天功能    
    path('', views.login_view, name='home'),  # 根路徑，指向教學步驟
    path('login/',views.login_view, name='login'),  # 登入
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),  # 登出
    path('remove-teaching-session/', views.remove_teaching_session, name='remove_teaching_session'),    
]
