import os
from django.shortcuts import redirect, render
from django.http.response import HttpResponse
from .models import *
from .classes import *
from userpage.views import dictfetchall
import cloudinary.uploader
from webapp.settings import CLOUDINARY_STORAGE
import requests
import json

# Create your views here.

def hastalar(request):
    green_error = None
    red_error = None

    if request.method == "POST":
        if request.POST.get("sil"):
            hasta_id = request.POST["sil"]

            sql_query_deleting = "SELECT * FROM adminpage_hastalar WHERE hastaID=%s"
            params_deleting = (hasta_id, )
            with connection.cursor() as cursor:
                cursor.execute(sql_query_deleting, params_deleting)
                tempData = dictfetchall(cursor)

            if len(tempData) == 1:
                hasta = HastaClass(hastaID=tempData[0]["hastaID"], ad=tempData[0]["ad"], soyad=tempData[0]["soyad"], 
                                dogumTarihi=tempData[0]["dogumTarihi"], cinsiyet=tempData[0]["cinsiyet"], 
                                telNo=tempData[0]["telNo"], adres=tempData[0]["adres"])                
                hasta.delete()
                red_error = f"ID: {hasta.hastaID} | Hasta başarılı bir şekilde silindi"
                
        else:
            hastaID = int(request.POST["hastaID"])
            ad = request.POST["ad"]
            soyad = request.POST["soyad"]
            dogumTarihi =request.POST["dogumTarih"]
            cinsiyet = request.POST["cinsiyet"]
            telNo = request.POST["telefonNumarasi"]
            adres = request.POST["adres"]
            
            hasta = HastaClass(hastaID=hastaID, ad=ad, soyad=soyad, dogumTarihi=dogumTarihi,
                                cinsiyet=cinsiyet, telNo=telNo, adres=adres)
            hasta.save()
            green_error = f"ID: {hasta.hastaID} | Hasta başarılı bir şekilde eklendi."

    sql_query = "SELECT * FROM adminpage_hastalar"
    with connection.cursor() as cursor:
        cursor.execute(sql_query)
        hastalar = dictfetchall(cursor)

    data = {
        "hastalar": hastalar,
        "red_error": red_error,
        "green_error": green_error
    }

    return render(request, "adminpage/hastalar.html", data)

def doktorlar(request):
    green_error = None
    red_error = None
    yellow_error = None

    if request.method == "POST":
        if request.POST.get("sil"):
            doktor_id = request.POST["sil"]

            sql_query_deleting = "SELECT * FROM adminpage_doktorlar WHERE doktorID=%s"
            params_deleting = (doktor_id, )
            with connection.cursor() as cursor:
                cursor.execute(sql_query_deleting, params_deleting)
                tempData = dictfetchall(cursor)

            if len(tempData) == 1:
                doktor = DoktorClass(doktorID=tempData[0]["doktorID"], ad=tempData[0]["ad"], soyad=tempData[0]["soyad"], 
                    uzmanlikAlani=tempData[0]["uzmanlikAlani"], calistigiHastane=tempData[0]["calistigiHastane"])
                
                if doktor.checkRandevu() == 0:
                    doktor.delete()
                    red_error = f"ID: {doktor.doktorID} | Doktor başarılı bir şekilde silindi."
                else:
                    yellow_error = f"ID: {doktor.doktorID} | Doktor randevuları olduğu için silinemedi."
                
        else:
            doktorID = int(request.POST["doktorID"])
            ad = request.POST["ad"]
            soyad = request.POST["soyad"]
            uzmanlikAlani =request.POST["uzmanlikAlani"]
            calistigiHastane = request.POST["calistigiHastane"]

            doktor = DoktorClass(doktorID=doktorID, ad=ad, soyad=soyad, 
                    uzmanlikAlani=uzmanlikAlani, calistigiHastane=calistigiHastane)
            doktor.save()
            green_error = f"ID: {doktor.doktorID} | Doktor başarılı bir şekilde eklendi"
        

    sql_query = "SELECT * FROM adminpage_doktorlar"
    with connection.cursor() as cursor:
        cursor.execute(sql_query)
        doktorlar = dictfetchall(cursor)

    data = {
        "doktorlar": doktorlar,
        "red_error": red_error,
        "green_error": green_error,
        "yellow_error": yellow_error
    }

    return render(request, "adminpage/doktorlar.html", data)


