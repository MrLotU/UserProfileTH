from django.forms import ModelForm, DateField, EmailField, ValidationError, Form, PasswordInput, CharField
from django.core.validators import EmailValidator
from .models import UserProfile
from django.contrib.auth import forms, password_validation
from django.contrib.auth.models import User
from UserProfileTH.settings import DATE_INPUT_FORMATS
import re

class UserProfileForm(ModelForm):
    birthday = DateField(input_formats=DATE_INPUT_FORMATS)
    class Meta:
        model = UserProfile
        fields = ['first', 'last', 'birthday', 'bio', 'pfp']
    
    def clean_bio(self):
        bio = self.cleaned_data['bio']
        if not len(bio) > 10:
            raise ValidationError('Bio must be 10 characters or more')
        return bio


class UserForm(ModelForm):
    email = EmailField()
    confirm_email = EmailField(label='Confirm email', validators=[EmailValidator()], required=False)
    class Meta:
        model = User
        fields = ['email']

    def clean(self):
        cleaned_data = super(UserForm, self).clean()
        email = cleaned_data['email']
        if email == self.instance.email:
            return
        try:
            confirmed_email = cleaned_data['confirm_email']
        except KeyError:
            raise ValidationError(
                'Emails don\'t match!'
            )
        if not email.lower() == confirmed_email.lower():
            raise ValidationError(
                'Emails don\'t match!'
            )


class PasswordForm(Form):
    old_password = CharField(widget=PasswordInput, label='Current password')
    new_password1 = CharField(widget=PasswordInput, label='New password')
    new_password2 = CharField(widget=PasswordInput, label='Confirm new password')
    
    def __init__(self, user, *args, **kwargs):
        self.user = user # type: User
        super(PasswordForm, self).__init__(*args, **kwargs)
        
    def clean(self):
        current = self.cleaned_data['old_password']
        password1 = self.cleaned_data['new_password1']
        password2 = self.cleaned_data['new_password2']

        if not self.user.check_password(current):
            raise ValidationError('Wrong current password provided')

        mismatch = password1 != password2
        no_change = current == password1
        too_short = not len(password1) >= 14
        no_case = password1 == password1.upper() or password1 == password1.lower()
        contains_numbers = not re.search(r'\d', password1)
        contains_special_char = not re.search(r'\W', password1)
        new_contains_old =  self.user.userprofile.first.lower() in password1.lower() \
                            or self.user.userprofile.last.lower() in password1.lower() \
                            or self.user.username.lower() in password1.lower()

        if mismatch or no_change or too_short or no_case or \
        contains_numbers or contains_special_char or new_contains_old:
            raise ValidationError('Password must:\n '
                                        'be 14 or more symbols long\n'
                                        'include upper and lowercase letters\n'
                                        'include special characters\n'
                                        'include one or more digits\n'
                                        'NOT be same as current password.')

