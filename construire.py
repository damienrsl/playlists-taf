"""Construit les 7 listes de titres (playlists.json) depuis des playlists publiques de référence + recherches d'artistes."""
import json, random, time, sys
import spot

PREFIXE = "TAF · "
random.seed(21112026)

def sources_embed(ids):
    out = []
    for pid in ids:
        try:
            name, tr = spot.playlist_tracks_embed(pid)
            print(f"  source {pid} « {name} » : {len(tr)} titres", file=sys.stderr)
            out.append((name, tr))
        except Exception as e:
            print(f"  source {pid} : ERREUR {e}", file=sys.stderr)
        time.sleep(0.6)
    return out

def recherche_artistes(artistes, par_artiste=6):
    out = []
    for a in artistes:
        try:
            r = spot.search(f'artist:"{a}"', "track", 20)
            items = [t for t in r["tracks"]["items"] if not t.get("explicit")]
            # titres les moins « tubes » mais pas confidentiels : popularité moyenne
            items.sort(key=lambda t: -t.get("popularity", 0))
            items = items[2:2 + par_artiste] if len(items) > par_artiste + 2 else items[:par_artiste]
            tr = [{"uri": t["uri"], "name": t["name"], "artist": ", ".join(x["name"] for x in t["artists"]),
                   "duration_ms": t["duration_ms"], "explicit": t.get("explicit", False)} for t in items]
            print(f"  artiste {a} : {len(tr)}", file=sys.stderr)
            out.append((a, tr))
        except Exception as e:
            print(f"  artiste {a} : ERREUR {e}", file=sys.stderr)
        time.sleep(0.4)
    return out

def assembler(sources, cible_min, dmin=90, dmax=12*60, max_par_artiste=3, exclure_mots=()):
    """Tourniquet entre les sources, filtres, dédoublonnage, plafond par artiste, jusqu'à cible_min minutes."""
    piles = [list(tr) for _, tr in sources if tr]
    for p in piles: random.shuffle(p)
    vus, par_artiste, out, total = set(), {}, [], 0
    while piles and total < cible_min * 60 * 1000:
        for p in list(piles):
            if not p:
                piles.remove(p); continue
            t = p.pop()
            if not t.get("uri") or not t["uri"].startswith("spotify:track:"): continue
            if t.get("explicit"): continue
            d = t.get("duration_ms") or 0
            if d < dmin * 1000 or d > dmax * 1000: continue
            cle = (t["name"].lower().strip(), t["artist"].lower().split(",")[0].strip())
            if cle in vus: continue
            nom = t["name"].lower()
            if any(m in nom for m in exclure_mots): continue
            art = cle[1]
            if par_artiste.get(art, 0) >= max_par_artiste: continue
            vus.add(cle); par_artiste[art] = par_artiste.get(art, 0) + 1
            out.append(t); total += d
            if total >= cible_min * 60 * 1000: break
    return out, total

