import datetime
import uuid
import random
from django.shortcuts import render, redirect
from django.contrib import messages  
from django.http import HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.db import connection
from fitur_merah.views import get_artist_id
    

# AUTHENTICATION
def login_user(request):
    context = {"error": ""}
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        is_artist = False
        is_songwriter = False
        is_podcaster = False
        is_premium = False

        with connection.cursor() as cursor:
            cursor.execute("SET search_path to MARMUT;")
            # Check AKUN table
            cursor.execute(
                """
                SELECT EXISTS (
                    SELECT 1
                    FROM AKUN
                    WHERE email = %s
                    AND password = %s
                )
                """, [email, password]
            )
            result_akun = cursor.fetchone()

            if result_akun and result_akun[0]:  # If AKUN table query returns true
                # Determine role by checking related tables
                role = None

                # Check if the user is an artist
                cursor.execute(
                    """
                    SELECT EXISTS (
                        SELECT 1
                        FROM artist
                        WHERE email_akun = %s
                    )
                    """, [email]
                )
                if cursor.fetchone()[0]:
                    is_artist = True

                # Check if the user is a songwriter
                cursor.execute(
                    """
                    SELECT EXISTS (
                        SELECT 1
                        FROM songwriter
                        WHERE email_akun = %s
                    )
                    """, [email]
                )
                if cursor.fetchone()[0]:
                    is_songwriter = True

                # Check if the user is a podcaster
                cursor.execute(
                    """
                    SELECT EXISTS (
                        SELECT 1
                        FROM podcaster
                        WHERE email = %s
                    )
                    """, [email]
                )
                if cursor.fetchone()[0]:
                    is_podcaster = True
                
                # Check if account is premium
                cursor.execute(
                    """
                    SELECT EXISTS(
                        SELECT 1
                        FROM premium
                        WHERE email = %s
                    )
                    """, [email]
                )
                if cursor.fetchone()[0]:
                    is_premium = True                

                response = HttpResponseRedirect(reverse("theme:landing_page"))
                response.set_cookie('last_login', str(datetime.datetime.now()))
                response.set_cookie('is_authenticated', 'True')
                response.set_cookie('user_email', email)
                response.set_cookie('user_role', 'pengguna')
                response.set_cookie('is_artist', is_artist)
                response.set_cookie('is_songwriter', is_songwriter)
                response.set_cookie('is_podcaster', is_podcaster)
                response.set_cookie('is_premium', is_premium)
                response.set_cookie('is_label', False)
                return response
            else:
                # Check LABEL table
                cursor.execute(
                    """
                    SELECT EXISTS (
                        SELECT 1
                        FROM LABEL
                        WHERE email = %s
                        AND password = %s
                    )
                    """, [email, password]
                )
                result_label = cursor.fetchone()

                if result_label and result_label[0]:  # If LABEL table query returns true
                    response = HttpResponseRedirect(reverse("theme:landing_page"))
                    response.set_cookie('last_login', str(datetime.datetime.now()))
                    response.set_cookie('is_authenticated', 'True')
                    response.set_cookie('user_email', email)
                    response.set_cookie('user_role', 'label')
                    response.set_cookie('is_artist', False)
                    response.set_cookie('is_songwriter', False)
                    response.set_cookie('is_podcaster', False)
                    response.set_cookie('is_premium', False)
                    response.set_cookie('is_label', True)
                    return response

            messages.info(request, 'Sorry, incorrect email or password. Please try again.')

    return render(request, 'authentication/login.html', context)


