from django.db import models
from django.contrib.auth.hashers import make_password


class ChatMessage(models.Model):
    user_message = models.TextField()
    ai_message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"User: {self.user_message} | AI: {self.ai_message}"


class Post(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
    

from django.db import models

class TeachingSession(models.Model):
    user_id = models.CharField(max_length=100)  # 用于存储用户的标识
    user_account_name = models.CharField(max_length=20, default="guest")
    user_account_id = models.CharField(max_length=20)
    current_step = models.IntegerField(default=0)  # 当前步骤
    total_steps = models.IntegerField(default=0)  # 总步骤数
    topic_fail_count = models.IntegerField(default=0)  # 當前失敗次數
    all_fail_count = models.IntegerField(default=0) #總共失敗次數
    guide_key = models.CharField(max_length=30, default="Guide1")  # 當前 Guide 的索引
    question_displayed = models.BooleanField(default=False)  # 是否已显示 Question
    current_state = models.CharField(max_length=50, default="Idle")  # 新增字段
    last_user_situation = models.CharField(max_length=100, default="")  #上一個情境
    origin_user_situation = models.CharField(max_length=100, default="")  #原始情境

    def __str__(self):
        return f"User: {self.user_id}, Current Step: {self.current_step} of {self.total_steps}"
    
class UserAuth(models.Model):
    user_id = models.CharField(max_length=255, unique=True)  # 使用者 ID，設定為唯一
    password = models.CharField(max_length=255)  # 密碼，存儲加密後的值
    created_at = models.DateTimeField(auto_now_add=True)  # 記錄創建時間

    def save(self, *args, **kwargs):
        # 確保密碼存儲為加密格式
        if not self.password.startswith('pbkdf2_'):  # 避免重複加密
            self.password = make_password(self.password)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"UserAuth(user_id={self.user_id})"