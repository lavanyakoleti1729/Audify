from django.db import models
from django.contrib.auth.models import User

# def get_default_user():
#     return User.objects.filter(is_superuser=True).first()
class AudioFile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=1)
    audio_path = models.FileField(upload_to='audio/')
    created_date = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.audio_path.name

class Comment(models.Model):
    audio = models.ForeignKey(AudioFile, on_delete=models.CASCADE)
    timestamp = models.FloatField(null=True, blank=True)
    text = models.TextField()
    def __str__(self):
        return f"Comment on {self.audio.audio_path.name} at {self.timestamp}"