from django.db import connection
from django.shortcuts import redirect, render
from adminpage.classes import *
from adminpage.models import *
from .classes import *
from datetime import date

# Create your views here.

def loginPage(request):
    if request.method == "POST":
        ID = request.POST["ID"]
        type = request.POST["type"]

        tempData = None

        match type:
            case "Hasta":
                sql_query = "SELECT * FROM adminpage_hastalar WHERE hastaID=%s"
                params = (ID, )
                with connection.cursor() as cursor:
                    cursor.execute(sql_query, params)
                    tempData = dictfetchall(cursor)

                if len(tempData) == 1:
                    return redirect("hastaPage", int(tempData[0]["hastaID"]))

            case "Doktor":
                sql_query = "SELECT * FROM adminpage_doktorlar WHERE doktorID=%s"
                params = (ID, )
                with connection.cursor() as cursor:
                    cursor.execute(sql_query, params)
                    tempData = dictfetchall(cursor)
        
                if len(tempData) == 1:
                    return redirect("doktorPage", int(tempData[0]["doktorID"]))


        return render(request, "userpage/login.html", {
            "error": "Bu ID'ye sahip seçtiğiniz türde bir kişi bulunmuyor."
            })
    
    return render(request, "userpage/login.html")

def dictfetchall(cursor):
    desc = cursor.description
    return [
        dict(zip([col[0] for col in desc], row))
        for row in cursor.fetchall()
    ]

def hastaPage(request, id):
    green_error = None
    yellow_error = None
    red_error = None

    if request.method == "POST":
        if request.POST.get("sil"):
            randevu_id = request.POST["sil"]
            
            sql_query_deleting = "SELECT * FROM userpage_randevular WHERE id=%s"
            params_to_delete = (randevu_id, )
            with connection.cursor() as cursor:
                cursor.execute(sql_query_deleting, params_to_delete)
                tempData = dictfetchall(cursor)

            if len(tempData) == 1:
                randevu = randevuClass(hastaID=tempData[0]["hastaID_id"], doktorID=tempData[0]["doktorID_id"],
                                randevuTarihi=tempData[0]["randevuTarihi"], randevuSaati=tempData[0]["randevuSaati"])
                randevu.delete()
                sql_query_select = "SELECT * FROM adminpage_doktorlar WHERE doktorID=%s"
                params_to_select = (tempData[0]["doktorID_id"], )
                with connection.cursor() as cursor:
                    cursor.execute(sql_query_select, params_to_select)
                    selectedData = dictfetchall(cursor)
                red_error = f"{randevu.randevuTarihi} tarihinde {selectedData[0]["ad"]} {selectedData[0]["soyad"]} adlı doktordan alınan randevu iptal edildi."

        elif request.POST.get("degistir"):
            randevu_id = request.POST["degistir"]
            yeni_randevuTarihi = request.POST['yeniRandevuTarihi'+randevu_id]
            yeni_randevuSaati = request.POST['yeniRandevuSaati'+randevu_id]

            sql_query_updating = "SELECT * FROM userpage_randevular WHERE id=%s"
            params_to_update = (randevu_id, )
            with connection.cursor() as cursor:
                cursor.execute(sql_query_updating, params_to_update)
                tempData = dictfetchall(cursor)

            if len(tempData) == 1:
                randevu = randevuClass(hastaID=tempData[0]["hastaID_id"], doktorID=tempData[0]["doktorID_id"],
                                        randevuTarihi=yeni_randevuTarihi, randevuSaati=yeni_randevuSaati)
                randevu.update(randevu_id)
                sql_query_select = "SELECT * FROM adminpage_doktorlar WHERE doktorID=%s"
                params_to_select = (tempData[0]["doktorID_id"], )
                with connection.cursor() as cursor:
                    cursor.execute(sql_query_select, params_to_select)
                    selectedData = dictfetchall(cursor)
                yellow_error = f"{randevu.randevuTarihi} tarihinde {selectedData[0]["ad"]} {selectedData[0]["soyad"]} adlı doktordan alınan randevunun zamanı güncellendi."

        else:
            hasta_id = id
            doktor_id = request.POST["sectigiDoktor"]
            randevu_tarihi = request.POST["randevuTarihi"]
            randevu_saati = request.POST["randevuSaati"]

            randevu = randevuClass(hastaID=hasta_id, doktorID=doktor_id, randevuTarihi=randevu_tarihi, randevuSaati=randevu_saati)
            randevu.save()
            sql_query_select = "SELECT * FROM adminpage_doktorlar WHERE doktorID=%s"
            params_to_select = (doktor_id, )
            with connection.cursor() as cursor:
                cursor.execute(sql_query_select, params_to_select)
                selectedData = dictfetchall(cursor)
            green_error = f"{randevu.randevuTarihi} tarihine {selectedData[0]["ad"]} {selectedData[0]["soyad"]} adlı doktordan randevu alındı."


    sql_query1 = "SELECT * FROM adminpage_hastalar WHERE hastaID=%s"
    params1 = (id, )
    with connection.cursor() as cursor:
        cursor.execute(sql_query1, params1)
        userData = dictfetchall(cursor)

    sql_query2 = "SELECT * FROM adminpage_doktorlar"
    with connection.cursor() as cursor:
        cursor.execute(sql_query2)
        doktorData = dictfetchall(cursor)

    sql_query3 = "SELECT * FROM adminpage_doktorlar d, userpage_randevular r WHERE d.doktorID=r.doktorID_id AND r.hastaID_id=%s"
    params3 = (id, )
    with connection.cursor() as cursor:
        cursor.execute(sql_query3, params3)
        allRandevuData = dictfetchall(cursor)

    gecmis_randevular = []
    ileri_randevular = []

    for randevu in allRandevuData:
        randevu_tarihi = randevu.get("randevuTarihi")
        bugun = date.today().strftime('%d/%m/%Y')
        val = compareDate(str(randevu_tarihi), str(bugun))
        if val == "K":
            gecmis_randevular.append(randevu)
        else:
            ileri_randevular.append(randevu)

    data = {
        "user": userData[0],
        "doktorlar": doktorData,
        "randevular": ileri_randevular,
        "gecmis_randevular": gecmis_randevular,
        "green_error": green_error,
        "red_error": red_error,
        "yellow_error": yellow_error
    }

    return render(request, "userpage/hasta/hasta.html", data)

