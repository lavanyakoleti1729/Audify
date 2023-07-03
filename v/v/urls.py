"""
URL configuration for v project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/dev/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.contrib import admin
from django.urls import path
from converter.views import convert_video
from django.conf.urls.static import static
from converter.views import saved_audios,delete_audio,audio_edit,my_form,delete_comment,save_comment,loginPage,registerPage,logoutUser
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', loginPage, name='login'),
    path('convert/', convert_video, name='convert_video'),
path('saved_audios/', saved_audios, name='saved_audios'),
path('convert/saved_audios/', saved_audios, name='saved_audios'),
    path('delete_audio/<int:audio_id>/', delete_audio, name='delete_audio'),
    # path('download_audio/<int:audio_id>/', views.download_audio, name='download_audio'),
    path('delete_comment/<int:comment_id>/', delete_comment, name='delete_comment'),
     path('audio/edit/<int:audio_id>/', audio_edit, name='audio_edit'),
     path('save_comment/<int:audio_id>/', save_comment, name='save_comment'),
     path('login/', loginPage, name='login'),
    path('signup/',registerPage, name='signup'),
     path('logout/', logoutUser, name='logout'),

]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
