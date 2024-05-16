from django.urls import path
from fitur_hijau.views import *

app_name = 'fitur_hijau'

urlpatterns = [
    # CRUD KELOLA PLAYLIST
    path('crud_kelola_playlist_main/', kelola_user_playlist_main, name='crud_kelola_playlist_main'),
    path('crud_kelola_playlist_detail/', show_crud_kelola_playlist_detail, name='crud_kelola_playlist_detail'),
    path('crud_kelola_playlist_tambah_lagu', tambah_lagu, name='crud_kelola_playlist_tambah_lagu'),
    path('crud_kelola_playlist_tambah_playlist', tambah_playlist, name='crud_kelola_playlist_tambah_playlist'),

    # R PLAY SONG
    path('r_play_song_main', show_r_play_song_main, name='r_play_song_main'),
    path('r_play_song_tambah_playlist', show_r_play_song_tambah_playlist, name='r_play_song_tambah_playlist'),
    path('r_play_song_download_lagu', show_r_play_song_download_lagu, name='r_play_song_download_lagu'),
    path('r_play_song_tambah_lagu_clear', show_r_play_song_tambah_lagu_clear, name='r_play_song_tambah_lagu_clear'),

    # R PLAY USER PLAYLIST  
    path('r_play_playlist_main', show_r_play_playlist, name='r_play_playlist_main'),
]