# Dashboard
def show_dashboard(request):
    cursor = connection.cursor()
    is_label = request.COOKIES.get('is_label')
    is_artist = request.COOKIES.get('is_artist')
    is_songwriter = request.COOKIES.get('is_songwriter')
    is_podcaster = request.COOKIES.get('is_podcaster')
    email = request.COOKIES.get('user_email')

    if is_label == 'True':
        cursor.execute(
            """
            SET search_path to MARMUT;
            SELECT kontak
            FROM LABEL
            WHERE email = %s
            """, [email]
        )
        kontak = cursor.fetchone()

        cursor.execute(
            """
            SET search_path to MARMUT;
            SELECT AL.judul
            FROM LABEL L
            JOIN ALBUM AL ON AL.id_label = L.id
            WHERE L.email = %s
            """, [email]
        )
        albums = cursor.fetchall()

        cursor.execute(
            """
            SET search_path to MARMUT;
            SELECT nama, email
            FROM LABEL
            WHERE email = %s
            """, [email]
        )
        pengguna = cursor.fetchone()

        print(pengguna)

        context = {
            'is_pengguna': False,
            'is_label': True,
            'is_artist': False,
            'is_songwriter': False,
            'is_podcaster': False,

            'kontak': kontak,
            'albums': albums,
            'pengguna': pengguna
        }
        return render(request, 'dashboard.html', context)
    else:
        cursor.execute(
            """
            SET search_path to MARMUT;
            SELECT nama, email, kota_asal, gender, tempat_lahir, tanggal_lahir
            FROM AKUN
            WHERE email = %s
            """, [email]
        )
        pengguna = cursor.fetchone()

        cursor.execute(
            """
            SELECT EXISTS(
                SELECT 1
                FROM AKUN
                JOIN PREMIUM ON PREMIUM.email = AKUN.email
                WHERE AKUN.email = %s
            )
            """, [email]
        )
        status_langganan = cursor.fetchone()

        roles = []
        if is_songwriter == 'True' or is_artist == 'True':
            songs = []
            
            if is_songwriter == 'True':
                roles.append('Songwriter')
                cursor.execute(
                    """
                    SET search_path to MARMUT;
                    SELECT K.judul
                    FROM SONG
                    JOIN KONTEN K ON SONG.id_konten = K.id
                    JOIN SONGWRITER_WRITE_SONG SWS ON SONG.id_konten = SWS.id_song
                    JOIN SONGWRITER SW ON SWS.id_songwriter = SW.id
                    JOIN AKUN A ON SW.email_akun = A.email
                    WHERE A.email = %s
                    """, [email]
                )
                songs += cursor.fetchall()
            
            if is_artist == 'True':
                roles.append('Artist')
                cursor.execute(
                    """
                    SET search_path to MARMUT;
                    SELECT K.judul
                    FROM ARTIST A
                    JOIN SONG S ON A.id = S.id_artist
                    JOIN KONTEN K ON S.id_konten = K.id
                    WHERE A.email_akun = %s
                    """, [email]
                )
                songs += cursor.fetchall() 
        else:
            songs = None
            
        if is_podcaster == 'True':
            cursor.execute(
                """
                SET search_path to MARMUT;
                SELECT K.judul
                FROM PODCASTER PR
                JOIN PODCAST P ON PR.email = P.email_podcaster
                JOIN KONTEN K ON K.id = P.id_konten
                WHERE PR.email = %s
                """, [email]
            )
            podcast = cursor.fetchall()

            roles.append('Podcaster')
        else:
            podcast = None

        if is_podcaster == 'False' or is_artist == 'False' or is_songwriter == 'False':
            cursor.execute(
                """
                SET search_path to MARMUT;
                SELECT judul
                FROM USER_PLAYLIST
                WHERE email_pembuat = %s
                """, [email]
            )
            playlists = cursor.fetchall()
        else:
            playlists = None

    print(roles)
    context = {
        'is_label': False,
        'is_pengguna': True,
        'is_artist': is_artist,
        'is_songwriter': is_songwriter,
        'is_podcaster': is_podcaster,

        'pengguna': pengguna,
        'status_langganan': status_langganan,
        'songs': songs,
        'podcasts': podcast,
        'playlists': playlists,
        'roles': ', '.join(roles)
    }
    print(context)
    return render(request, 'dashboard.html', context)


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
        roles = request.POST.getlist('roles')
        is_podcaster = 'podcaster' in roles
        is_artist = 'artist' in roles
        is_songwriter = 'songwriter' in roles
        
        
        if is_podcaster or is_artist or is_songwriter:
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
            
            if is_podcaster:
                cursor.execute(
                    """
                    SET search_path to MARMUT;
                    INSERT INTO PODCASTER
                    VALUES (%s)
                    """, (email,)
                )
                
            if is_artist:
                uuid_artist = str(uuid.uuid4())
                uuid_hak_cipta = str(uuid.uuid4())
                rate_royalti = random.randint(1, 11) 
                cursor.execute(
                    """
                    SET search_path to MARMUT;
                    INSERT INTO PEMILIK_HAK_CIPTA
                    VALUES (%s, %s)
                    """, (uuid_hak_cipta, rate_royalti)
                )
                cursor.execute(
                    """
                    SET search_path to MARMUT;
                    INSERT INTO ARTIST
                    VALUES (%s,%s,%s)
                    """, (uuid_artist,email,uuid_hak_cipta)
                )
                
            if is_songwriter:
                uuid_songwriter = str(uuid.uuid4())
                uuid_hak_cipta = str(uuid.uuid4())
                rate_royalti = random.randint(1, 11)
                
                cursor.execute(
                    """
                    SET search_path to MARMUT;
                    INSERT INTO PEMILIK_HAK_CIPTA
                    VALUES (%s, %s)
                    """, (uuid_hak_cipta, rate_royalti)
                )
                
                cursor.execute(
                    """
                    SET search_path to MARMUT;
                    INSERT INTO SONGWRITER
                    VALUES (%s,%s,%s)
                    """, (uuid_songwriter,email,uuid_hak_cipta)
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
        uuid_hak_cipta = str(uuid.uuid4())
        uuid_label = str(uuid.uuid4())
        rate_royalti = random.randint(1, 11)

        cursor = connection.cursor()
        try:
            cursor.execute(
                """
                SET search_path to MARMUT;
                INSERT INTO PEMILIK_HAK_CIPTA
                VALUES (%s, %s)
                """, (uuid_hak_cipta, rate_royalti)
            )
            
            cursor.execute(
                """
                SET search_path to MARMUT;
                INSERT INTO LABEL(id, nama, email, password, kontak, id_pemilik_hak_cipta)
                VALUES (%s, %s, %s, %s, %s, %s)
                """, (uuid_label, nama, email, password, kontak, uuid_hak_cipta)
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

# fitur biru
def show_r_play_podcast(request, podcast_id):
    podcast = get_podcast_details(request, podcast_id)
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
            GROUP BY k.id, a.nama, e.id_konten_podcast, e.judul, e.deskripsi, e.durasi, e.tanggal_rilis
            ORDER BY e.tanggal_rilis;
        """, [podcast_id])
        episodes = cursor.fetchall()
    return render(request, 'r_play_podcast.html', {'podcast': podcast, 'episodes': episodes})

def r_play_podcast(request):
    return render(request, 'r_play_podcast.html')

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
            GROUP BY k.id, a.nama, e.id_konten_podcast, e.judul, e.deskripsi, e.durasi, e.tanggal_rilis
            ORDER BY e.tanggal_rilis;
        """, [podcast_id])
        result = cursor.fetchone()
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
                a.nama AS artist_name,
                k.tanggal_rilis AS release_date,
                s.total_play AS total_plays,
                k.id AS song_id
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
                AKUN a ON ar.email_akun = a.email
            WHERE 
                c.tipe = %s
            ORDER BY 
                s.total_play DESC
            LIMIT 20;
        """, [chart_type])
        songs = cursor.fetchall()
    return render(request, 'ru_melihat_chart/detail.html', {'chart_type': chart_type, 'songs': songs})

def get_song_chart(request, song_id):
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
    song_detail = cursor.fetchone()
    return render(request, 'ru_melihat_chart/song_detail.html', {'song_detail': song_detail})

def show_crud_kelola_podcast(request):
    genres = get_genres()
    podcasts = get_all_podcasts(request)
    context = {'podcasts': podcasts, 'genres' : genres}
    return render(request, "crud_kelola_podcast.html", context)

def get_genres():
    with connection.cursor() as cursor:
        cursor.execute('''
            SET search_path to MARMUT;
            SELECT DISTINCT genre FROM genre 
            INNER JOIN konten ON genre.id_konten = konten.id
            INNER JOIN podcast ON konten.id = podcast.id_konten;
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
    if request.method == 'GET':
        genres = get_genres()
        return render(request, 'create_podcast.html', {'genres': genres})

    elif request.method == 'POST':
        judul = request.POST.get('judul')
        genres = request.POST.getlist('genre')
        email_podcaster = request.COOKIES.get('user_email')
        uuid_podcast = str(uuid.uuid4())

        with connection.cursor() as cursor:
            cursor.execute('''
                SET search_path to MARMUT;
                INSERT INTO konten (id, judul, tanggal_rilis, tahun, durasi) 
                VALUES (%s, %s, CURRENT_DATE, EXTRACT(YEAR FROM CURRENT_DATE), 0)
                RETURNING id;
            ''', [uuid_podcast, judul])
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

        return redirect('theme:show_crud_kelola_podcast')

def delete_podcast(request, podcast_id):
    with connection.cursor() as cursor:
        cursor.execute("""
            SET search_path to MARMUT;
            DELETE FROM EPISODE WHERE id_konten_podcast = %s;
            DELETE FROM GENRE WHERE id_konten = %s;
            DELETE FROM PODCAST WHERE id_konten = %s;
            DELETE FROM KONTEN WHERE id = %s;
        """, [podcast_id, podcast_id, podcast_id, podcast_id])
    return redirect(request.META.get('HTTP_REFERER'))

def show_podcast_detail(request, podcast_id):
    with connection.cursor() as cursor:
        cursor.execute("""
            SET search_path to MARMUT;
            SELECT e.judul AS judul_podcast, e.deskripsi, e.durasi, e.tanggal_rilis, e.id_episode, k.judul
            FROM PODCAST p
            JOIN EPISODE e ON p.id_konten = e.id_konten_podcast
            JOIN KONTEN k ON p.id_konten = k.id
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
        return show_podcast_detail(request, podcast_id)
    return render(request, 'create_episode.html', {'podcast_id': podcast_id})

def delete_episode(request, episode_id):
    with connection.cursor() as cursor:
        cursor.execute("""
            SET search_path to MARMUT;
            DELETE FROM MARMUT.EPISODE WHERE id_episode = %s;
        """, [episode_id])
    return redirect(request.META.get('HTTP_REFERER'))