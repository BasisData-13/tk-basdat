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

def tambah_lagu(request):
    return render(request, 'crud_kelola_playlist/form_tambah_lagu.html')

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

def detail_playlist(request, playlist_id):
    cursor = connection.cursor()
    cursor.execute("""
        SET search_path to MARMUT;
        SELECT AKUN.nama, UP.judul, UP.deskripsi, UP.jumlah_lagu, UP.total_durasi, UP.tanggal_dibuat
        FROM USER_PLAYLIST UP
        JOIN AKUN ON AKUN.email = UP.email_pembuat
        WHERE id_playlist = %s
    """, [playlist_id])
    playlist = cursor.fetchone()

    if not playlist:
        return render(request, 'error.html', {'message': 'Playlist not found'})
    
    playlist_details = {
        'nama': playlist[0],
        'judul': playlist[1],
        'deskripsi': playlist[2],
        'jumlah_lagu': playlist[3],
        'total_durasi': playlist[4],
        'tanggal_dibuat': playlist[5],
    }

    cursor.execute("""
        SET search_path to MARMUT;
        SELECT konten.judul AS judul, konten.durasi AS durasi, akun.nama AS oleh
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