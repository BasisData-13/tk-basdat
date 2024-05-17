from django.urls import path
from fitur_hijau.views import *

app_name = 'fitur_hijau'

urlpatterns = [
    # CRUD KELOLA PLAYLIST
    path('crud_kelola_playlist_main/', kelola_user_playlist_main, name='crud_kelola_playlist_main'),
    path('tambah_lagu/<uuid:playlist_id>/', tambah_lagu, name='tambah_lagu'),
    path('tambah_playlist/', tambah_playlist, name='tambah_playlist'),
    path('hapus_playlist/<uuid:playlist_id>/', hapus_playlist, name='hapus_playlist'),
    path('hapus_lagu/<uuid:playlist_id>/<uuid:song_id>/', hapus_lagu, name='hapus_lagu'),
    path('detail_playlist/<uuid:playlist_id>/', detail_playlist, name='detail_playlist'),
    path('ubah_main/<uuid:playlist_id>/', ubah_main, name='ubah_main'),
    path('ubah_playlist/<uuid:playlist_id>/', ubah_playlist, name='ubah_playlist'),

    # R PLAY SONG
    path('play_song_main/<uuid:song_id>/', play_song_main, name='play_song_main'),
    path('play_button/<uuid:song_id>/', play_button, name='play_button'),
    path('tambah_ke_playlist/<uuid:song_id>/', tambah_ke_playlist, name='tambah_ke_playlist'),
    path('action_tambah/<uuid:playlist_id>/<uuid:song_id>/', action_tambah, name='action_tambah'),
    path('r_play_song_tambah_lagu_clear', show_r_play_song_tambah_lagu_clear, name='r_play_song_tambah_lagu_clear'),

    # R PLAY USER PLAYLIST
    path('shuffle_play/<uuid:playlist_id>/', shuffle_play, name='shuffle_play'),
]