from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django import forms

User = get_user_model()


# Как по мне, UserCreationForm уже отражает смысл модели,
# но я от модели с таким именем наследуюсь.
# Поэтому додумался только такого
class AuthUserCreationForm(UserCreationForm):

    class Meta(UserCreationForm.Meta):
        model = User


class AuthUserUpdateForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email')
