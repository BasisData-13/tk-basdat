from django.shortcuts import redirect, render
from django.db import connection
from django.views.decorators.csrf import csrf_exempt
import uuid, datetime

# CRUD Kelola User Playlist
def kelola_user_playlist_main(request):
    cursor = connection.cursor()
    cursor.execute(
        """
        SET search_path to MARMUT;
        SELECT judul, jumlah_lagu, total_durasi, id_playlist
        FROM USER_PLAYLIST UP
        """
    )

    user_playlists = cursor.fetchall()
    return render(request, 'crud_kelola_playlist/main.html', {'user_playlists': user_playlists})

def tambah_lagu(request, playlist_id):
    cursor = connection.cursor()
    cursor.execute(
        """
        SET search_path to MARMUT;
        SELECT K.judul, A.nama, S.id_konten
        FROM SONG S
        JOIN KONTEN K ON S.id_konten = K.id
        JOIN ARTIST AR ON S.id_artist = AR.id
        JOIN AKUN A ON AR.email_akun = A.email
        """
    )
    songs = cursor.fetchall()
    context = {'songs': songs, 'playlist': playlist_id}

    if request.method == 'POST':
        selected_song_id = request.POST.get('song_select')

        try:
            cursor.execute(
                """
                SET search_path to MARMUT;
                INSERT INTO PLAYLIST_SONG(id_playlist, id_song)
                VALUES (%s, %s)
                """, [playlist_id, selected_song_id]
            )
            return redirect("fitur_hijau:detail_playlist", playlist_id=playlist_id)
        except Exception as e:
            # Handle any errors that occur
            print(f"{e}")
    
    return render(request, 'crud_kelola_playlist/form_tambah_lagu.html', context)

