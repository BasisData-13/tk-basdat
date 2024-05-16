import datetime
from django.shortcuts import render, redirect
from django.contrib import messages  
from django.http import HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.db import connection
import datetime, uuid

# AUTHENTICATION
def login_user(request):
    context = {"error": ""}
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        with connection.cursor() as cursor:
            cursor.execute(
                f"""
                SET search_path to MARMUT;
                SELECT EXISTS (
                    SELECT 1
                    FROM AKUN
                    WHERE email = '{email}'
                    AND password = '{password}'
                );
                """
            )
            result_akun = cursor.fetchall()

            if not result_akun[0][0]:  # If AKUN table query returns false
                # Check LABEL table
                cursor.execute(
                    f"""
                    SELECT EXISTS (
                        SELECT 1
                        FROM LABEL
                        WHERE email = '{email}'
                        AND password = '{password}'
                    );
                    """
                )
                result_label = cursor.fetchall()

                if result_label[0][0]:  # If LABEL table query returns true
                    response = HttpResponseRedirect(reverse("theme:landing_page"))
                    response.set_cookie('last_login', str(datetime.datetime.now()))
                    response.set_cookie('is_authenticated', 'True')
                    return response
            else:
                response = HttpResponseRedirect(reverse("theme:landing_page"))
                response.set_cookie('last_login', str(datetime.datetime.now()))
                response.set_cookie('is_authenticated', 'True')
                return response

            messages.info(request, 'Sorry, incorrect email or password. Please try again.')

    return render(request, 'authentication/login.html', context)


def register_pengguna(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        nama = request.POST.get('username')
        gender = request.POST.get('gender')
        tempat_lahir = request.POST.get('tempat_lahir')
        tanggal_lahir = request.POST.get('tanggal_lahir')
        kota_asal = request.POST.get('kota_asal')

        # periksa role dan tentukan isVerified
        podcaster = request.POST.get('podcaster')
        artist = request.POST.get('artist')
        songwriter = request.POST.get('songwriter')
        if podcaster or artist or songwriter:
            is_verified = 'True'
        else:
            is_verified = 'False'

        cursor = connection.cursor()
        try:
            cursor.execute(
                """
                SET search_path to MARMUT;
                INSERT INTO AKUN(email, password, nama, gender, tempat_lahir, tanggal_lahir, kota_asal, is_verified)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, (email, password, nama, gender, tempat_lahir, tanggal_lahir, kota_asal, is_verified)
            )

            is_podcaster = 'podcaster' in request.POST
            is_artist = 'artist' in request.POST
            is_songwriter = 'songwriter' in request.POST

            if is_podcaster:
                cursor.execute(
                    """
                    SET search_path to MARMUT;
                    INSERT INTO PODCASTER(email)
                    VALUES (%s)
                    """, (email)
                )
            if is_artist:
                cursor.execute(
                    """
                    SET search_path to MARMUT;
                    INSERT INTO ARTIST(email)
                    VALUES (%s)
                    """, (email)
                )
            if is_songwriter:
                cursor.execute(
                    """
                    SET search_path to MARMUT;
                    INSERT INTO SONGWRITER(email)
                    VALUES (%s)
                    """, (email)
                )

            messages.success(request, 'Your account has been successfully created!')
            return HttpResponseRedirect(reverse('theme:login'))
        except Exception as e:
            print(e)

    return render(request, 'authentication/cru_registrasi/register_pengguna.html')

def register_label(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        nama = request.POST.get('username')
        kontak = request.POST.get('kontak')

        # random generate id
        id = uuid.uuid4()

        cursor = connection.cursor()
        try:
            cursor.execute(
                """
                SET search_path to MARMUT;
                INSERT INTO LABEL(id, nama, email, password, kontak)
                VALUES (%s, %s, %s, %s, %s)
                """, (id, email, password, nama, kontak)
            )
            messages.success(request, 'Your account has been successfully created!')
            return HttpResponseRedirect(reverse('theme:login'))
        except Exception as e:
            print(e)

    return render(request, 'authentication/cru_registrasi/register_label.html')

def logout_user(request):
    response = HttpResponseRedirect(reverse('theme:login'))
    response.delete_cookie('last_login')
    response.set_cookie('is_authenticated', '')
    return response
    
def show_main(request):
    return render(request, "authentication/login.html")

def landing_page(request):
    return render(request, 'main.html')

def register_main(request):
    return render(request, 'authentication/cru_registrasi/main.html')




# FITUR MERAH
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
    return render(request, "rd_kelola_album_song.html")

def show_crud_album_song(request):
    songwriters = get_songwriters(request)
    albums = get_album(request)
    genres = get_daftar_genre_song(request)
    labels = get_labels(request)
    artists = get_artists(request)
    context = {'songwriters': songwriters, 'albums': albums, 
               'genres': genres, 'labels': labels, 'artists': artists}
    return render(request, "crud_album_song.html",context)

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