from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib import messages  
from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.db import connection
import datetime, uuid

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




def show_crud_album_song(request):
    return render(request, "crud_album_song.html")

def show_r_cek_royalti(request):
    return render(request, "r_cek_royalti.html")

def show_rd_kelola_album_song(request):
    return render(request, "rd_kelola_album_song.html")


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