def doktorPage(request, id):
    sql_query = "SELECT * FROM adminpage_doktorlar WHERE doktorID=%s"
    params = (id, )
    with connection.cursor() as cursor:
        cursor.execute(sql_query, params)
        userdata = dictfetchall(cursor)

    sql_query3 = "SELECT * FROM adminpage_hastalar h, userpage_randevular r WHERE h.hastaID=r.hastaID_id AND r.doktorID_id=%s"
    params3 = (id, )
    with connection.cursor() as cursor:
        cursor.execute(sql_query3, params3)
        randevuData = dictfetchall(cursor)

    data = {
        "user": userdata[0],
        "randevular": randevuData,
    }

    return render(request, "userpage/doktor/doktor.html", data)

def hastaProfilePage(request, id):
    green_error = None

    if request.method == "POST":
        hastaID = id
        ad = request.POST["ad"]
        soyad = request.POST["soyad"]
        dogumTarihi =request.POST["dogumTarih"]
        cinsiyet = "null"
        telNo = request.POST["telefonNumarasi"]
        adres = request.POST["adres"]
            
        hasta = HastaClass(hastaID=hastaID, ad=ad, soyad=soyad, dogumTarihi=dogumTarihi,
                                cinsiyet=cinsiyet, telNo=telNo, adres=adres)
        hasta.update()
        green_error = "Bilgileriniz başarılı bir şekilde güncellendi."

    sql_query1 = "SELECT * FROM adminpage_hastalar WHERE hastaID=%s"
    params1 = (id, )
    with connection.cursor() as cursor:
        cursor.execute(sql_query1, params1)
        userData = dictfetchall(cursor)

    data = {
        "user": userData[0],
        "green_error": green_error
    }

    return render(request, "userpage/hasta/hasta_profil.html", data)

