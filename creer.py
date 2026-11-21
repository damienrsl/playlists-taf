"""Crée ou met à jour les 7 playlists TAF dans le Spotify de Damien.
Jeton : --sp-dc <cookie> | SP_DC env | --trousseau (lit la clé Chrome Safe Storage du trousseau macOS : UN dialogue « Autoriser »).
Résultat : liens.json {cle: {id, url}} puis relancer page.py."""
import json, os, re, sys, time, sqlite3, shutil, subprocess, hashlib, urllib.request, urllib.parse, pathlib

ICI = pathlib.Path(__file__).parent
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0 Safari/537.36"

def sp_dc_trousseau():
    pw = subprocess.run(["security", "find-generic-password", "-s", "Chrome Safe Storage", "-w"],
                        capture_output=True, text=True, timeout=180).stdout.strip()
    if not pw: raise SystemExit("trousseau : clé Chrome refusée ou absente")
    key = hashlib.pbkdf2_hmac("sha1", pw.encode(), b"saltysalt", 1003, 16)
    src = pathlib.Path.home() / "Library/Application Support/Google/Chrome/Default/Cookies"
    tmp = pathlib.Path("/tmp/ck-taf.db"); shutil.copy(src, tmp)
    row = sqlite3.connect(tmp).execute("select encrypted_value, host_key from cookies where host_key='.spotify.com' and name='sp_dc'").fetchone()
    tmp.unlink(missing_ok=True)
    if not row: raise SystemExit("pas de cookie sp_dc dans Chrome")
    blob, host = row
    if blob[:3] != b"v10": raise SystemExit("format de cookie inattendu " + str(blob[:3]))
    dec = subprocess.run(["openssl", "enc", "-d", "-aes-128-cbc", "-K", key.hex(), "-iv", (b" " * 16).hex()],
                         input=blob[3:], capture_output=True).stdout
    if dec[:32] == hashlib.sha256(host.encode()).digest(): dec = dec[32:]   # Chrome ≥ 130 préfixe l'empreinte de l'hôte
    return dec.decode("utf-8", "ignore").strip()

def jeton_depuis_sp_dc(sp_dc):
    req = urllib.request.Request("https://open.spotify.com/", headers={"User-Agent": UA, "Cookie": "sp_dc=" + sp_dc})
    h = urllib.request.urlopen(req, timeout=20).read().decode("utf-8", "ignore")
    m = re.search(r'<script id="session"[^>]*>(.*?)</script>', h, re.S)
    if not m: raise SystemExit("pas de session dans la page Spotify (cookie périmé ?)")
    s = json.loads(m.group(1))
    if s.get("isAnonymous"): raise SystemExit("session anonyme : le cookie sp_dc ne connecte pas")
    return s["accessToken"]

class Api:
    def __init__(self, tok): self.tok = tok
    def call(self, method, path, body=None, params=None):
        url = "https://api.spotify.com/v1" + path + (("?" + urllib.parse.urlencode(params)) if params else "")
        data = json.dumps(body).encode() if body is not None else None
        for _ in range(5):
            req = urllib.request.Request(url, data=data, method=method, headers={
                "Authorization": "Bearer " + self.tok, "Content-Type": "application/json", "User-Agent": UA,
                "app-platform": "WebPlayer", "Accept": "application/json"})
            try:
                with urllib.request.urlopen(req, timeout=30) as r:
                    raw = r.read(); return json.loads(raw) if raw else {}
            except urllib.error.HTTPError as e:
                if e.code == 429: time.sleep(int(e.headers.get("Retry-After", "3")) + 1); continue
                raise SystemExit(f"{method} {path} → {e.code} {e.read()[:300]}")
        raise SystemExit("trop de 429 sur " + path)

def main():
    args = sys.argv[1:]
    if "--trousseau" in args: sp_dc = sp_dc_trousseau()
    elif "--sp-dc" in args: sp_dc = args[args.index("--sp-dc") + 1]
    else: sp_dc = os.environ.get("SP_DC") or sys.exit("il faut --sp-dc, SP_DC ou --trousseau")
    api = Api(jeton_depuis_sp_dc(sp_dc))
    moi = api.call("GET", "/me"); print("connecté :", moi.get("display_name"), moi.get("id"))
    plans = json.load(open(ICI / "playlists.json"))
    liens_p = ICI / "liens.json"; liens = json.load(open(liens_p)) if liens_p.exists() else {}
    for p in plans:
        uris = [t["uri"] for t in p["titres"]]
        desc = (p["son"] + ". Playlist de concentration construite le 21/11/2026 : pas de paroles, tempo stable, ~" + str(p["duree_min"]) + " min.")[:300]
        if p["cle"] in liens:
            pid = liens[p["cle"]]["id"]
            api.call("PUT", f"/playlists/{pid}", {"name": p["nom"], "description": desc})
            api.call("PUT", f"/playlists/{pid}/tracks", {"uris": uris[:100]})
            for i in range(100, len(uris), 100): api.call("POST", f"/playlists/{pid}/tracks", {"uris": uris[i:i+100]})
            print("mise à jour :", p["nom"], len(uris))
        else:
            r = api.call("POST", f"/users/{moi['id']}/playlists", {"name": p["nom"], "description": desc, "public": False})
            pid = r["id"]
            for i in range(0, len(uris), 100): api.call("POST", f"/playlists/{pid}/tracks", {"uris": uris[i:i+100]}); time.sleep(0.5)
            liens[p["cle"]] = {"id": pid, "url": r["external_urls"]["spotify"], "nom": p["nom"]}
            json.dump(liens, open(liens_p, "w"), ensure_ascii=False, indent=1)
            print("créée :", p["nom"], len(uris), r["external_urls"]["spotify"])
        time.sleep(0.8)
    # vérification : relire chaque playlist
    for cle, l in liens.items():
        r = api.call("GET", f"/playlists/{l['id']}", params={"fields": "name,tracks.total"})
        print("vérif :", r["name"], r["tracks"]["total"], "titres")

if __name__ == "__main__": main()
