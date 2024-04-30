from django.urls import path
from theme.views import show_main, register, login_user, logout_user, show_r_play_podcast, show_ru_melihat_chart, show_crud_kelola_podcast

app_name = 'theme'

urlpatterns = [
    path('', show_main, name='show_main'),
    path('register/', register, name='register'),
    path('login/', login_user, name='login'),
    path('logout/', logout_user, name='logout'),
    path('r_play_podcast/', show_r_play_podcast, name='r_play_podcast'),
    path('ru_melihat_chart/', show_ru_melihat_chart, name='ru_melihat_chart'),
    path('crud_kelola_podcast/', show_crud_kelola_podcast, name='crud_kelola_podcast'),
]