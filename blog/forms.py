from django import forms
from .models import Comment#, Answer


class EmailPostForm(forms.Form):
    '''форма для отправки статьи по email'''
    # name: этот тип поля будет отображаться как элемент
    # <inputtype="text">
    # Каждый тип имеет виджет для отображения в HTML.
    # Виджет изменяется с помощью параметра witget

    name = forms.CharField(max_length=25)
    email = forms.EmailField()
    to = forms.EmailField()
    # comments: не обязательное поле
    comments = forms.CharField(required=False, widget=forms.Textarea)

class CommentForm(forms.ModelForm):
    '''Form for comments'''
    class Meta:
        ordering = ('-created',)
        model = Comment
        fields = ('name', 'email', 'body')


class SearchForm(forms.Form):
    '''Form for post search'''
    query = forms.CharField()

