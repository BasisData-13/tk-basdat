import datetime
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages  
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.urls import reverse


@login_required(login_url='/login')
def show_main(request):
    return render(request, "main.html")


def register(request):
    form = UserCreationForm()

    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your account has been successfully created!')
            return redirect('theme:login')
    context = {'form':form}
    return render(request, 'register.html', context)


def login_user(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            response = HttpResponseRedirect(reverse("theme:show_main")) 
            response.set_cookie('last_login', str(datetime.datetime.now()))
            return response
        else:
            messages.info(request, 'Sorry, incorrect username or password. Please try again.')
    context = {}
    return render(request, 'login.html', context)


def logout_user(request):
    logout(request)
    response = HttpResponseRedirect(reverse('theme:login'))
    response.delete_cookie('last_login')
    return response

def show_crud_album_song(request):
    return render(request, "crud_album_song.html")

def show_r_cek_royalti(request):
    return render(request, "r_cek_royalti.html")

def show_rd_kelola_album_song(request):
    return render(request, "rd_kelola_album_song.html")

# CRUD Kelola User Playlist
def show_crud_kelola_playlist_main(request):
    return render(request, "crud_kelola_playlist/main.html")

def show_crud_kelola_playlist_detail(request):
    return render(request, "crud_kelola_playlist/detail.html")

def show_crud_kelola_playlist_tambah_lagu(request):
    return render(request, "crud_kelola_playlist/form_tambah_lagu.html")

def show_crud_kelola_playlist_tambah_playlist(request):
    return render(request, "crud_kelola_playlist/form_tambah_playlist.html")

# R Play Song
def show_r_play_song_main(request):
    return render(request, "r_play_song/main.html")

def show_r_play_song_tambah_playlist(request):
    return render(request, "r_play_song/form_tambah_playlist.html")

def show_r_play_song_download_lagu(request):
    return render(request, 'r_play_song/download_lagu.html')

def show_r_play_song_tambah_lagu_clear(request):
    return render(request, 'r_play_song/tambah_lagu_clear.html')