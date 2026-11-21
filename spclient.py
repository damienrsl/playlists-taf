"""Écriture de playlists par les points d'entrée du lecteur web (spclient), avec les en-têtes capturés par session.mjs.
Même voie que les playlists Flow (19/10, 03/11) : kind 2 = ajout, kind 6 = attributs (nom, description)."""
import json, time, urllib.request, urllib.parse, pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).parent))
import creer, spot

SP = "https://spclient.wg.spotify.com"

def entetes():
    h = creer.entetes_lecteur()
    return {"Authorization": h["authorization"], "client-token": h["client-token"], "spotify-app-version": h["spotify-app-version"],
            "app-platform": "WebPlayer", "User-Agent": h["user-agent"], "Accept": "application/json", "Content-Type": "application/json",
            "Origin": "https://open.spotify.com", "Referer": "https://open.spotify.com/"}

def appel(method, url, body=None, h=None):
    h = h or entetes()
    data = json.dumps(body).encode() if body is not None else None
    for _ in range(4):
        req = urllib.request.Request(url, data=data, method=method, headers=h)
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                raw = r.read(); return json.loads(raw) if raw.strip() else {}
        except urllib.error.HTTPError as e:
            if e.code == 429: time.sleep(int(e.headers.get("Retry-After", "3")) + 1); continue
            raise SystemExit(f"{method} {url.split('.com')[1][:60]} → {e.code} {e.read()[:300]}")
    raise SystemExit("429 répétés " + url)

def username():
    d = spot.api("/playlists/7eUSan9utyV6rNcnmy5f8f", {"fields": "owner(id,display_name)"})
    return d["owner"]["id"], d["owner"].get("display_name")

def attributs(nom, description=""):
    return {"kind": 6, "updateListAttributes": {"newAttributes": {"values": {"name": nom, "description": description, "formatAttributes": [], "pictureSize": []}, "noValue": []}}}

def creer_playlist(nom, description, h):
    r = appel("POST", SP + "/playlist/v2/playlist", {"ops": [attributs(nom, description)]}, h)
    uri = r.get("uri") or r.get("playlistUri")
    if not uri: raise SystemExit("création sans uri : " + json.dumps(r)[:300])
    return uri

def rootlist_ajout(user, uri, h):
    body = {"deltas": [{"ops": [{"kind": 2, "add": {"items": [{"uri": uri, "attributes": {"timestamp": str(int(time.time() * 1000)), "formatAttributes": [], "availableSignals": []}}], "addFirst": True}}],
                        "info": {"source": {"client": 5}}}], "wantResultingRevisions": False, "wantSyncResult": False, "nonces": []}
    return appel("POST", SP + f"/playlist/v2/user/{urllib.parse.quote(user)}/rootlist/changes", body, h)

def changes(pid, ops, h):
    body = {"deltas": [{"ops": ops, "info": {"source": {"client": 5}}}], "wantResultingRevisions": False, "wantSyncResult": False, "nonces": []}
    return appel("POST", SP + f"/playlist/v2/playlist/{pid}/changes", body, h)

def ajouter(pid, uris, h):
    for i in range(0, len(uris), 100):
        changes(pid, [{"kind": 2, "add": {"items": [{"uri": u, "attributes": {"timestamp": str(int(time.time() * 1000)), "formatAttributes": [], "availableSignals": []}} for u in uris[i:i+100]], "addLast": True}}], h)
        time.sleep(0.5)

def lire(pid, h):
    return appel("GET", SP + f"/playlist/v2/playlist/{pid}?decorate=revision%2Clength%2Cattributes%2Ctimestamp%2Cowner", None, h)

if __name__ == "__main__":
    h = entetes()
    user, nom = username(); print("compte :", nom, "|", user)
    if "--test" in sys.argv:
        p = json.load(open("playlists.json"))[0]
        uri = creer_playlist(p["nom"], "essai de création, sera remplie dans la foulée", h); pid = uri.split(":")[-1]
        print("créée :", uri)
        rootlist_ajout(user, uri, h); print("rootlist : ok")
        ajouter(pid, [t["uri"] for t in p["titres"][:5]], h); print("ajout 5 : ok")
        r = lire(pid, h); print("relecture :", r.get("length"), "titres, nom", (r.get("attributes") or {}).get("name"))
        json.dump({p["cle"]: {"id": pid, "url": "https://open.spotify.com/playlist/" + pid, "nom": p["nom"]}}, open("liens.json", "w"), ensure_ascii=False, indent=1)
