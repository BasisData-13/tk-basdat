from django.urls import path
from theme.views import *

app_name = 'theme'

urlpatterns = [
    path('', show_main, name='show_main'),
    path('register/', register, name='register'),
    path('login/', login_user, name='login'),
    path('logout/', logout_user, name='logout'),
    path('crud_album_song/', show_crud_album_song, name='crud_album_song'),
    path('r_cek_royalti/', show_r_cek_royalti, name='r_cek_royalti'),
    path('rd_kelola_album_song/', show_rd_kelola_album_song, name='rd_kelola_album_song'),
    path('crud_kelola_playlist_main/', show_crud_kelola_playlist_main, name='crud_kelola_playlist_main'),
    path('crud_kelola_playlist_detail/', show_crud_kelola_playlist_detail, name='crud_kelola_playlist_detail'),
    path('crud_kelola_playlist_tambah_lagu', show_crud_kelola_playlist_tambah_lagu, name='crud_kelola_playlist_tambah_lagu'),
    path('crud_kelola_playlist_tambah_playlist', show_crud_kelola_playlist_tambah_playlist, name='crud_kelola_playlist_tambah_playlist'),
    path('r_play_song_main', show_r_play_song_main, name='r_play_song_main'),
    path('r_play_song_tambah_playlist', show_r_play_song_tambah_playlist, name='r_play_song_tambah_playlist'),
    path('r_play_song_download_lagu', show_r_play_song_download_lagu, name='r_play_song_download_lagu'),
    path('r_play_song_tambah_lagu_clear', show_r_play_song_tambah_lagu_clear, name='r_play_song_tambah_lagu_clear'),
    path('cr_langganan_paket_main', show_cr_langganan_paket_main, name='cr_langganan_paket_main'),
    path('cr_langganan_paket_pembayaran_paket', show_cr_langganan_paket_pembayaran_paket, name='cr_langganan_paket_pembayaran_paket'),
    path('cr_langganan_paket_riwayat_transaksi', show_cr_langganan_paket_riwayat_transaksi, name='cr_langganan_paket_riwayat_transaksi')
]