@csrf_exempt
def tambah_playlist(request):
    if request.method == 'POST':
        judul = request.POST.get('judul')
        deskripsi = request.POST.get('deskripsi')
        email_pembuat = request.COOKIES.get('user_email')
        id_user_playlist = uuid.uuid4()
        tanggal_dibuat = datetime.datetime.now()
        id_playlist = uuid.uuid4()

        cursor = connection.cursor()
        cursor.execute( 
            """
            SET search_path to MARMUT;
            INSERT INTO PLAYLIST(id)
            VALUES (%s);

            INSERT INTO USER_PLAYLIST(email_pembuat, id_user_playlist, judul, deskripsi, jumlah_lagu, tanggal_dibuat, id_playlist, total_durasi)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (id_playlist, email_pembuat, id_user_playlist, judul, deskripsi, 0, tanggal_dibuat, id_playlist, 0)
        )
        return redirect("fitur_hijau:crud_kelola_playlist_main")

    return render(request, "crud_kelola_playlist/form_tambah_playlist.html")

@csrf_exempt
def hapus_playlist(request, playlist_id):
    if request.method == 'POST':
        cursor = connection.cursor()
        cursor.execute(
            """
            SET search_path to MARMUT;
            DELETE FROM USER_PLAYLIST WHERE id_playlist = %s;
            DELETE FROM PLAYLIST WHERE id = %s;
            """, [playlist_id, playlist_id]
        )
        return redirect("fitur_hijau:crud_kelola_playlist_main")

    return render(request, "crud_kelola_playlist/kelola_user_playlist.html")

@csrf_exempt
def hapus_lagu(request, playlist_id, song_id):
    cursor = connection.cursor()
    cursor.execute(
        """
        SET search_path to MARMUT;
        DELETE FROM PLAYLIST_SONG 
        WHERE id_playlist = %s
        AND id_song = %s 
        """, [playlist_id, song_id]
    ) 

    return redirect("fitur_hijau:detail_playlist", playlist_id=playlist_id)
    

def detail_playlist(request, playlist_id):
    cursor = connection.cursor()
    cursor.execute("""
        SET search_path to MARMUT;
        SELECT AKUN.nama, UP.judul, UP.deskripsi, UP.jumlah_lagu, UP.total_durasi, UP.tanggal_dibuat, UP.id_playlist
        FROM USER_PLAYLIST UP
        JOIN AKUN ON AKUN.email = UP.email_pembuat
        WHERE id_playlist = %s
    """, [playlist_id])
    playlist = cursor.fetchone()
    
    playlist_details = {
        'nama': playlist[0],
        'judul': playlist[1],
        'deskripsi': playlist[2],
        'jumlah_lagu': playlist[3],
        'total_durasi': playlist[4],
        'tanggal_dibuat': playlist[5],
        'id': playlist[6]
    }

    cursor.execute("""
        SET search_path to MARMUT;
        SELECT konten.judul AS judul, akun.nama AS oleh, konten.durasi AS durasi, konten.id
        FROM USER_PLAYLIST up
        JOIN PLAYLIST_SONG ps ON up.id_playlist = ps.id_playlist
        JOIN SONG s ON ps.id_song = s.id_konten
        JOIN KONTEN konten ON s.id_konten = konten.id
        JOIN ARTIST artis ON s.id_artist = artis.id
        JOIN AKUN akun ON artis.email_akun = akun.email
        WHERE up.id_playlist = %s
    """, [playlist_id])
    songs = cursor.fetchall()

    return render(request, 'crud_kelola_playlist/detail.html', {
        'playlist': playlist_details,
        'songs': songs,
    })

def ubah_main(request, playlist_id):
    context = {'playlist_id': playlist_id}
    return render(request, 'crud_kelola_playlist/ubah_playlist.html', context)

@csrf_exempt
def ubah_playlist(request, playlist_id):
    context = {'playlist_id': playlist_id}
    if request.method == 'POST':
        judul = request.POST.get('judul')
        deskripsi = request.POST.get('deskripsi')

        cursor = connection.cursor()
        cursor.execute(
            """
            SET search_path to MARMUT;
            UPDATE USER_PLAYLIST
            SET judul = %s, deskripsi = %s
            WHERE id_playlist = %s
            """, [judul, deskripsi, playlist_id]
        )
        return redirect('fitur_hijau:crud_kelola_playlist_main')
    
    return render(request, 'crud_kelola_playlist/ubah_playlist.html', context)





# R Play Song
def play_song_main(request, song_id):
    context = get_song_context(song_id)
    return render(request, "r_play_song/main.html", context)

def get_song_context(song_id):
    cursor = connection.cursor()
    cursor.execute(
        """
        SET search_path to MARMUT;

        SELECT
            k.judul,
            g.genre,
            a.nama AS artist,
            ARRAY_AGG(aw.nama) AS songwriters,
            k.durasi,
            k.tanggal_rilis,
            k.tahun,
            s.total_play,
            s.total_download,
            al.judul AS album,
            s.id_konten
        FROM SONG s
            JOIN KONTEN k ON s.id_konten = k.id
            JOIN GENRE g ON s.id_konten = g.id_konten
            JOIN ARTIST ar ON s.id_artist = ar.id
            JOIN AKUN a ON ar.email_akun = a.email
            LEFT JOIN SONGWRITER_WRITE_SONG sws ON s.id_konten = sws.id_song
            LEFT JOIN SONGWRITER sw ON sws.id_songwriter = sw.id
            LEFT JOIN AKUN aw ON sw.email_akun = aw.email
            JOIN ALBUM al ON s.id_album = al.id
        WHERE 
            s.id_konten = %s
        GROUP BY
            k.judul,
            g.genre,
            a.nama,
            k.durasi,
            k.tanggal_rilis,
            k.tahun,
            s.total_play,
            s.total_download,
            al.judul,
            s.id_konten;
        """, [song_id]
    )
    song_data = cursor.fetchone()

    context = {
        'judul': song_data[0],
        'genre': song_data[1],
        'artist': song_data[2],
        'songwriters': song_data[3],
        'durasi': song_data[4],
        'tanggal_rilis': song_data[5],
        'tahun': song_data[6],
        'total_play': song_data[7],
        'total_download': song_data[8],
        'album': song_data[9],
        'id': song_data[10]
    }
    
    return context


@csrf_exempt
def play_button(request, song_id):
    if request.method == 'POST':
        email = request.COOKIES.get('user_email')
        input_range = int(request.POST.get('range_input'))
        waktu = datetime.datetime.now()
        
        cursor = connection.cursor()
        if (input_range > 70): 
            cursor.execute(
                """
                SET search_path to MARMUT;
                INSERT INTO AKUN_PLAY_SONG(email_pemain, id_song, waktu)
                VALUES (%s, %s, %s)
                """, (email, song_id, waktu)
            )

    return play_song_main(request, song_id)

def tambah_ke_playlist(request, song_id):
    songs = get_song_context(song_id)

    cursor = connection.cursor()
    cursor.execute(
        """
        SET search_path to MARMUT;
        SELECT UP.judul, UP.id_playlist
        FROM USER_PLAYLIST UP
        """
    )
    playlists = cursor.fetchall()

    context = {
        'songs': songs,
        'playlists': playlists
    }
    return render(request, 'r_play_song/form_tambah_playlist.html', context)

def action_tambah(request, playlist_id, song_id):

    try:
        cursor = connection.cursor()
        cursor.execute(
            """
            SET search_path to MARMUT;
            INSERT INTO PLAYLIST_SONG(id_playlist, id_song)
            VALUES (%s, %s)
            """, [playlist_id, song_id]
        )
        return render(request, 'r_play_song/tambah_lagu_clear.html', context=get_song_context(song_id))
    except Exception as e:
        print(e)

    songs = get_song_context(song_id)
    cursor.execute(
        """
        SET search_path to MARMUT;
        SELECT UP.judul, UP.id_playlist
        FROM USER_PLAYLIST UP
        """
    )
    playlists = cursor.fetchall()

    context = {
        'songs': songs,
        'playlists': playlists
    }

    return render(request, 'r_play_song/form_tambah_playlist.html', context)

    

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