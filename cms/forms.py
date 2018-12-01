from django import forms
from django.core.validators import MaxValueValidator, MinValueValidator


class select_manga(forms.Form):

    username = forms.CharField(max_length=100,
                             label='ユーザー名',
                             widget=forms.TextInput(attrs={'placeholder': 'ユーザー名'}))

    manga1 = forms.CharField(max_length=100,
                             label='漫画１',
                             widget=forms.TextInput(attrs={'placeholder': 'シリーズ名'}))
    evaluat1=forms.IntegerField(validators=[MinValueValidator(1),MaxValueValidator(5)],
                                label='漫画評価１',
                                widget=forms.TextInput(attrs={'placeholder': '1~5'}))

    manga2 = forms.CharField(max_length=100,
                             label='漫画２',
                             widget=forms.TextInput(attrs={'placeholder': 'シリーズ名'}))
    evaluat2=forms.IntegerField(validators=[MinValueValidator(1),MaxValueValidator(5)],
                                label='漫画評価２',
                                widget=forms.TextInput(attrs={'placeholder': '1~5'}))

    manga3 = forms.CharField(max_length=100,
                             label='漫画３',
                             widget=forms.TextInput(attrs={'placeholder': 'シリーズ名'}))
    evaluat3=forms.IntegerField(validators=[MinValueValidator(1),MaxValueValidator(5)],
                                label='漫画評価３',
                                widget=forms.TextInput(attrs={'placeholder': '1~5'}))

    manga4 = forms.CharField(max_length=100,
                             label='漫画４',
                             widget=forms.TextInput(attrs={'placeholder': 'シリーズ名'}))
    evaluat4=forms.IntegerField(validators=[MinValueValidator(1),MaxValueValidator(5)],
                                label='漫画評価４',
                                widget=forms.TextInput(attrs={'placeholder': '1~5'}))

    manga5 = forms.CharField(max_length=100,
                             label='漫画５',
                             widget=forms.TextInput(attrs={'placeholder': 'シリーズ名'}))
    evaluat5=forms.IntegerField(validators=[MinValueValidator(1),MaxValueValidator(5)],
                                label='漫画評価５',
                                widget=forms.TextInput(attrs={'placeholder': '1~5'}))

    #clean_~は入力規則を設定し自動で実行できるらしいが、反応なし。。

    def clean_evaluat(self):
        evaluat = self.cleaned_data['evaluat1']

        print(evaluat)
        if evaluat < 1 or evaluat > 5:
            raise forms.ValidationError('範囲外です。')

        return evaluat
