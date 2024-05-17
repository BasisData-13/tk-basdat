import uuid
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.db import connection

# Create your views here.
def get_all_royalti(request):
    cursor = connection.cursor()
    role = request.COOKIES.get('user_role')
    email = request.COOKIES.get('user_email')
    kumpulan_id = []
    royalties = []
    id_pemilik_hak_cipta = None
    
    if role != 'label':
        if request.COOKIES.get('is_songwriter') == 'True':
            id_pemilik_hak_cipta = get_id_hak_cipta(request,get_songwriter_id(request,email),"songwriter")
            kumpulan_id.append(id_pemilik_hak_cipta)
        if request.COOKIES.get('is_artist') == 'True':
            id_pemilik_hak_cipta = get_id_hak_cipta(request,get_artist_id(request,email),"artist")
            kumpulan_id.append(id_pemilik_hak_cipta)
            
        print(kumpulan_id)
            
        for id in kumpulan_id:
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
                SELECT DISTINCT
                    k.judul AS judul_lagu,
                    a.judul AS judul_album,
                    s.total_play,
                    s.total_download,
                    ur.jumlah AS total_royalti_didapat,
                    r.id_pemilik_hak_cipta
                FROM 
                    SONG s
                JOIN 
                    KONTEN k ON s.id_konten = k.id
                JOIN 
                    ALBUM a ON s.id_album = a.id
                JOIN 
                    ROYALTI ur ON s.id_konten = ur.id_song
                JOIN
                    SONGWRITER_WRITE_SONG sw ON s.id_konten = sw.id_song
                JOIN
                    ROYALTI r ON k.id = r.id_song
                WHERE 
                    r.id_pemilik_hak_cipta = %s
                ORDER BY 
                    k.judul;
                ''', [id]
            )
            royalties += cursor.fetchall()
            print(royalties)
        return list(set(royalties))
            
    elif role == 'label':
        cursor.execute(
            '''
            SET search_path to MARMUT;
            SELECT id FROM label WHERE nama = %s;
            ''', [email]
        )
        try:
            id_pemilik_hak_cipta = cursor.fetchone()[0]
        except TypeError:
            id_pemilik_hak_cipta = None
        
    
def get_album(request):
    cursor = connection.cursor()
    role = request.COOKIES.get('user_role')
    email = request.COOKIES.get('user_email')
    albums = []
    
    if role == 'label':
        id_label = get_label_id(request,email)
        cursor.execute(
            '''
            SET search_path to MARMUT;
            SELECT * FROM album
            WHERE id_label = %s;
            ''', [id_label]
        )
        try:
            albums += cursor.fetchall()
        except TypeError:
            albums += []
    else:
        if request.COOKIES.get('is_artist') == 'True':
            id_artist = get_artist_id(request,email)
            cursor.execute(
                '''
                SET search_path to MARMUT;
                SELECT DISTINCT a.id, a.judul, a.jumlah_lagu, a.id_label, a.total_durasi
                FROM album a
                JOIN
                    SONG s ON a.id = s.id_album
                WHERE s.id_artist = %s;
                ''', [id_artist]
            )
            try:
                albums += cursor.fetchall()
            except TypeError:
                albums += []
        if request.COOKIES.get('is_songwriter') == 'True':
            id_songwriter = get_songwriter_id(request,email)
            cursor.execute(
                '''
                SET search_path to MARMUT;
                SELECT DISTINCT a.id, a.judul, a.jumlah_lagu, a.id_label, a.total_durasi
                FROM album a
                JOIN
                    SONG s ON a.id = s.id_album
                JOIN
                    songwriter_write_song sw ON s.id_konten = sw.id_song
                WHERE sw.id_songwriter = %s;
                ''', [id_songwriter]
            )
            try:
                albums += cursor.fetchall()
            except TypeError:
                albums += []
            
    return list(set(albums))

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
        DELETE FROM royalti WHERE id_song = %s;
        ''', [song_id]
    )
    
    cursor.execute(
        '''
        SET search_path to MARMUT;
        DELETE FROM akun_play_song WHERE id_song = %s;
        ''', [song_id]
    )
    
    cursor.execute(
        '''
        SET search_path to MARMUT;
        DELETE FROM playlist_song WHERE id_song = %s;
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
        if request.COOKIES.get('user_role') == 'label':
            albums = get_album(request)
            songs = get_album_songs(request, album_id)
            album_name = get_album_name(request, album_id)
            context = {'albums': albums, 'songs': songs, 'album_name': album_name}
            return render(request, "rd_kelola_album_song.html", context)
        
        elif request.COOKIES.get('is_artist') == 'True' or request.COOKIES.get('is_songwriter') == 'True':
            albums = get_album(request)
            songs = get_album_songs(request, album_id)
            album_name = get_album_name(request, album_id)
            album_id = album_id
            add_song = False
            is_artist = False
            is_songwriter = False
            
            if request.COOKIES.get('is_artist') == 'True':
                is_artist = True
                artist_id = get_artist_id(request, request.COOKIES.get('user_email'))
            if request.COOKIES.get('is_songwriter') == 'True':
                is_songwriter = True
                songwriter_id = get_songwriter_id(request, request.COOKIES.get('user_email'))
            
            genres = get_daftar_genre_song(request)
            songwriters = get_songwriters(request)
            artists = get_artists(request)
            
            context = {'albums': albums, 'songs': songs, 'genres': genres, 'songwriters' : songwriters, 'is_artist': is_artist, 'artist_id': artist_id,
                        'is_songwriter': is_songwriter, 'songwriter_id': songwriter_id, 'album_name': album_name, 'album_id': album_id, 
                        'add_song': add_song, 'artists': artists}
            return render(request, "crud_album_song.html", context)
        
def addto_album_action(request, album_id):
    if request.method == 'GET':
        albums = get_album(request)
        songs = get_album_songs(request, album_id)
        album_name = get_album_name(request, album_id)
        album_id = album_id
        add_song = True
        is_artist = False
        is_songwriter = False
        
        if request.COOKIES.get('is_artist') == 'True':
            is_artist = True
            artist_id = get_artist_id(request, request.COOKIES.get('user_email'))
        if request.COOKIES.get('is_songwriter') == 'True':
            is_songwriter = True
            songwriter_id = get_songwriter_id(request, request.COOKIES.get('user_email'))
        
        genres = get_daftar_genre_song(request)
        songwriters = get_songwriters(request)
        artists = get_artists(request)
        
        context = {'albums': albums, 'songs': songs, 'genres': genres, 'songwriters' : songwriters, 'is_artist': is_artist, 'artist_id': artist_id,
                    'is_songwriter': is_songwriter, 'songwriter_id': songwriter_id, 'album_name': album_name, 'album_id': album_id, 
                    'add_song': add_song, 'artists': artists}
        return render(request, "crud_album_song.html", context)

def delete_album_action(request, album_id):
    if request.method == 'GET':
        delete_album(request, album_id)
        role = request.COOKIES.get('user_role')
        if request.COOKIES.get('is_artist') == 'True' or request.COOKIES.get('is_songwriter') == 'True':
            return redirect('fitur_merah:crud_album_song')
        elif(role == 'label'):
            return redirect('fitur_merah:rd_kelola_album_song')
            
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

def get_artist_id(request,artist_email):
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
            ak.email = %s;
        ''', [artist_email]
    )
    try:
        artist_id = cursor.fetchone()[0]
        return artist_id
    except TypeError:
        return None

