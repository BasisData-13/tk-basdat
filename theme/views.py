import datetime
import uuid
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms
from django.contrib import messages  
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.db import connection

    

@login_required(login_url='/login')
def show_main(request):
    return render(request, "main.html")


def register_pengguna(request):
    form = UserCreationForm()

    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your account has been successfully created!')
            return redirect('theme:login')
    context = {'form':form}
    return render(request, 'cru_registrasi/register_pengguna.html', context)

def register_label(request):
    form = UserCreationForm()

    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your account has been successfully created!')
            return redirect('theme:login')
    context = {'form':form}
    return render(request, 'cru_registrasi/register_label.html', context)

def register_main(request):
    return render(request, 'cru_registrasi/main.html')


def login_user(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            response = HttpResponseRedirect(reverse("theme:show_main")) 
            response.set_cookie('last_login', str(datetime.datetime.now()))
            return response
        else:
            messages.info(request, 'Sorry, incorrect username or password. Please try again.')
    context = {}
    return render(request, 'login.html', context)


def logout_user(request):
    logout(request)
    response = HttpResponseRedirect(reverse('theme:login'))
    response.delete_cookie('last_login')
    return response

def show_crud_album_song(request):
    return render(request, "crud_album_song.html")

def show_r_cek_royalti(request):
    return render(request, "r_cek_royalti.html")

def show_rd_kelola_album_song(request):
    return render(request, "rd_kelola_album_song.html")

# CRUD Kelola User Playlist
def show_crud_kelola_playlist_main(request):
    return render(request, "crud_kelola_playlist/main.html")

def show_crud_kelola_playlist_detail(request):
    return render(request, "crud_kelola_playlist/detail.html")

def show_crud_kelola_playlist_tambah_lagu(request):
    return render(request, "crud_kelola_playlist/form_tambah_lagu.html")

def show_crud_kelola_playlist_tambah_playlist(request):
    return render(request, "crud_kelola_playlist/form_tambah_playlist.html")

# R Play Song
def show_r_play_song_main(request):
    return render(request, "r_play_song/main.html")

def show_r_play_song_tambah_playlist(request):
    return render(request, "r_play_song/form_tambah_playlist.html")

def show_r_play_song_download_lagu(request):
    return render(request, 'r_play_song/download_lagu.html')

def show_r_play_song_tambah_lagu_clear(request):
    return render(request, 'r_play_song/tambah_lagu_clear.html')

# R Play Playlist
def show_r_play_playlist(request):
    return render(request, 'r_play_playlist/main.html')

# CR Langganan 
def show_cr_langganan_paket_main(request):
    return render(request, 'cr_langganan_paket/main.html')

def show_cr_langganan_paket_pembayaran_paket(request):
    return render(request, 'cr_langganan_paket/pembayaran_paket.html')

def show_cr_langganan_paket_riwayat_transaksi(request):
    return render(request, 'cr_langganan_paket/riwayat_transaksi.html')

# RD Downloaded Songs
def show_rd_downloaded_songs_main(request):
    return render(request, 'rd_downloaded_songs/main.html')

def show_rd_downloaded_songs_berhasil_hapus(request):
    return render(request, 'rd_downloaded_songs/berhasil_hapus.html')

# Dashboard
def show_dashboard(request):
    return render(request, 'dashboard.html')

# fitur biru
def show_r_play_podcast(request, podcast_id):
    play_podcast = get_podcast_details(request, podcast_id)
    return render(request, 'r_play_podcast/main.html', {'play_podcast': play_podcast})

def get_podcast_details(request, podcast_id):
    from django.db import connection
    with connection.cursor() as cursor:
        cursor.execute("""
            SET search_path to marmut;
            SELECT 
                k.judul AS podcast_title,
                array_agg(g.genre) AS genres,
                a.nama AS podcaster_name,
                k.durasi AS total_duration,
                k.tanggal_rilis,
                k.tahun,
                e.judul AS episode_title,
                e.deskripsi,
                e.durasi AS episode_duration,
                e.tanggal_rilis AS episode_date
            FROM PODCAST p
            JOIN KONTEN k ON p.id_konten = k.id
            JOIN PODCASTER pd ON p.email_podcaster = pd.email
            JOIN AKUN a ON pd.email = a.email
            LEFT JOIN EPISODE e ON p.id_konten = e.id_konten_podcast
            LEFT JOIN GENRE g ON k.id = g.id_konten
            WHERE p.id_konten = %s
            GROUP BY k.id, a.nama, e.id
            ORDER BY e.tanggal_rilis;
        """, [podcast_id])
        result = cursor.fetchall()
        return result
    
def show_ru_melihat_chart(request):
    with connection.cursor() as cursor:
        cursor.execute("""
                SET search_path to MARMUT;
                SELECT tipe FROM CHART
                """)
        charts = cursor.fetchall()
    return render(request, "ru_melihat_chart/main.html", {'charts': charts})

def show_ru_melihat_chart_detail(request, chart_type):
    with connection.cursor() as cursor:
        cursor.execute("""
            SET search_path to MARMUT;
            SELECT 
                k.judul AS song_title,
                a.name AS artist_name,
                k.tanggal_rilis AS release_date,
                s.total_play AS total_plays
            FROM 
                CHART c
            JOIN 
                PLAYLIST_SONG ps ON c.id_playlist = ps.id_playlist
            JOIN 
                SONG s ON ps.id_song = s.id_konten
            JOIN 
                ARTIST ar ON s.id_artist = ar.id
            JOIN
                KONTEN k ON s.id_konten = k.id
            JOIN 
                AKUN a ON ar.email = a.email
            WHERE 
                c.tipe = %s
            ORDER BY 
                s.total_play DESC
            LIMIT 20;
        """, [chart_type])
        songs = cursor.fetchall()
    return render(request, 'ru_melihat_chart/detail.html', {'chart_type': chart_type, 'songs': songs})

def show_crud_kelola_podcast(request):
    genres = get_genres()
    podcasts = get_all_podcasts(request)
    context = {'podcasts': podcasts, 'genres' : genres}
    return render(request, "crud_kelola_podcast.html", context)

def get_genres():
    with connection.cursor() as cursor:
        cursor.execute('''
            SET search_path to MARMUT;
            SELECT genre FROM genre;
        ''')
        genres = cursor.fetchall()
    return genres

def get_all_podcasts(request):
    with connection.cursor() as cursor:
        cursor.execute("""
            SET search_path to MARMUT;
            SELECT k.id, k.judul, k.durasi AS total_durasi, COUNT(e.id_episode) AS jumlah_episode
            FROM MARMUT.PODCAST p
            JOIN MARMUT.KONTEN k ON p.id_konten = k.id
            LEFT JOIN MARMUT.EPISODE e ON p.id_konten = e.id_konten_podcast
            GROUP BY k.id, k.judul, k.durasi;
        """)
        return cursor.fetchall()

def create_podcast(request):
    if request.method == 'POST':
        judul = request.POST.get('judul')
        genres = request.POST.getlist('genre')
        email_podcaster = request.COOKIES.get('user_email')

        with connection.cursor() as cursor:
            cursor.execute('''
                SET search_path to MARMUT;
                INSERT INTO konten (id, judul, tanggal_dibuat, tahun_dibuat, durasi) 
                VALUES (UUID(), %s, CURRENT_DATE, EXTRACT(YEAR FROM CURRENT_DATE), INTERVAL '0 seconds')
                RETURNING id;
            ''', [judul])
            id_konten = cursor.fetchone()[0]
            
            cursor.execute('''
                INSERT INTO podcast (id_konten, email_podcaster)
                VALUES (%s, %s);
            ''', [id_konten, email_podcaster])

            for genre in genres:
                cursor.execute('''
                    INSERT INTO genre (id_konten, genre)
                    VALUES (%s, %s);
                ''', [id_konten, genre])

        return redirect('show_crud_kelola_podcast')

def delete_podcast(request, podcast_id):
    with connection.cursor() as cursor:
        cursor.execute("""
            SET search_path to MARMUT;
            DELETE FROM MARMUT.PODCAST WHERE id_konten = %s;
            DELETE FROM MARMUT.KONTEN WHERE id = %s;
        """, [podcast_id, podcast_id])
    return redirect('show_crud_kelola_podcast')

def show_podcast_detail(request, podcast_id):
    with connection.cursor() as cursor:
        cursor.execute("""
            SET search_path to MARMUT;
            SELECT k.judul AS judul_podcast, k.durasi AS total_durasi, g.genre, e.judul AS judul_episode, e.deskripsi, e.durasi AS durasi_episode, e.tanggal_rilis
            FROM MARMUT.PODCAST p
            JOIN MARMUT.KONTEN k ON p.id_konten = k.id
            LEFT JOIN MARMUT.EPISODE e ON p.id_konten = e.id_konten_podcast
            LEFT JOIN MARMUT.GENRE g ON k.id = g.id_konten
            WHERE p.id_konten = %s;
        """, [podcast_id])
        podcast_details = cursor.fetchall()
    return render(request, 'podcast_detail.html', {'podcast_details': podcast_details})

def create_episode(request, podcast_id):
    if request.method == 'POST':
        judul = request.POST.get('judul')
        deskripsi = request.POST.get('deskripsi')
        durasi = request.POST.get('durasi')
        tanggal_rilis = request.POST.get('tanggal_rilis')
        with connection.cursor() as cursor:
            cursor.execute("""
                SET search_path to MARMUT;
                INSERT INTO MARMUT.EPISODE (id_episode, id_konten_podcast, judul, deskripsi, durasi, tanggal_rilis)
                VALUES (%s, %s, %s, %s, %s, %s);
            """, [str(uuid.uuid4()), podcast_id, judul, deskripsi, durasi, tanggal_rilis])
        return redirect('show_podcast_detail', podcast_id=podcast_id)
    return render(request, 'create_episode.html', {'podcast_id': podcast_id})

def delete_episode(request, episode_id):
    with connection.cursor() as cursor:
        cursor.execute("""
            SET search_path to MARMUT;
            DELETE FROM MARMUT.EPISODE WHERE id_episode = %s;
        """, [episode_id])
    return redirect('show_podcast_detail', podcast_id=request.GET.get('podcast_id'))