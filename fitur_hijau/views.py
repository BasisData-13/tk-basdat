from django.shortcuts import render
from django.db import connection

# CRUD Kelola User Playlist
def kelola_user_playlist_main(request):
    cursor = connection.cursor()
    cursor.execute(
        """
        SET search_path to MARMUT;
        SELECT judul, jumlah_lagu, total_durasi
        FROM USER_PLAYLIST
        """
    )

    user_playlists = cursor.fetchall()
    return render(request, 'crud_kelola_playlist/main.html', {'user_playlists': user_playlists})

def tambah_lagu(request):
    return render(request, 'crud_kelola_playlist/form_tambah_lagu.html')


def show_crud_kelola_playlist_detail(request):
    return render(request, "crud_kelola_playlist/detail.html")

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


# R Play Playlist
def show_r_play_playlist(request):
    return render(request, 'r_play_playlist/main.html')