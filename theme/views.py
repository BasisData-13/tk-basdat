import datetime
import uuid
from django.db import connection
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms
from django.contrib import messages  
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, JsonResponse
from django.urls import reverse
    

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


# Fitur Merah

def get_all_royalti(request):
    cursor = connection.cursor()
    cursor.execute(
        '''
        SET search_path to MARMUT;
        WITH updated_royalties AS (
            UPDATE ROYALTI
            SET jumlah = subquery.total_play * subquery.rate_royalti
            FROM (
                SELECT 
                    r.id_song,
                    s.total_play,
                    p.rate_royalti
                FROM 
                    ROYALTI r
                JOIN 
                    SONG s ON r.id_song = s.id_konten
                JOIN 
                    PEMILIK_HAK_CIPTA p ON r.id_pemilik_hak_cipta = p.id
            ) AS subquery
            WHERE ROYALTI.id_song = subquery.id_song
            RETURNING ROYALTI.id_song, ROYALTI.jumlah
        )
        SELECT 
            k.judul AS judul_lagu,
            a.judul AS judul_album,
            s.total_play,
            s.total_download,
            ur.jumlah AS total_royalti_didapat
        FROM 
            SONG s
        JOIN 
            KONTEN k ON s.id_konten = k.id
        JOIN 
            ALBUM a ON s.id_album = a.id
        JOIN 
            updates_royalties ur ON s.id_konten = ur.id_song
        ORDER BY 
            k.judul;
        '''
    )
    royalties = cursor.fetchall()
    return royalties

def get_album(request):
    cursor = connection.cursor()
    cursor.execute(
        '''
        SET search_path to MARMUT;
        SELECT * FROM album;
        '''
    )
    albums = cursor.fetchall()
    return albums

def get_album_songs(request, album_id):
    cursor = connection.cursor()
    cursor.execute(
        '''
        SET search_path to MARMUT;
        SELECT k.judul, k.durasi, s.total_play, s.total_download, s.id_konten
        FROM song s
        JOIN konten k ON s.id_konten = k.id
        WHERE s.id_album = %s;
        ''', [album_id]
    )
    songs = cursor.fetchall()
    return songs

def delete_album(request, album_id):
    cursor = connection.cursor()
    cursor.execute(
        '''
        SET search_path to MARMUT;
        SELECT * 
        FROM song WHERE id_album = %s;
        ''', [album_id]
    )
    songs = cursor.fetchall()
    for song in songs:
        id_konten = song[0]
        delete_song(request, id_konten)
    
    cursor.execute(
        '''
        SET search_path to MARMUT;
        DELETE FROM album WHERE id = %s;
        ''', [album_id]
    )

def get_album_name(request, album_id):
    cursor = connection.cursor()
    cursor.execute(
        '''
        SET search_path to MARMUT;
        SELECT judul FROM album WHERE id = %s;
        ''', [album_id]
    )
    album_name = cursor.fetchall()
    return album_name[0][0].upper()

def get_song_detail(request, song_id):
    cursor = connection.cursor()
    cursor.execute(
        '''
        SET search_path to MARMUT;
        SELECT 
            k.judul,
            ak.nama, 
            k.durasi, 
            s.total_play, 
            s.total_download 
        FROM 
            song s
        JOIN 
            konten k ON s.id_konten = k.id
        JOIN
            artist ar ON s.id_artist = ar.id
        JOIN 
            pemilik_hak_cipta p ON ar.id_pemilik_hak_cipta = p.id
        JOIN
            akun ak ON ar.email_akun = ak.email
        WHERE 
            k.id = %s;
        ''', [song_id]
    )
    song_detail = cursor.fetchall()
    return JsonResponse({'judul': song_detail[0][0], 'nama': song_detail[0][1], 
            'durasi': song_detail[0][2], 'total_play': song_detail[0][3], 
            'total_download': song_detail[0][4]})

def delete_song(request, song_id):
    cursor = connection.cursor()
    
    cursor.execute(
        '''
        SET search_path to MARMUT;
        DELETE FROM genre WHERE id_konten = %s;
        ''', [song_id]
    )
    
    cursor.execute(
        '''
        SET search_path to MARMUT;
        DELETE FROM songwriter_write_song WHERE id_song = %s;
        ''', [song_id]
    )
    
    cursor.execute(
        '''
        SET search_path to MARMUT;
        DELETE FROM song WHERE id_konten = %s;
        ''', [song_id]
    )
    
    cursor.execute(
        '''
        SET search_path to MARMUT;
        DELETE FROM song WHERE id_konten = %s;
        ''', [song_id]
    )

def view_album_action(request, album_id):
    if request.method == 'GET':
        albums = get_album(request)
        songs = get_album_songs(request, album_id)
        album_name = get_album_name(request, album_id)
        context = {'albums': albums, 'songs': songs, 'album_name': album_name}
        return render(request, "rd_kelola_album_song.html", context)
    
def addto_album_action(request, album_id):
    if request.method == 'GET':
        albums = get_album(request)
        songs = get_album_songs(request, album_id)
        album_name = get_album_name(request, album_id)
        album_id = album_id
        add_song = True
        genres = get_daftar_genre_song(request)
        songwriters = get_songwriters(request)
        artists = get_artists(request)
        context = {'albums': albums, 'songs': songs, 'genres': genres, 'songwriters' : songwriters,
                   'album_name': album_name, 'album_id': album_id, 'add_song': add_song, 'artists': artists}
        return render(request, "crud_album_song.html", context)