def get_songwriter_id(request,songwriter_email):
    cursor = connection.cursor()
    cursor.execute(
        '''
        SET search_path to MARMUT;
        SELECT
            sw.id
        FROM
            songwriter sw
        WHERE
            sw.email_akun = %s;
        ''', [songwriter_email]
    )
    try:
        songwriter_id = cursor.fetchone()[0]
        return songwriter_id
    except TypeError:
        return None


def create_song(request,judul,artist_id,songwriters_id,genres,durasi,album_id):
    print(songwriters_id, genres)
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
    
    for songwriter_id in songwriters_id:
        cursor.execute(
            '''
            SET search_path to MARMUT;
            INSERT INTO songwriter_write_song
            VALUES (%s, %s);
            ''', [songwriter_id,id_konten]
        )
    
    for genre in genres:
        cursor.execute(
            '''
            SET search_path to MARMUT;
            INSERT INTO genre
            VALUES (%s, %s);
            ''', [id_konten,genre]
        )
    
    artist_id_hak_cipta = get_id_hak_cipta(request,artist_id,"artist")
    cursor.execute(
        '''
        SET search_path to MARMUT;
        INSERT INTO royalti
        VALUES (%s, %s, 0);
        ''', [artist_id_hak_cipta,id_konten]
    )
    
    for songwriter_id in songwriters_id:
        songwriter_id_hak_cipta = get_id_hak_cipta(request,songwriter_id,"songwriter")
        cursor.execute(
            '''
            SET search_path to MARMUT;
            INSERT INTO royalti
            VALUES (%s, %s, 0);
            ''', [songwriter_id_hak_cipta,id_konten]
        )
    
