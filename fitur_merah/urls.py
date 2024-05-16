from django.urls import path
from fitur_merah.views import *

app_name = 'fitur_merah'

urlpatterns = [
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
]