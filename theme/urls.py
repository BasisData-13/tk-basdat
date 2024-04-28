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
]