PLANS = [
    dict(cle="classique", nom="Classique", son="Baroque et musique de chambre, cordes et clavecin, sans voix",
         pourquoi="Tempo stable, pas de paroles : le choix classique des bibliothèques. L'« effet Mozart » est un mythe, mais la régularité du baroque reste un bon fond.",
         embeds=["37i9dQZF1DWXjj6kdiviS0", "0QknRAZUpwPtM2dQIzAnAa"],
         artistes=["Johann Sebastian Bach", "Antonio Vivaldi", "Arcangelo Corelli", "Georg Philipp Telemann", "Erik Satie", "Claude Debussy"],
         cible=160, exclure=("aria", "cantata", "chorus", "choir", "ave maria", "magnificat", "stabat")),
    dict(cle="piano", nom="Piano", son="Piano solo contemporain (Nils Frahm, Ólafur Arnalds, Hania Rani), lent et doux",
         pourquoi="Un seul instrument, peu de variations : le fond le plus neutre pour lire et écrire.",
         embeds=["37i9dQZF1DX4sWSpwq3LiO"],
         artistes=["Nils Frahm", "Ólafur Arnalds", "Hania Rani", "Max Richter", "Joep Beving", "Dustin O'Halloran"],
         cible=160),
    dict(cle="jazz", nom="Jazz", son="Jazz instrumental, trios piano et nu-jazz feutré, sans chant",
         pourquoi="Rythme régulier et chaleur, assez de vie pour ne pas s'endormir. Instrumental seulement : les voix coûtent de l'attention.",
         embeds=["37i9dQZF1DX0SM0LYsmbMT", "37i9dQZF1DWVqfgj8NZEp1"],
         artistes=["Bill Evans", "Ahmad Jamal", "Tord Gustavsen Trio", "GoGo Penguin", "Mammal Hands", "Brad Mehldau", "Esbjörn Svensson Trio"],
         cible=160, exclure=("vocal", "feat.", "sings")),
    dict(cle="lofi", nom="Lofi", son="Lofi hip-hop : beats lents, boucles, souffle de vinyle",
         pourquoi="Le son des « study with me ». Stimulation douce et répétitive, utile sur les tâches répétitives. Peu de preuves, beaucoup d'adeptes.",
         embeds=["37i9dQZF1DWWQRwui0ExPn"],
         artistes=["Nujabes", "Idealism", "Tomppabeats", "jinsang", "Kupla", "Aso"],
         cible=160),
    dict(cle="ambient", nom="Ambient", son="Nappes et drones (Brian Eno, Stars of the Lid, Hammock), presque sans rythme",
         pourquoi="Quasi aucune variation ni mélodie à suivre : le cerveau n'a rien à attraper. Le plus proche d'un bruit, en musical.",
         embeds=["37i9dQZF1DWZeKCadgRdKQ", "37i9dQZF1DX3Ogo9pFvBkY", "4iGAttKqCR2Jg9kl2cUiBq"],
         artistes=["Brian Eno", "Stars of the Lid", "Hammock", "Biosphere", "Harold Budd", "36"],
         cible=170, dmax=20*60),
    dict(cle="bruit", nom="Bruits sourds", son="Bruit brun et bruit rose en continu, pas de musique",
         pourquoi="Le seul type de son avec une preuve chez les profils TDAH : bruit blanc/rose = petit gain mesuré (13 études, 2024). Hors TDAH, ça gêne plutôt.",
         embeds=["37i9dQZF1DX4hpot8sYudB"],
         artistes=[], recherches=["brown noise", "deep brown noise", "pink noise", "brown noise sleep focus"],
         cible=200, dmin=120, dmax=60*60, max_par_artiste=6, exclure=("rain", "white noise", "fan", "ocean", "wave")),
    dict(cle="jeux", nom="Jeux vidéo", son="Bandes originales calmes de jeux (Minecraft, Journey, Stardew Valley…)",
         pourquoi="Écrite pour tenir l'attention des heures sans jamais la voler : c'est leur cahier des charges.",
         embeds=["7yS1SKPgJphkjP3kEpzgCg", "6AMLo7m6b3eTbv11buZNaM", "37i9dQZF1DXdfOcg1fm0VG"],
         artistes=["C418", "Austin Wintory", "Disasterpeace", "ConcernedApe", "Jeremy Soule", "Darren Korb"],
         cible=160, exclure=("battle", "boss", "fight")),
]

def recherche_mots(mots, par_mot=15):
    out = []
    for m in mots:
        try:
            r = spot.search(m, "track", 30)
            items = [t for t in r["tracks"]["items"] if not t.get("explicit")]
            items.sort(key=lambda t: -(t["duration_ms"]))  # les plus longs d'abord
            tr = [{"uri": t["uri"], "name": t["name"], "artist": ", ".join(x["name"] for x in t["artists"]),
                   "duration_ms": t["duration_ms"], "explicit": False} for t in items[:par_mot]]
            print(f"  mot « {m} » : {len(tr)}", file=sys.stderr)
            out.append((m, tr))
        except Exception as e:
            print(f"  mot « {m} » : ERREUR {e}", file=sys.stderr)
        time.sleep(0.4)
    return out

resultat = []
for p in PLANS:
    print(f"== {PREFIXE}{p['nom']}", file=sys.stderr)
    src = sources_embed(p["embeds"])
    if p.get("artistes"): src += recherche_artistes(p["artistes"])
    if p.get("recherches"): src += recherche_mots(p["recherches"])
    titres, total = assembler(src, p["cible"], dmin=p.get("dmin", 90), dmax=p.get("dmax", 12*60),
                              max_par_artiste=p.get("max_par_artiste", 3), exclure_mots=p.get("exclure", ()))
    print(f"  → {len(titres)} titres, {total/60000:.0f} min", file=sys.stderr)
    resultat.append({"cle": p["cle"], "nom": PREFIXE + p["nom"], "son": p["son"], "pourquoi": p["pourquoi"],
                     "sources": p["embeds"], "duree_min": round(total / 60000), "titres": titres})

json.dump(resultat, open("playlists.json", "w"), ensure_ascii=False, indent=1)
print(json.dumps([{"nom": r["nom"], "n": len(r["titres"]), "min": r["duree_min"]} for r in resultat], ensure_ascii=False))