def doktorProfilePage(request, id):
    green_error = None

    if request.method == "POST":
        doktorID = id
        ad = request.POST["ad"]
        soyad = request.POST["soyad"]
        uzmanlikAlani = request.POST["uzmanlikAlani"]
        calistigiHastane = request.POST["calistigiHastane"]
            
        doktor = DoktorClass(doktorID=doktorID, ad=ad, soyad=soyad,
                        uzmanlikAlani=uzmanlikAlani, calistigiHastane=calistigiHastane )
        doktor.update()
        green_error = "Bilgileriniz başarılı bir şekilde güncellendi."


    sql_query1 = "SELECT * FROM adminpage_doktorlar WHERE doktorID=%s"
    params1 = (id, )
    with connection.cursor() as cursor:
        cursor.execute(sql_query1, params1)
        userData = dictfetchall(cursor)

    data = {
        "user": userData[0],
        "green_error": green_error
    }

    return render(request, "userpage/doktor/doktor_profil.html", data)

def doktorRaporPage(request, id):
    red_error = None
    yellow_error = None

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
        
        elif request.POST.get("degistir"):
            rapor_id = request.POST["degistir"]
            yeniRaporTarihi = request.POST['yeniRaporTarihi'+rapor_id]
            yeniRaporIcerigi = request.POST['yeniRaporIcerigi'+rapor_id]
            
            sql_query_updating = "SELECT * FROM adminpage_raporlar WHERE raporID=%s"
            params_to_update = (rapor_id, )
            with connection.cursor() as cursor:
                cursor.execute(sql_query_updating, params_to_update)
                updatedData = dictfetchall(cursor)

            if len(updatedData) == 1:
                rapor = RaporClass(raporID=updatedData[0]["raporID"], raporTarihi=yeniRaporTarihi, raporIcerigi=yeniRaporIcerigi, 
                    raporJSON=updatedData[0]["raporJSON"], hastaID=updatedData[0]["hastaID_id"], resimURL=updatedData[0]["resimURL"])
                rapor.update()

                yellow_error = f"{yeniRaporTarihi} tarihindeki {updatedData[0]["raporID"]} ID'li rapor güncellendi."


    sql_query = "SELECT r.raporID, r.raporTarihi, r.raporIcerigi, r.hastaID_id, h.ad, h.soyad FROM adminpage_raporlar r, adminpage_hastalar h WHERE r.hastaID_id=h.hastaID AND r.hastaID_id IN (SELECT DISTINCT h.hastaID FROM adminpage_hastalar h, userpage_randevular r WHERE h.hastaID=r.hastaID_id AND r.doktorID_id=%s)"
    params = (id, )
    with connection.cursor() as cursor:
        cursor.execute(sql_query, params)
        raporlar = dictfetchall(cursor)


    sql_query2 = "SELECT DISTINCT h.hastaID, h.ad, h.soyad FROM adminpage_hastalar h, userpage_randevular r WHERE h.hastaID=r.hastaID_id AND r.doktorID_id=%s"
    params2 = (id, )
    with connection.cursor() as cursor:
        cursor.execute(sql_query2, params2)
        hastalar = dictfetchall(cursor)

    sql_query1 = "SELECT * FROM adminpage_doktorlar WHERE doktorID=%s"
    params1 = (id, )
    with connection.cursor() as cursor:
        cursor.execute(sql_query1, params1)
        userData = dictfetchall(cursor)

    sql_query_all = "SELECT raporID FROM adminpage_raporlar"
    with connection.cursor() as cursor:
        cursor.execute(sql_query_all)
        raporlar_all = dictfetchall(cursor)
   
    data = {
        "user": userData[0],
        "raporlar": raporlar,
        "hastalar": hastalar,
        "red_error": red_error,
        "yellow_error": yellow_error,
        "raporlar_all": raporlar_all
    }

    return render(request, "userpage/doktor/raporlar.html", data)

def doktorDownloadPage(request, id):
    sql_query = "SELECT r.* FROM adminpage_raporlar r WHERE r.hastaID_id IN (SELECT DISTINCT h.hastaID FROM adminpage_hastalar h, userpage_randevular r WHERE h.hastaID=r.hastaID_id AND r.doktorID_id=%s)"
    params = (id, )
    with connection.cursor() as cursor:
        cursor.execute(sql_query, params)
        raporlar = dictfetchall(cursor)

    data = {
        "raporlar": raporlar
    }

    return render(request, "userpage/doktor/raporindir_doktor.html", data)

