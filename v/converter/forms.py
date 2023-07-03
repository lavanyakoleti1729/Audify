from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
VIDEO_SOURCES = [
    ('', '....'),
    ('upload', 'Upload Video'),
    ('youtube', 'YouTube Link'),
    ('twitter', 'Twitter Link'),
    ('facebook', 'Facebook Link'),
]

class VideoForm(forms.Form):
    videoFile = forms.FileField(required=False)
    videoUrl = forms.URLField(required=False)
    videoSource = forms.ChoiceField(choices=VIDEO_SOURCES, required=True, initial='')

class CommentForm(forms.Form):
    timestamp = forms.FloatField()
    text = forms.CharField(widget=forms.Textarea)

class CreateUserForm(UserCreationForm):
    class Meta:
        model=User
        fields=['username','email','password1','password2']
class UserUpdateForm(forms.ModelForm):
    """ Form for update user details used for registration """
    class Meta:
        model=User
        fields=['username','first_name','last_name','email']