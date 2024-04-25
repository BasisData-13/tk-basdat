from django.db import models

class AKUN(models.Model):
    email = models.CharField(max_length=50, primary_key=True)
    password = models.CharField(max_length=50, null=False)
    nama = models.CharField(max_length=100, null=False)
    gender = models.IntegerField(null=False)
    tempat_lahir = models.CharField(max_length=50, null=False)
    tanggal_lahir = models.DateField(null=False)
    is_verified = models.BooleanField(null=False)
    kota_asal = models.CharField(max_length=50, null=False)