def doktorHastalarimPage(request, id):
    sql_query1 = "SELECT * FROM adminpage_doktorlar WHERE doktorID=%s"
    params1 = (id, )
    with connection.cursor() as cursor:
        cursor.execute(sql_query1, params1)
        userData = dictfetchall(cursor)

    sql_query2 = "SELECT DISTINCT a.* FROM adminpage_hastalar a WHERE a.hastaID IN (SELECT h.hastaID FROM adminpage_hastalar h, userpage_randevular r WHERE h.hastaID=r.hastaID_id AND r.doktorID_id=%s)"
    params2 = (id, )
    with connection.cursor() as cursor:
        cursor.execute(sql_query2, params2)
        hastalarım = dictfetchall(cursor)

    data = {
        "user": userData[0],
        "hastalarım": hastalarım
    }

    return render(request, "userpage/doktor/hastalarim.html", data)

def hastaRaporPage(request, id):
    red_error = None
    yellow_error = None
    blue_error = None

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
        
        elif request.POST.get("degistir"):
            rapor_id = request.POST["degistir"]
            yeniRaporTarihi = request.POST['yeniRaporTarihi'+rapor_id]
            yeniRaporIcerigi = request.POST['yeniRaporIcerigi'+rapor_id]
            
            sql_query_updating = "SELECT * FROM adminpage_raporlar WHERE raporID=%s"
            params_to_update = (rapor_id, )
            with connection.cursor() as cursor:
                cursor.execute(sql_query_updating, params_to_update)
                updatedData = dictfetchall(cursor)

            if len(updatedData) == 1:
                rapor = RaporClass(raporID=updatedData[0]["raporID"], raporTarihi=yeniRaporTarihi, raporIcerigi=yeniRaporIcerigi, 
                    raporJSON=updatedData[0]["raporJSON"], hastaID=updatedData[0]["hastaID_id"], resimURL=updatedData[0]["resimURL"])
                rapor.update()

                yellow_error = f"{yeniRaporTarihi} tarihindeki {updatedData[0]["raporID"]} ID'li rapor güncellendi."




    sql_query1 = "SELECT * FROM adminpage_hastalar WHERE hastaID=%s"
    params1 = (id, )
    with connection.cursor() as cursor:
        cursor.execute(sql_query1, params1)
        userData = dictfetchall(cursor)

    sql_query_all = "SELECT raporID FROM adminpage_raporlar"
    with connection.cursor() as cursor:
        cursor.execute(sql_query_all)
        raporlar_all = dictfetchall(cursor)

    sql_query2 = "SELECT raporID_id FROM adminpage_bildirimsistemi WHERE hastaID_id=%s"
    params2 = (id, )
    with connection.cursor() as cursor:
        cursor.execute(sql_query2, params2)
        raporlar2 = dictfetchall(cursor)

    sql_query = "SELECT * FROM adminpage_raporlar WHERE hastaID_id=%s"
    params = (id, )
    with connection.cursor() as cursor:
        cursor.execute(sql_query, params)
        raporlar = dictfetchall(cursor)

    array1 = []
    array2 = []

    for r in raporlar:
        array1.append(r["raporID"])

    for r in raporlar2:
        array2.append(r["raporID_id"])

    set1 = set(array1)
    set2 = set(array2)
    
    ortak_elemanlar = set1.intersection(set2)
    ortak_olmayanlar = (set1 - ortak_elemanlar) | (set2 - ortak_elemanlar)

    if len(ortak_olmayanlar) > 0:
        if len(ortak_olmayanlar) == 1: 
            blue_error = ', '.join(map(str, ortak_olmayanlar)) + " ID'li raporunuz yeni eklendi."
        else:  
            blue_error = ', '.join(map(str, ortak_olmayanlar)) + " ID'li raporlarınız yeni eklendi."

        for o in ortak_olmayanlar:
            bildirimSistemi = BildirimSistemiClass(raporID=o, hastaID=id)
            bildirimSistemi.save()
    
    data = {
        "user": userData[0],
        "raporlar_all": raporlar_all,
        "raporlar": raporlar,
        "yellow_error": yellow_error,
        "red_error": red_error,
        "blue_error": blue_error
    }
        
    return render(request, "userpage/hasta/raporlar.html", data)

def hastaDownloadPage(request, id):
    sql_query = "SELECT * FROM adminpage_raporlar WHERE hastaID_id=%s"
    params = (id, )
    with connection.cursor() as cursor:
        cursor.execute(sql_query, params)
        raporlar = dictfetchall(cursor)

    data = {
        "raporlar": raporlar
    }

    return render(request, "userpage/doktor/raporindir_doktor.html", data)