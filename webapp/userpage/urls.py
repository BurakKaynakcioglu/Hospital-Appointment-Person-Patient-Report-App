from django.urls import path
from . import views

urlpatterns = [
    path("", views.loginPage),
    path("main", views.loginPage),
    path("hasta/<int:id>", views.hastaPage, name="hastaPage"),
    path("doktor/<int:id>", views.doktorPage, name="doktorPage"),
    path("hasta_profil/<int:id>", views.hastaProfilePage, name="hastaProfilePage"),
    path("hasta_rapor/<int:id>", views.hastaRaporPage, name="hastaRaporPage"),
    path("rapor_indir_hasta/<int:id>", views.hastaDownloadPage, name="hastaDownloadPage"),
    path("doktor_profil/<int:id>", views.doktorProfilePage, name="doktorProfilePage"),
    path("doktor_rapor/<int:id>", views.doktorRaporPage, name="doktorRaporPage"),
    path("rapor_indir_doktor/<int:id>", views.doktorDownloadPage, name="doktorDownloadPage"),
    path("hastalarim_doktor/<int:id>", views.doktorHastalarimPage, name="doktorHastalarimPage"),

]
