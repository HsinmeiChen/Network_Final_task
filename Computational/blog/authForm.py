from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ValidationError

class CustomAuthenticationForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': '請輸入用戶名',
        })
        self.fields['password'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': '請輸入密碼',
        })

    def confirm_login_allowed(self, user):
        """
        This function allows additional validation of the user after authentication.
        If login is not allowed, raise a ValidationError.
        """
        if not user.is_active:
            raise ValidationError("此帳號已被停用。", code='inactive')

    def clean(self):
        """
        Override the default clean method to display a custom error message
        for invalid login attempts.
        """
        try:
            return super().clean()
        except ValidationError:
            raise ValidationError("登入失敗", code='invalid_login')


