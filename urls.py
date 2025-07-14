from django.urls import path
from meine_app import views as app_views
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

urlpatterns = [
    path("upload", app_views.saveUploadedFile, name="upload"),
    path("form", app_views.landingPage),
    path("g", app_views.g),
    path("startseite", app_views.startseite, name="startseite"),
    path("login", app_views.login, name="login"),
    path("posten", app_views.posten, name="posten"),
    path("profil", app_views.profil, name="profil"),
    path("profil_bearbeiten", app_views.profil_bearbeiten, name="profil_bearbeiten"),
    path("registrieren", app_views.registrieren, name="registrieren"),
    path("ueber_uns", app_views.ueber_uns, name="ueber_uns"),
    path("post/<str:bildname>/", app_views.post_detail, name="post_detail"),
    path("save_comment/", app_views.save_comment, name="save_comment")
]

urlpatterns += staticfiles_urlpatterns()