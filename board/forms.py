from django import forms
from .models import Post, UserResponse


class AddPostForm(forms.ModelForm):
    class Meta:
        model = Post
        widgets = {'title': forms.TextInput(attrs={'size': '100'})}
        fields = ['category', 'title', 'text', 'upload']

    def __init__(self, *args, **kwargs):
        super(AddPostForm, self).__init__(*args, **kwargs)
        self.fields['category'].label = "Категория:"
        self.fields['title'].label = "Заголовок"
        self.fields['text'].label = "Текст объявления:"
        self.fields['upload'].label = "Фото:"


class RespondForm(forms.ModelForm):
    class Meta:
        model = UserResponse
        fields = ['text_response']

    def __init__(self, *args, **kwargs):
        super(RespondForm, self).__init__(*args, **kwargs)
        self.fields['text_response'].label = "Текст отклика:"


class ResponsesFilterForm(forms.Form):

    def __init__(self, user, *args, **kwargs):
        super(ResponsesFilterForm, self).__init__(*args, **kwargs)
        self.fields['title'] = forms.ModelChoiceField(
            label='Объявление',
            queryset=Post.objects.filter(author_id=user.id).order_by('-time_create').values_list('title', flat=True),
            empty_label="Все",
            required=False
        )



