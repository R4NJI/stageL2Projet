from django import forms
from .models import CustomUser

class CustomUserCreationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    password2 = forms.CharField(label='Confirmez le mot de passe', widget=forms.PasswordInput)
    is_superuser = forms.BooleanField(required=False, label='Superutilisateur')

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password', 'password2', 'is_superuser']

    def clean_password2(self):
        password1 = self.cleaned_data.get('password')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError('Les mots de passe ne correspondent pas.')
        return password2