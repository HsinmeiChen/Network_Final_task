# myapp/decorators.py
from django.shortcuts import redirect
from blog.models import TeachingSession

def custom_login_required(view_func):
    def wrapper(request, *args, **kwargs):
        try:
            if not TeachingSession.objects.filter(user_id=request.session.session_key).exists():
                return redirect('login')  # 假設你的 login view 名稱為 'login'
            return view_func(request, *args, **kwargs)
        except TeachingSession.DoesNotExist:
            return redirect('login')  # 假設你的 login view 名稱為 'login'      
    return wrapper
