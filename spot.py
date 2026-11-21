"""Accès Spotify public (jeton anonyme de la page embed) : lecture de playlists, recherche. Stdlib seule."""
import json, re, sys, time, urllib.request, urllib.parse

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15"
_tok = {"v": None, "exp": 0}

def _get(url, headers=None, timeout=20):
    req = urllib.request.Request(url, headers={"User-Agent": UA, **(headers or {})})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()

def embed(kind, sid):
    """Page embed → NEXT_DATA (entity + accessToken)."""
    h = _get(f"https://open.spotify.com/embed/{kind}/{sid}").decode("utf-8", "ignore")
    m = re.search(r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>', h, re.S)
    if not m:
        raise RuntimeError("embed sans NEXT_DATA")
    return json.loads(m.group(1))

def _find(o, k):
    if isinstance(o, dict):
        if k in o: return o[k]
        for v in o.values():
            r = _find(v, k)
            if r is not None: return r
    elif isinstance(o, list):
        for v in o:
            r = _find(v, k)
            if r is not None: return r
    return None

def token():
    if _tok["v"] and time.time() < _tok["exp"] - 60:
        return _tok["v"]
    d = embed("playlist", "37i9dQZF1DX4sWSpwq3LiO")
    t = _find(d, "accessToken"); exp = _find(d, "accessTokenExpirationTimestampMs") or 0
    _tok["v"], _tok["exp"] = t, (exp / 1000 if exp else time.time() + 1800)
    return t

def api(path, params=None, retries=3):
    url = "https://api.spotify.com/v1" + path + (("?" + urllib.parse.urlencode(params)) if params else "")
    for i in range(retries):
        try:
            return json.loads(_get(url, {"Authorization": "Bearer " + token()}))
        except urllib.error.HTTPError as e:
            if e.code == 429:
                time.sleep(int(e.headers.get("Retry-After", "2")) + 1); continue
            if e.code == 401:
                _tok["v"] = None; continue
            raise
    raise RuntimeError("api: échec " + path)

def playlist_tracks_embed(pid):
    """Jusqu'à 100 titres via la page embed (marche pour les playlists éditoriales)."""
    d = embed("playlist", pid)
    ent = _find(d, "entity") or {}
    out = []
    for t in ent.get("trackList", []):
        out.append({"uri": t.get("uri"), "name": t.get("title"), "artist": t.get("subtitle"),
                    "duration_ms": t.get("duration"), "explicit": t.get("isExplicit", False)})
    return ent.get("name"), out

def playlist_tracks_api(pid, limit=200):
    out, off = [], 0
    while off < limit:
        d = api(f"/playlists/{pid}/tracks", {"limit": 100, "offset": off, "fields": "items(track(uri,name,duration_ms,explicit,popularity,artists(name,id))),next"})
        for it in d.get("items", []):
            t = it.get("track") or {}
            if not t.get("uri"): continue
            out.append({"uri": t["uri"], "name": t["name"], "artist": ", ".join(a["name"] for a in t.get("artists", [])),
                        "artist_ids": [a["id"] for a in t.get("artists", [])], "duration_ms": t.get("duration_ms"),
                        "explicit": t.get("explicit"), "popularity": t.get("popularity")})
        if not d.get("next"): break
        off += 100
    return out

def search(q, kind="track", limit=20, market="FR"):
    return api("/search", {"q": q, "type": kind, "limit": limit, "market": market})

if __name__ == "__main__":
    print("jeton:", token()[:10] + "…")
    name, tr = playlist_tracks_embed("37i9dQZF1DX4sWSpwq3LiO")
    print("embed:", name, len(tr), tr[0] if tr else None)
    try:
        tr2 = playlist_tracks_api("37i9dQZF1DX4sWSpwq3LiO", 100)
        print("api playlist éditoriale:", len(tr2), tr2[0] if tr2 else None)
    except Exception as e:
        print("api playlist éditoriale: ERREUR", str(e)[:120])
    try:
        s = search("artist:Nils Frahm", "track", 5)
        print("api search:", [t["name"] for t in s["tracks"]["items"]])
    except Exception as e:
        print("api search: ERREUR", str(e)[:120])
    try:
        tr3 = playlist_tracks_api("7eUSan9utyV6rNcnmy5f8f", 100)
        print("api playlist perso:", len(tr3))
    except Exception as e:
        print("api playlist perso: ERREUR", str(e)[:120])
