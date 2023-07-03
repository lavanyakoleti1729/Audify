import os
import subprocess
import youtube_dl
import yt_dlp as youtube_dl
import pytube
from django.http import HttpResponse
from django.shortcuts import render
from .forms import VideoForm,CommentForm
from .models import AudioFile,Comment
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.utils import timezone
from pytz import timezone as pytz_timezone
from django.shortcuts import render, redirect, get_object_or_404
from django.db import IntegrityError
from django.core.exceptions import ValidationError
import json
from .forms import CreateUserForm
from django.contrib import messages
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
ffmpeg_executable = r'C:\ffmpeg\ffmpeg-2023-06-19-git-1617d1a752-full_build\bin\ffmpeg.exe'
# replace this with your ffmpeg path



def registerPage(request):
    form = CreateUserForm()

    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')

            # Authenticate and login the user
            authenticated_user = authenticate(username=username, password=form.cleaned_data['password1'])
            login(request, authenticated_user)

            messages.success(request, 'Account was created for ' + username)
            return redirect('convert_video')  # Replace 'home' with the desired URL after login

    context = {'form': form}
    return render(request, 'converter/register.html', context)

def loginPage(request):
    if request.method == 'POST':
        username=request.POST.get('username')
        password=request.POST.get('password')
        user=authenticate(request,username=username,password=password)

        if user is not None:
            login(request,user)
            return redirect('convert_video')
        else:
            messages.info(request,'Username or Password is incorrect')
    context={}
    return render(request,'converter/login.html',context)

def logoutUser(request):
    logout(request)
    return redirect('login')
def download_youtube_video(url):
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': 'media/temp_video.%(ext)s',
    }

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(url, download=True)
        video_path = ydl.prepare_filename(info_dict)

    return video_path




def download_twitter_video(url):
    ydl_opts = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'outtmpl': 'media/temp_video.%(ext)s',
    }

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    return 'media/temp_video.mp4'


def download_facebook_video(url):
    ydl_opts = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'outtmpl': 'media/temp_video.%(ext)s',
    }

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    return 'media/temp_video.mp4'

@login_required(login_url='login')
def convert_video(request):
    if request.method == 'POST':
        form = VideoForm(request.POST, request.FILES)
        if form.is_valid():
            video_file = request.FILES.get('videoFile')
            video_url = form.cleaned_data.get('videoUrl')

            if video_file:
                video_path = os.path.join('media', 'temp_video.mp4')
                with open(video_path, 'wb') as destination:
                    for chunk in video_file.chunks():
                        destination.write(chunk)
                video_token = video_file.name.split('.')[0]
                audio_filename = f"audio_{video_token}.mp3"
            elif video_url:
                if 'youtube.com' in video_url:
                    video_path = download_youtube_video(video_url)
                    # Extract the token from the video URL
                    video_token = video_url.split('=')[-1] if '=' in video_url else video_url.split('/')[-1]
                    audio_filename = f"audio_{video_token}.mp3"
                elif 'facebook.com' in video_url:
                    video_path = download_facebook_video(video_url)
                    # Extract the token from the video URL (if applicable)
                    video_token = video_url.split('=')[-1]
                    audio_filename = f"audio_{video_token}.mp3"
                elif 'twitter.com' in video_url:
                    video_path = download_twitter_video(video_url)
                    # Extract the token from the video URL (if applicable)
                    video_token = video_url.split('/')[-1]
                    audio_filename = f"audio_{video_token}.mp3"
                else:
                    return HttpResponse("Invalid video URL")
            else:
                return HttpResponse("No video file or URL provided")

            try:
                audio_path = os.path.join('media', 'audio', audio_filename)
                subprocess.run([ffmpeg_executable, '-i', video_path, audio_path], check=True)

                user = request.user
                audio_file = AudioFile.objects.create(audio_path=audio_path, user=user)


                

                audio_file_name = audio_file.audio_path  # Get the audio file name

                # Add audio name and date created information
                audio_name = audio_file_name
                ist_timezone = pytz_timezone('Asia/Kolkata')
                date_created = timezone.localtime(timezone.now()).date()
                os.remove(video_path)
                

                return render(request, 'converter/success.html', {
                    'audio_file': audio_file,
                    'audio_name': audio_filename,
                    'date_created': date_created
                })
            except subprocess.CalledProcessError as e:
                error_message = str(e)
                return HttpResponse(f"Error converting video to audio: {error_message}")
            except Exception as e:
                error_message = str(e)
                return HttpResponse(f"Error: {error_message}")

    form = VideoForm()
    return render(request, 'converter/convert_video.html', {'form': form})

