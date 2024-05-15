from django.shortcuts import render

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


# R Play Playlist
def show_r_play_playlist(request):
    return render(request, 'r_play_playlist/main.html')