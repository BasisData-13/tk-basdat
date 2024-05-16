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
    path('r_play_podcast', show_r_play_podcast, name='r_play_podcast'),
    path('ru_melihat_chart', show_ru_melihat_chart, name='ru_melihat_chart'),
    path('ru_melihat_chart_detail', show_ru_melihat_chart_detail, name='ru_melihat_chart_detail'),
    path('crud_kelola_podcast', show_crud_kelola_podcast, name='crud_kelola_podcast')
]