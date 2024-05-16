from django.urls import path
from fitur_hijau.views import *

app_name = 'fitur_hijau'

urlpatterns = [
    # CRUD KELOLA PLAYLIST
    path('crud_kelola_playlist_main/', kelola_user_playlist_main, name='crud_kelola_playlist_main'),
    path('crud_kelola_playlist_tambah_lagu/', tambah_lagu, name='crud_kelola_playlist_tambah_lagu'),
    path('tambah_playlist', tambah_playlist, name='tambah_playlist'),
    path('hapus_playlist/<uuid:playlist_id>/', hapus_playlist, name='hapus_playlist'),
    path('detail_playlist/<uuid:playlist_id>/', detail_playlist, name='detail_playlist'),
    path('ubah_main/<uuid:playlist_id>/', ubah_main, name='ubah_main'),
    path('ubah_playlist/<uuid:playlist_id>/', ubah_playlist, name='ubah_playlist'),

    # R PLAY SONG
    path('r_play_song_main', show_r_play_song_main, name='r_play_song_main'),
    path('r_play_song_tambah_playlist', show_r_play_song_tambah_playlist, name='r_play_song_tambah_playlist'),
    path('r_play_song_download_lagu', show_r_play_song_download_lagu, name='r_play_song_download_lagu'),
    path('r_play_song_tambah_lagu_clear', show_r_play_song_tambah_lagu_clear, name='r_play_song_tambah_lagu_clear'),

    # R PLAY USER PLAYLIST
    path('r_play_playlist_main', show_r_play_playlist, name='r_play_playlist_main'),
]