def get_id_hak_cipta(request,id,status):
    if status=="songwriter":
        cursor = connection.cursor()
        cursor.execute(
            '''
            SET search_path to MARMUT;
            SELECT id_pemilik_hak_cipta FROM songwriter
            WHERE id = %s;
            ''', [id]
        )
        try:
            id_hak_cipta = cursor.fetchone()[0]
            return id_hak_cipta
        except TypeError:
            return None
    elif status=="artist":
        cursor = connection.cursor()
        cursor.execute(
            '''
            SET search_path to MARMUT;
            SELECT id_pemilik_hak_cipta FROM artist WHERE id = %s;
            ''', [id]
        )
        try:
            id_hak_cipta = cursor.fetchone()[0]
            return id_hak_cipta
        except TypeError:
            return None    
    
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
        print(request.POST.get('artist'))
        create_song(request,request.POST.get('judul_lagu'),request.POST.get('artist'),request.POST.getlist('songwriter'),
                    request.POST.getlist('genre'),request.POST.get('durasi'),id_album)
        return redirect(request.META.get('HTTP_REFERER')) 

def create_song_action(request):
    if request.method == 'POST':
        print(request.POST.get('artist'))
        create_song(request,request.POST.get('judul_lagu'),request.POST.get('artist'),request.POST.getlist('songwriter'),
                    request.POST.getlist('genre'),request.POST.get('durasi'),request.POST.get('album'))
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

def get_label_id(request,label_email):
    cursor = connection.cursor()
    cursor.execute(
        '''
        SET search_path to MARMUT;
        SELECT l.id
        FROM label l
        WHERE l.email = %s;
        ''', [label_email]
    )
    try:
        label_id = cursor.fetchone()[0]
        return label_id
    except TypeError:
        return None
    
def show_r_cek_royalti(request):
    royalties = get_all_royalti(request)
    if royalties == None:
        royalties_dict = []
    else:
        royalties_dict = [
            {
                'judul_lagu': row[0],
                'judul_album': row[1],
                'total_play': row[2],
                'total_download': row[3],
                'total_royalti': row[4]
            }
            for row in royalties
        ]

    context = {'royalties': royalties_dict}
    return render(request, "r_cek_royalti.html", context)

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
    is_artist = False
    is_songwriter = False
    
    if request.COOKIES.get('is_artist') == 'True':
        is_artist = True
        artist_id = get_artist_id(request, request.COOKIES.get('user_email'))
    if request.COOKIES.get('is_songwriter') == 'True':
        is_songwriter = True
        songwriter_id = get_songwriter_id(request, request.COOKIES.get('user_email'))
    
    context = {'songwriters': songwriters, 'albums': albums, 'is_artist': is_artist, 'artist_id': artist_id, 
               'is_songwriter': is_songwriter, 'songwriter_id': songwriter_id,
               'genres': genres, 'labels': labels, 'artists': artists}
    return render(request, "crud_album_song.html",context)