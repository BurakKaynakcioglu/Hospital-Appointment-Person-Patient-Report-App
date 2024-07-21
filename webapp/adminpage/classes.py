
from django.db import connection
import cloudinary.uploader
import cloudinary.api
import cloudinary
from userpage.views import dictfetchall
from webapp.settings import CLOUDINARY_STORAGE


def dictfetchall(cursor):
    desc = cursor.description
    return [
        dict(zip([col[0] for col in desc], row))
        for row in cursor.fetchall()
    ]

class HastaClass(): 
    def __init__(self, hastaID, ad, soyad, dogumTarihi, cinsiyet, telNo, adres):
        self.hastaID = hastaID
        self.ad = ad
        self.soyad = soyad
        self.dogumTarihi = dogumTarihi
        self.cinsiyet = cinsiyet
        self.telNo = telNo
        self.adres = adres
    
    def save(self):        
        sql_query = "INSERT INTO adminpage_hastalar (hastaID, ad, soyad, dogumTarihi, cinsiyet, telNo, adres) VALUES (%s, %s, %s, %s, %s, %s, %s)"
        params = (self.hastaID, self.ad, self.soyad, self.dogumTarihi, self.cinsiyet, self.telNo, self.adres)

        with connection.cursor() as cursor:
            cursor.execute(sql_query, params)
    
    def delete(self):
        sql_query_deletion = "DELETE FROM userpage_randevular WHERE hastaID_id=%s"
        params_deletion = (self.hastaID, )
        with connection.cursor() as cursor:
            cursor.execute(sql_query_deletion, params_deletion)

        sql_query1 = "DELETE FROM adminpage_bildirimsistemi WHERE hastaID_id = %s"
        params1 = (self.hastaID, )
        with connection.cursor() as cursor:
            cursor.execute(sql_query1, params1)

        sql_query_deletion_rapor = "DELETE FROM adminpage_raporlar WHERE hastaID_id=%s"
        params_deletion_rapor = (self.hastaID, )
        with connection.cursor() as cursor:
            cursor.execute(sql_query_deletion_rapor, params_deletion_rapor)

        sql_query = "DELETE FROM adminpage_hastalar WHERE hastaID = %s"
        params = (self.hastaID, )
        with connection.cursor() as cursor:
            cursor.execute(sql_query, params)

    def update(self):
        sql_query = "UPDATE adminpage_hastalar SET ad=%s, soyad=%s, dogumTarihi=%s, telNo=%s, adres=%s WHERE hastaID=%s"
        params = (self.ad, self.soyad, self.dogumTarihi, self.telNo, self.adres, self.hastaID)
        with connection.cursor() as cursor:
            cursor.execute(sql_query, params)


class DoktorClass(): 
    def __init__(self, doktorID, ad, soyad, uzmanlikAlani, calistigiHastane):
        self.doktorID = doktorID
        self.ad = ad
        self.soyad = soyad
        self.uzmanlikAlani = uzmanlikAlani
        self.calistigiHastane = calistigiHastane

    def save(self):
        sql_query = "INSERT INTO adminpage_doktorlar (doktorID, ad, soyad, uzmanlikAlani, calistigiHastane) VALUES (%s, %s, %s, %s, %s)"
        params = (self.doktorID, self.ad, self.soyad, self.uzmanlikAlani, self.calistigiHastane)

        with connection.cursor() as cursor:
            cursor.execute(sql_query, params)

    def delete(self):
        sql_query_deletion = "DELETE FROM userpage_randevular WHERE doktorID_id=%s"
        params_deletion = (self.doktorID, )
        with connection.cursor() as cursor:
            cursor.execute(sql_query_deletion, params_deletion)

        sql_query = "DELETE FROM adminpage_doktorlar WHERE doktorID = %s"
        params = (self.doktorID, )
        with connection.cursor() as cursor:
            cursor.execute(sql_query, params)

    def update(self):
        sql_query = "UPDATE adminpage_doktorlar SET ad=%s, soyad=%s, calistigiHastane=%s, uzmanlikAlani=%s WHERE doktorID=%s"
        params = (self.ad, self.soyad, self.calistigiHastane, self.uzmanlikAlani, self.doktorID)
        with connection.cursor() as cursor:
            cursor.execute(sql_query, params)

    def checkRandevu(self):
        sql_query = "SELECT COUNT(*) FROM userpage_randevular WHERE doktorID_id=%s"
        params = (self.doktorID, )
        with connection.cursor() as cursor:
            cursor.execute(sql_query, params)
            dataCount = dictfetchall(cursor)

        print(dataCount[0]["COUNT(*)"])
        return dataCount[0]["COUNT(*)"]

class RaporClass():
    def __init__(self, raporID, hastaID, raporTarihi, raporIcerigi, raporJSON, resimURL):
        self.raporID = raporID
        self.hastaID = hastaID
        self.raporTarihi = raporTarihi
        self.raporIcerigi = raporIcerigi
        self.raporJSON = raporJSON
        self.resimURL = resimURL

    def save(self):
        sql_query = "INSERT INTO adminpage_raporlar (raporID, raporTarihi, raporIcerigi, raporJSON, hastaID_id, resimURL) VALUES (%s, %s, %s, %s, %s, %s)"
        params = (self.raporID, self.raporTarihi, self.raporIcerigi, self.raporJSON, self.hastaID, self.resimURL)

        with connection.cursor() as cursor:
            cursor.execute(sql_query, params)

    def delete(self):
        sql_query = "DELETE FROM adminpage_bildirimsistemi WHERE raporID_id = %s"
        params = (self.raporID, )
        with connection.cursor() as cursor:
            cursor.execute(sql_query, params)

        sql_query2 = "SELECT resimURL FROM adminpage_raporlar WHERE raporID = %s"
        params2 = (self.raporID, )
        with connection.cursor() as cursor:
            cursor.execute(sql_query2, params2)
            silincekResimURL = dictfetchall(cursor)[0]["resimURL"]

        parts = silincekResimURL.split("/")
        media_index = parts.index("media")
        media_string = "/".join(parts[media_index:])
        filename = media_string.split(".")[0]
        publicID = [filename]
        cloudinary.config(
            cloud_name=CLOUDINARY_STORAGE['CLOUD_NAME'],
            api_key=CLOUDINARY_STORAGE['API_KEY'],
            api_secret=CLOUDINARY_STORAGE['API_SECRET']
        )
        print(publicID)
        cloudinary.api.delete_resources(publicID, resource_type="image", type="upload")

        sql_query1 = "DELETE FROM adminpage_raporlar WHERE raporID = %s"
        params1 = (self.raporID, )
        with connection.cursor() as cursor:
            cursor.execute(sql_query1, params1)

    def update(self):
        sql_query = "UPDATE adminpage_raporlar SET raporTarihi=%s, raporIcerigi=%s WHERE raporID=%s"
        params = (self.raporTarihi, self.raporIcerigi, self.raporID)
        with connection.cursor() as cursor:
            cursor.execute(sql_query, params)


class BildirimSistemiClass():
    def __init__(self, raporID, hastaID):
        self.raporID = raporID
        self.hastaID = hastaID

    def save(self):
        sql_query = "INSERT INTO adminpage_bildirimsistemi (raporID_id, hastaID_id) VALUES (%s, %s)"
        params = (self.raporID, self.hastaID)

        with connection.cursor() as cursor:
            cursor.execute(sql_query, params)

    def delete(self):
        sql_query = "DELETE FROM adminpage_bildirimsistemi WHERE raporID_id = %s"
        params = (self.raporID, )
        with connection.cursor() as cursor:
            cursor.execute(sql_query, params)

        