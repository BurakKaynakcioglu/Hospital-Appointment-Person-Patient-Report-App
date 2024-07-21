from django.urls import path
from . import views

urlpatterns = [
    path("", views.hastalar),
    path("hastalar", views.hastalar, name="hastalar"),
    path("doktorlar", views.doktorlar, name="doktorlar"),
    path("raporlar", views.raporlar, name="raporlar"),
    path("rapor_indir", views.downloadPage, name="rapor_indir"),
    path("add", views.add, name="add"),
    path("download", views.download, name="download"),
]
