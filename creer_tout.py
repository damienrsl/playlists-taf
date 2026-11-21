"""Crée (ou complète) les 7 playlists TAF dans le Spotify de Damien via spclient, écrit liens.json, relit chaque playlist."""
import json, time, pathlib
import spclient
ICI = pathlib.Path(__file__).parent
h = spclient.entetes()
user, nom_compte = spclient.username(); print("compte :", nom_compte)
P = json.load(open(ICI / "playlists.json"))
lp = ICI / "liens.json"; L = json.load(open(lp)) if lp.exists() else {}
for p in P:
    uris = [t["uri"] for t in p["titres"]]
    desc = (p["son"] + ". Concentration, sans paroles, " + f"{p['duree_min'] // 60} h {p['duree_min'] % 60:02d}. Construite le 21/11/2026.")[:300]
    if p["cle"] in L:
        pid = L[p["cle"]]["id"]
        deja = spclient.lire(pid, h).get("length", 0)
        spclient.changes(pid, [spclient.attributs(p["nom"], desc)], h)
        if deja < len(uris): spclient.ajouter(pid, uris[deja:], h)
        print("complétée :", p["nom"], f"{deja} → {len(uris)}")
    else:
        uri = spclient.creer_playlist(p["nom"], desc, h); pid = uri.split(":")[-1]
        spclient.rootlist_ajout(user, uri, h)
        spclient.ajouter(pid, uris, h)
        L[p["cle"]] = {"id": pid, "url": "https://open.spotify.com/playlist/" + pid, "nom": p["nom"]}
        json.dump(L, open(lp, "w"), ensure_ascii=False, indent=1)
        print("créée :", p["nom"], len(uris), L[p["cle"]]["url"])
    time.sleep(0.8)
print("--- relecture")
ok = True
for p in P:
    r = spclient.lire(L[p["cle"]]["id"], h); n = r.get("length"); a = (r.get("attributes") or {})
    bon = n == len(p["titres"]) and a.get("name") == p["nom"]
    ok &= bon
    print(("ok " if bon else "ÉCART ") + f"{a.get('name')} : {n}/{len(p['titres'])} titres")
print("TOUT OK" if ok else "ÉCARTS")
