from typing import Any
import datetime

from django import forms
from django.contrib.auth import get_user_model

from .models import Post, Comment

User = get_user_model()


class UserForm(forms.ModelForm):
    
    
    class Meta:
        model = User
        fields = (
            'username',
            'first_name',
            'last_name',
            'email',
        )


class PostForm(forms.ModelForm):
    # У виджетов есть атрибут choices, в который можно загнать варианты на выбор. Хотя сейчас, вроде, все работает, но можно попробовать использовать choices.
    date = forms.DateField(
        label='Дата публикации',
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    time = forms.TimeField(
        label='Время публикации',
        widget=forms.TimeInput(attrs={'type': 'time'})
    )
    # pub_date = forms.DateTimeField(widget=)
    # attrs={'type': 'datetime'}
    
    
    class Meta:
        model = Post
        fields = ('title', 'text', 'category', 'pub_date', 'location', 'image')
        widgets = {
            'pub_date': forms.HiddenInput(),
        }
    
    
    def clean_pub_date(self):
        # print(self.cleaned_data)
        # print(self.data)
        raw_date = self.data['date']
        raw_time = self.data['time']
        # print(datetime.datetime.combine(datetime.date.fromisoformat(rdate), datetime.time.fromisoformat(rtime)))
        return datetime.datetime.combine(datetime.date.fromisoformat(raw_date), datetime.time.fromisoformat(raw_time))


class CommentForm(forms.ModelForm):
    
    
    class Meta:
        model = Comment
        fields = ('text',)