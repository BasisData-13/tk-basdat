from django.urls import path
from theme.views import *

app_name = 'theme'

urlpatterns = [
    path('', show_main, name='show_main'),
    path('register/', register_main, name='register'),
    path('register_pengguna', register_pengguna, name='register_pengguna'),
    path('register_label', register_label, name='register_label'),
    path('login/', login_user, name='login'),
    path('logout/', logout_user, name='logout'),
    # Fitur Merah
    path('crud_album_song/', show_crud_album_song, name='crud_album_song'),
    path('r_cek_royalti/', show_r_cek_royalti, name='r_cek_royalti'),
    path('rd_kelola_album_song/', show_rd_kelola_album_song, name='rd_kelola_album_song'),
    path('view/album/<str:album_id>/', view_album_action, name='view_album_action'),
    path('addto/album/<str:album_id>/', addto_album_action, name='addto_album_action'),
    path('delete/album/<str:album_id>/', delete_album_action, name='delete_album_action'),
    path('view/song/<str:song_id>/', get_song_detail, name='get_song_detail'),
    path('delete/song/<str:song_id>/', delete_song_action, name='delete_song_action'),
    path('create_song_action/', create_song_action, name='create_song_action'),
    path('create_album_action/', create_album_action, name='create_album_action'),
    # Fitur Merah
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
    path('cr_langganan_paket_riwayat_transaksi', show_cr_langganan_paket_riwayat_transaksi, name='cr_langganan_paket_riwayat_transaksi'),
    path('r_play_playlist_main', show_r_play_playlist, name='r_play_playlist_main'),
    path('rd_downloaded_songs_main', show_rd_downloaded_songs_main, name='rd_downloaded_songs_main'),
    path('rd_downloaded_songs_berhasil_hapus', show_rd_downloaded_songs_berhasil_hapus, name='rd_downloaded_songs_berhasil_hapus'),
    path('dashboard', show_dashboard, name='dashboard'),
    path('r_play_podcast', show_r_play_podcast, name='r_play_podcast'),
    path('ru_melihat_chart', show_ru_melihat_chart, name='ru_melihat_chart'),
    path('ru_melihat_chart_detail', show_ru_melihat_chart_detail, name='ru_melihat_chart_detail'),
    path('crud_kelola_podcast', show_crud_kelola_podcast, name='crud_kelola_podcast')
]