def raporlar(request):
    red_error = None

    if request.method == "POST":
        if request.POST.get("sil"):
            rapor_id = request.POST["sil"]

            sql_query_deleting = "SELECT * FROM adminpage_raporlar WHERE raporID=%s"
            params_to_delete = (rapor_id, )
            with connection.cursor() as cursor:
                cursor.execute(sql_query_deleting, params_to_delete)
                tempData = dictfetchall(cursor)

            if len(tempData) == 1:
                rapor = RaporClass(raporID=tempData[0]["raporID"], raporTarihi=tempData[0]["raporTarihi"], raporIcerigi=tempData[0]["raporIcerigi"], 
                        raporJSON=tempData[0]["raporJSON"], hastaID=tempData[0]["hastaID_id"], resimURL=tempData[0]["resimURL"])
                rapor.delete()
                red_error = f"{tempData[0]["raporTarihi"]} tarihinde eklenen {tempData[0]["raporID"]} ID'li rapor silindi."

    #sql_query = "SELECT r.raporID, r.raporTarihi, r.raporIcerigi, r.hastaID_id, h.ad, h.soyad FROM adminpage_raporlar r, adminpage_hastalar h WHERE r.hastaID_id=h.hastaID AND r.hastaID_id IN (SELECT DISTINCT h.hastaID FROM adminpage_hastalar h, userpage_randevular r WHERE h.hastaID=r.hastaID_id AND r.doktorID_id=%s)"

    sql_query = "SELECT r.raporID, r.raporTarihi, r.raporIcerigi, r.hastaID_id, h.ad, h.soyad FROM adminpage_raporlar r, adminpage_hastalar h WHERE r.hastaID_id=h.hastaID"
    with connection.cursor() as cursor:
        cursor.execute(sql_query)
        raporlar = dictfetchall(cursor)

    sql_query2 = "SELECT hastaID, ad, soyad FROM adminpage_hastalar"
    with connection.cursor() as cursor:
        cursor.execute(sql_query2)
        hastalar = dictfetchall(cursor)

    data = {
        "raporlar": raporlar,
        "hastalar": hastalar,
        "red_error": red_error
    }

    return render(request, "adminpage/raporlar.html", data)

def add(request):
    if request.method == "POST":
        raporID = request.POST["raporID"]
        hastaID = request.POST["hastaID"]
        raporTarihi = request.POST["raporTarihi"]
        raporIcerigi = request.POST["raporIcerigi"]
        raporJSON = request.FILES["raporJSON"]
        raporResim = request.FILES["raporResim"]

        cloudinary.config(
            cloud_name=CLOUDINARY_STORAGE['CLOUD_NAME'],
            api_key=CLOUDINARY_STORAGE['API_KEY'],
            api_secret=CLOUDINARY_STORAGE['API_SECRET']
        )
        result = cloudinary.uploader.upload(raporResim, folder="media")
        resimURL = result['url']
 
        raporJSON_content = json.loads(raporJSON.read())
        content = json.dumps(raporJSON_content)

        rapor = RaporClass(raporID=raporID, hastaID=hastaID, raporTarihi=raporTarihi, 
                    raporIcerigi=raporIcerigi, raporJSON=content, resimURL=resimURL)
        rapor.save()

        if request.POST.get("hasta_rapor_ekledi"):
            bildirimSistemi = BildirimSistemiClass(raporID=request.POST["raporID"], hastaID=request.POST["hastaID"])
            bildirimSistemi.save()

        success = "Rapor başarılı bir şekilde eklendi."
        return HttpResponse(success)

def downloadPage(request):
    sql_query = "SELECT * FROM adminpage_raporlar"
    with connection.cursor() as cursor:
        cursor.execute(sql_query)
        raporlar = dictfetchall(cursor)

    data = {
        "raporlar": raporlar
    }

    return render(request, "adminpage/raporindir.html", data)


def download(request):
    if request.method == "POST":
        raporID = request.POST["rapor_ID"]
        sql_query = "SELECT * FROM adminpage_raporlar WHERE raporID=%s"
        params = (raporID, )

        with connection.cursor() as cursor:
            cursor.execute(sql_query, params)
            indirilcek_rapor = dictfetchall(cursor)[0]

            #json indir
            dosya_adı = f'{raporID}_rapor.json'
            data = json.loads(indirilcek_rapor["raporJSON"])
            dosya_yolu = os.path.join(os.path.expanduser("~"), "Desktop", dosya_adı)
            with open(dosya_yolu, 'w') as json_file:
                json.dump(data, json_file, indent=4)
            with open(dosya_yolu, 'rb') as file:
                file.read()

        #resim indir
        dosya_adı_resim = f'{raporID}_resim.jpg'
        response = requests.get(indirilcek_rapor["resimURL"])
        if response.status_code == 200:
            masaustu_yolu = os.path.join(os.path.expanduser("~"), "Desktop", dosya_adı_resim)
            with open(masaustu_yolu, 'wb') as dosya:
                dosya.write(response.content)
    
        success = "Rapor başarılı bir şekilde indirildi."
        return HttpResponse(success)