def delete_album_action(request, album_id):
    if request.method == 'GET':
        delete_album(request, album_id)
        return redirect('theme:rd_kelola_album_song')
    
def delete_song_action(request, song_id):
    if request.method == 'GET':
        delete_song(request, song_id)
        return redirect(request.META.get('HTTP_REFERER'))
    
def get_artists(request):
    cursor = connection.cursor()
    cursor.execute(
        '''
        SET search_path to MARMUT;
        SELECT
            ar.id, ar.id_pemilik_hak_cipta, ak.nama
        FROM
            artist ar
        JOIN
            akun ak ON ar.email_akun = ak.email;
        '''
    )
    artists = cursor.fetchall()
    return artists

def get_artist_id(request,artist_name):
    cursor = connection.cursor()
    cursor.execute(
        '''
        SET search_path to MARMUT;
        SELECT
            ar.id
        FROM
            artist ar
        JOIN
            akun ak ON ar.email_akun = ak.email
        WHERE
            ak.nama = %s;
        ''', [artist_name]
    )
    artist_id = cursor.fetchone()[0]
    return artist_id


def create_song(request,judul,artist_id,songwriter_id,genre,durasi,album_id):
    print(artist_id, album_id)
    cursor = connection.cursor()
    id_konten = str(uuid.uuid4())
    cursor.execute(
        '''
        SET search_path to MARMUT;
        INSERT INTO konten
        VALUES (%s, %s, CURRENT_DATE, EXTRACT(YEAR FROM CURRENT_DATE), %s)
        RETURNING id;
        ''', [id_konten,judul,durasi]
    )
    
    cursor.execute(
        '''
        SET search_path to MARMUT;
        INSERT INTO song
        VALUES (%s, %s, %s, 0, 0);
        ''', [id_konten,artist_id,album_id]
    )
    
    cursor.execute(
        '''
        SET search_path to MARMUT;
        INSERT INTO songwriter_write_song
        VALUES (%s, %s);
        ''', [songwriter_id,id_konten]
    )
    
    cursor.execute(
        '''
        SET search_path to MARMUT;
        INSERT INTO genre
        VALUES (%s, %s);
        ''', [id_konten,genre]
    )
        
    
def create_album_action(request):
    if request.method == 'POST':
        id_album = str(uuid.uuid4())
        cursor = connection.cursor()
        cursor.execute(
            '''
            SET search_path to MARMUT;
            INSERT INTO album
            VALUES (%s, %s, 1, %s, %s);
            ''', [id_album, request.POST.get('judul_album'), request.POST.get('label'), request.POST.get('durasi')]
        )
        create_song(request,request.POST.get('judul_lagu'),request.POST.get('artist'),request.POST.get('songwriter'),
                    request.POST.get('genre'),request.POST.get('durasi'),id_album)
        return redirect(request.META.get('HTTP_REFERER')) 

def create_song_action(request):
    if request.method == 'POST':
        create_song(request,request.POST.get('judul_lagu'),request.POST.get('artist'),request.POST.get('songwriter'),
                    request.POST.get('genre'),request.POST.get('durasi'),request.POST.get('album'))
        return redirect(request.META.get('HTTP_REFERER')) 

def get_daftar_genre_song(request):
    cursor = connection.cursor()
    cursor.execute(
        '''
        SET search_path to MARMUT;
        SELECT DISTINCT genre FROM genre
        INNER JOIN konten k ON genre.id_konten = k.id
        INNER JOIN song s ON k.id = s.id_konten;
        '''
    )
    genres = cursor.fetchall()
    return genres

def get_songwriters(request):
    cursor = connection.cursor()
    cursor.execute(
        '''
        SET search_path to MARMUT;
        SELECT sw.id,ak.nama
        FROM songwriter sw
        JOIN akun ak ON sw.email_akun = ak.email;
        '''
    )
    songwriters = cursor.fetchall()
    return songwriters

def get_labels(request):
    cursor = connection.cursor()
    cursor.execute(
        '''
        SET search_path to MARMUT;
        SELECT l.id,l.nama
        FROM label l;
        '''
    )
    labels = cursor.fetchall()
    return labels
    
def show_r_cek_royalti(request):
    royalties = get_all_royalti(request)
    return render(request, "r_cek_royalti.html",royalties)

def show_rd_kelola_album_song(request):
    albums = get_album(request)
    context = {'albums': albums}
    return render(request, "rd_kelola_album_song.html",context)

def show_crud_album_song(request):
    songwriters = get_songwriters(request)
    albums = get_album(request)
    genres = get_daftar_genre_song(request)
    labels = get_labels(request)
    artists = get_artists(request)
    context = {'songwriters': songwriters, 'albums': albums, 
               'genres': genres, 'labels': labels, 'artists': artists}
    return render(request, "crud_album_song.html",context)

# Fitur Merah

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
def show_r_play_podcast(request):
    return render(request, "r_play_podcast.html")

def show_ru_melihat_chart(request):
    return render(request, "ru_melihat_chart/main.html")

def show_ru_melihat_chart_detail(request):
    return render(request, 'ru_melihat_chart/detail.html')

def show_crud_kelola_podcast(request):
    return render(request, "crud_kelola_podcast.html")