def audio_detail(request, audio_id):
    audio = Audio.objects.get(id=audio_id)
    comments = Comment.objects.filter(audio=audio)
    form = CommentForm(request.POST or None)
    
    if form.is_valid():
        text = form.cleaned_data['text']
        comment = Comment(audio=audio, text=text)
        if 'timestamp' in form.cleaned_data:
            timestamp = form.cleaned_data['timestamp']
            comment.timestamp = timestamp
        comment.save()
        return redirect('audio_detail', audio_id=audio.id)
    
    context = {
        'audio': audio,
        'comments': comments,
        'form': form
    }
    return render(request, 'converter/home.html', context)
def saved_audios(request):
    # Fetch the saved audios and their comments from the database
    audios = AudioFile.objects.filter(user=request.user).order_by('-created_date')
    ist_timezone = pytz_timezone('Asia/Kolkata')
    created_date = timezone.localtime(timezone.now()).date()
    for audio in audios:
        audio.created_date = created_date

    context = {
        'audios': audios,
    }
    
    return render(request, 'converter/saved_audio.html', context)

# Import the necessary modules and libraries

# Handler for deleting audio
@csrf_exempt
def delete_audio(request, audio_id):
    try:
        audio = AudioFile.objects.get(id=audio_id)
        prefix = '/media/'
        audio1_path=audio.audio_path.url
        # Delete the audio file from the media/audio folder
        trimmed_path = audio1_path[len(prefix):]
        audio_file_path = os.path.join(settings.MEDIA_ROOT, audio1_path)
        
        # audio_file_path =audio1_path


        audio_file_path=trimmed_path
        print(audio_file_path)
        if os.path.exists(audio_file_path):
            os.remove(audio_file_path)

        # Delete the AudioFile object
        audio.delete()

        return JsonResponse({'message': 'Audio deleted successfully'})
    except AudioFile.DoesNotExist:
        return JsonResponse({'message': 'Audio not found'}, status=404)
# from django.shortcuts import render, get_object_or_404

# from django.shortcuts import render, get_object_or_404, redirect
# from .models import AudioFile, Comment

def audio_edit(request, audio_id):
    audio = get_object_or_404(AudioFile, id=audio_id)

    if request.method == 'POST':
        # Process the comment form submission
        comment_text = request.POST.get('comment_text')
        timestamp = request.POST.get('timestamp')
        comment = Comment(audio=audio, text=comment_text, timestamp=timestamp)

        comment.save()
        print(comment.text)
        
        # Redirect to the same page to display the updated comments
        return redirect('audio_edit', audio_id=audio_id)

    comments = Comment.objects.filter(audio=audio).order_by('timestamp')

    audio_url = audio.audio_path.url
    prefix = "\media\audio\audio"
    audio_filename = audio_url[len(prefix):]
    # audio_filename = audio.audio_path.name.split('/')[-1]

    context = {
        'audio': audio,
        'comments': comments,
        'audio_url': audio_url,
        'audio_filename': audio_filename,
    }
    return render(request, 'converter/audio_edit.html', context)



def my_form(request):
    if request.method == "POST" and request.is_ajax():
        form = CommentForm(request.POST)
        if form.is_valid():
            audio_id = request.POST.get('audio_id')
            text = form.cleaned_data['text']
            timestamp = float(request.POST.get('timestamp'))

            # Save the comment in the Comment model
            comment = Comment(audio_id=audio_id, text=text, timestamp=timestamp)
            comment.save()

            return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False, 'errors': form.errors})

    else:
        form = CommentForm()
    
    return render(request, 'converter/audio_edit.html', {'form': form})

@csrf_exempt
def save_comment(request, audio_id):
    if request.method == 'POST':
        payload = json.loads(request.body)
        text = payload.get('text')
        timestamp = payload.get('timestamp')
        
        # Create a new Comment object and save it
        comment = Comment(audio_id=audio_id, text=text, timestamp=timestamp)
        comment.save()
        
        # Return a JSON response indicating success
        return JsonResponse({'message': 'Comment saved successfully.'})

def delete_comment(request, comment_id):
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        # Assuming you have a Comment model
        comment = get_object_or_404(Comment, id=comment_id)

        # Perform any additional checks here if needed (e.g., user authorization)

        comment.delete()

        return JsonResponse({'success': True})
    else:
        return JsonResponse({'success': False}, status=400)
