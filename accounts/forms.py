from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from .models import Profile

class SignupForm(UserCreationForm):
    nickname = forms.CharField()
    picture = forms.ImageField()

    class Meta(UserCreationForm.Meta):
        fields = UserCreationForm.Meta.fields + ('email', ) # NOTE : User 모델의 email field 사용

    # NOTE : clean_<필드명> 메서드를 활용하여 is_valid() 메소드 실행시 nickname 필드에 대한 유효성 검증 실행
    def clean_nickname(self):
        nickname = self.cleaned_data.get('nickname')
        if Profile.objects.filter(nickname=nickname).exists():
            raise forms.ValidationError('이미 존재하는 닉네임입니다.')
        return nickname

    def clean_email(self):
        email = self.cleaned_data.get('email')
        User = get_user_model()
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('이미 사용중인 이메일입니다.')
        return email

    def save(self):
        user = super().save()
        Profile.objects.create(
            user = user,
            nickname = self.cleaned_data['nickname']),
            picture = self.cleaned_data['picture'])
        return user
