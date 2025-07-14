import json
import os
from django.shortcuts import render
from django.shortcuts import redirect
from django.http import HttpResponse
from django.core.files.storage import FileSystemStorage
from django.views.decorators.csrf import csrf_exempt

BESCHREIBUNGEN_DATEI = "/var/www/static/images/beschreibungen.json"
UPLOAD_VERZEICHNIS = "/var/www/static/images"

def landingPage(request):
    with open("/var/www/static/images/beschreibungen.json", "r") as file:
        dictionary = json.load(file)
    vars = {
        "dictionary": dictionary,
    }
    return render(request, "meine_app/template.html", vars)

    

def startseite(request):
    if os.path.exists(BESCHREIBUNGEN_DATEI):
        with open(BESCHREIBUNGEN_DATEI, "r") as datei:
            try: 
                beschreibungen = json.load(datei)
            except:
                beschreibungen = {}
    else:
        beschreibungen = {}
    return render(request, "meine_app/startseite.html", {"posts": beschreibungen})

def posten(request):
    return render(request, "meine_app/posten.html")

def profil(request):
    if "username" not in request.session:
        return redirect("login")

    username = request.session["username"]

    if os.path.exists(BESCHREIBUNGEN_DATEI):
        with open(BESCHREIBUNGEN_DATEI, "r") as datei: 
            try:
                beschreibungen = json.load(datei)
            except:
                beschreibungen = {}
    else:
        beschreibungen = {}
    
    eigene_posts = {}
    for bild, info in beschreibungen.items():
        if isinstance(info, dict) and info.get("benutzer") == username:
            eigene_posts[bild] = info

    users = load_users()
    user_data = users.get(username, {})

    return render(request, "meine_app/profil.html", {"user": user_data, "posts": eigene_posts} )

def profil_bearbeiten(request):
    if "username" not in request.session:
        return redirect("login")

    username = request.session["username"]
    users = load_users()
    user_data = users.get(username, {})

    if request.method == "POST":
        user_data["vorname"] = request.POST.get("vorname", "")
        user_data["nachname"] = request.POST.get("nachname", "")
        user_data["email"] = request.POST.get("email", "")
        user_data["geburtsdatum"] = request.POST.get("geburtsdatum", "")

        new_password = request.POST.get("password", "")
        if new_password:
            user_data["password"] = new_password

        users[username] = user_data
        save_users(users)

        return redirect("profil")

    return render(request, "meine_app/profil_bearbeiten.html", {"user": user_data})
    
def registrieren(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        vorname = request.POST.get("vorname")
        nachname = request.POST.get("nachname")
        email = request.POST.get("email")
        geburtsdatum = request.POST.get("geburtsdatum")

        users = load_users()

        if username in users:
            return HttpResponse("Benutzer existiert bereits.")

        users[username] = {
            "password": password,
            "vorname": vorname,
            "nachname": nachname,
            "email": email,
            "geburtsdatum": geburtsdatum,
        }
        save_users(users)

        request.session["username"] = username
        return redirect("startseite")
    return render(request, "meine_app/registrieren.html")

def login(request):
    return render(request, "meine_app/login.html")


def ueber_uns(request):
    return render(request, "meine_app/ueber_uns.html")

USERS_FILES = os.path.join(os.path.dirname(__file__), "users.json")

def load_users():
    if os.path.exists(USERS_FILES):
        with open(USERS_FILES, "r") as datei:
            return json.load(datei)
    return {}

def login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        users = load_users()
        if username in users and users[username]["password"] == password:
            request.session["username"] = username
            return redirect("startseite")
        else:
            return HttpResponse("Ungültige Anmeldedaten")

    return render(request, "meine_app/login.html")


def home_view(request):
    if "username" not in request.session:
        return redirect("startseite")
    return render(request, "meine_app/startseite.html", {"username": request.session["username"]})

def logout_view(request):
    request.session.flush()
    return redirect("login")

def save_users(users):
    with open(USERS_FILES, "w") as datei:
        json.dump(users, datei)


def saveUploadedFile(request):
    if request.method == "POST" and request.FILES.get("datei"):
        datei = request.FILES["datei"]
        beschreibung = request.POST.get("titel", "")

        fs = FileSystemStorage(location=UPLOAD_VERZEICHNIS)
        filename = fs.save(datei.name, datei)

        if os.path.exists(BESCHREIBUNGEN_DATEI):
            with open(BESCHREIBUNGEN_DATEI, "r") as datei:
                try:
                    beschreibungen = json.load(datei)
                except:
                    beschreibungen = {}
        else:
            beschreibungen = {}
        
        neuer_eintrag = {
            "beschreibung": beschreibung,
            "benutzer": request.session.get("username", "unbekannt")
        }
        beschreibungen[filename] = neuer_eintrag

        with open(BESCHREIBUNGEN_DATEI, "w") as datei: 
            json.dump(beschreibungen, datei)

        
        return redirect("startseite")
    return HttpResponse("Kein Bild hochgeladen oder Fehler aufgetreten")
    
def post_detail(request, bildname):
    # Bildinfos aus der JSON-Datei holen
    if os.path.exists(BESCHREIBUNGEN_DATEI):
        with open(BESCHREIBUNGEN_DATEI, "r") as f:
            alle_beschreibungen = json.load(f)
    else:
        alle_beschreibungen = {}

    info = alle_beschreibungen.get(bildname, {})
    
    # Kommentare laden
    KOMMENTARE_DATEI = "/var/www/static/comments.json"
    if os.path.exists(KOMMENTARE_DATEI):
        with open(KOMMENTARE_DATEI, "r") as f:
            alle_kommentare = json.load(f)
    else:
        alle_kommentare = {}
    
    kommentare = alle_kommentare.get(bildname, [])

    context = {
        "bildname": bildname,
        "info": info,
        "kommentare": kommentare,
    }
    return render(request, "meine_app/post_detail.html", context)


@csrf_exempt
def save_comment(request):
    if request.method == "POST":
        data = json.loads(request.body)
        bild = data.get("bild")
        comment_text = data.get("comment")
        COMENTS_FILE = "/var/www/static/comments.json"

        username = request.session.get("username", "unbekannt")

        if os.path.exists(COMENTS_FILE):
            with open(COMENTS_FILE, "r") as datei:
                comments = json.load(datei)
        else: 
            comments = {}

        neuer_kommentar = {
            "benutzer": username,
            "text": comment_text
        }

        comments.setdefault(bild, []).append(neuer_kommentar)

        with open(COMENTS_FILE, "w") as datei:
            json.dump(comments, datei)
        
        return JsonResponse({"status": "success"})
    return JsonResponse({"error": "Ungültige Methode"}, status=405)