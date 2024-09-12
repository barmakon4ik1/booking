# myapp/authentication.py
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model


class EmailAuthBackend(ModelBackend):
    """
    Custom authentication backend that allows users to log in using their email and password.
    """
    def authenticate(self, request, username=None, password=None, **kwargs):
        UserModel = get_user_model()
        try:
            # Найти пользователя по email
            user = UserModel.objects.get(email=username)
        except UserModel.DoesNotExist:
            return None
        else:
            # Проверить пароль пользователя
            if user.check_password(password):
                return user
        return None
