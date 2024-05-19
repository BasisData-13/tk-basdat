from django.urls import path
from theme.views import *

app_name = 'theme'

urlpatterns = [
    path('', show_main, name='show_main'),
    path('landing_page/', landing_page, name='landing_page'),
    path('register/', register_main, name='register'),
    path('register_pengguna', register_pengguna, name='register_pengguna'),
    path('register_label', register_label, name='register_label'),
    path('login/', login_user, name='login'),
    path('logout/', logout_user, name='logout'),
    
    path('cr_langganan_paket_main', show_cr_langganan_paket_main, name='cr_langganan_paket_main'),
    path('cr_langganan_paket_pembayaran_paket', show_cr_langganan_paket_pembayaran_paket, name='cr_langganan_paket_pembayaran_paket'),
    path('cr_langganan_paket_riwayat_transaksi', show_cr_langganan_paket_riwayat_transaksi, name='cr_langganan_paket_riwayat_transaksi'),
    path('rd_downloaded_songs_main', show_rd_downloaded_songs_main, name='rd_downloaded_songs_main'),
    path('rd_downloaded_songs_berhasil_hapus', show_rd_downloaded_songs_berhasil_hapus, name='rd_downloaded_songs_berhasil_hapus'),
    path('dashboard', show_dashboard, name='dashboard'),
    path('r_play_podcast', r_play_podcast, name='r_play_podcast'),
    path('play_podcast/<str:podcast_id>/', show_r_play_podcast, name='play_podcast'),
    path('charts/', show_ru_melihat_chart, name='ru_melihat_chart'),
    path('charts/<str:chart_type>/', show_ru_melihat_chart_detail, name='ru_melihat_chart_detail'),
    path('crud_kelola_podcast/', show_crud_kelola_podcast, name='show_crud_kelola_podcast'),
    path('delete_podcast/<uuid:podcast_id>/', delete_podcast, name='delete_podcast'),
    path('create_podcast/', create_podcast, name='create_podcast'),
    path('create_episode/<uuid:podcast_id>/', create_episode, name='create_episode'),
    path('podcast_detail/<uuid:podcast_id>/', show_podcast_detail, name='show_podcast_detail'),
    path('delete_episode/<uuid:episode_id>/', delete_episode, name='delete_episode'),
    path('get_song_chart/<str:song_id>/', get_song_chart, name='show_chart_detail'),
]