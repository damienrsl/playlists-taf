"""playlists.json (+ liens.json) → corps.html → index.html (fabrique DA Aura)."""
import json, pathlib, subprocess, html
ICI = pathlib.Path(__file__).parent
P = json.load(open(ICI / "playlists.json"))
liens_p = ICI / "liens.json"; L = json.load(open(liens_p)) if liens_p.exists() else {}
REF = {"classique": ("Baroque Classics", "37i9dQZF1DWXjj6kdiviS0"), "piano": ("Peaceful Piano", "37i9dQZF1DX4sWSpwq3LiO"),
       "jazz": ("Jazz Vibes", "37i9dQZF1DX0SM0LYsmbMT"), "lofi": ("lofi beats", "37i9dQZF1DWWQRwui0ExPn"),
       "ambient": ("Deep Focus", "37i9dQZF1DWZeKCadgRdKQ"), "bruit": ("Brown Noise", "37i9dQZF1DX4hpot8sYudB"),
       "jeux": ("Video Game Study Music", "7yS1SKPgJphkjP3kEpzgCg")}
TEMOIN = {"cle": "flow", "nom": "Fatigue · Flow infini", "son": "Ta playlist actuelle : dark dream pop, slowed + reverb, witch house, avec paroles",
          "pourquoi": "Le témoin. Si rien ne la bat, tu gardes ce que tu as déjà.", "url": "https://open.spotify.com/playlist/7JIvoSwPOF7afre9Ps3RSR"}
dans_spotify = bool(L)
e = html.escape

def carte(p, i):
    cle = p["cle"]
    if cle in L: url, legende = L[cle]["url"], "Dans ton Spotify"
    elif cle == "flow": url, legende = p["url"], "Dans ton Spotify"
    else:
        nom_ref, pid = REF[cle]; url = f"https://open.spotify.com/playlist/{pid}"
        legende = f"En attendant la tienne : « {nom_ref} » (Spotify)"
    chiffres = ""
    if "titres" in p:
        chiffres = f'<p class="meta">{len(p["titres"])} titres · {p["duree_min"] // 60} h {p["duree_min"] % 60:02d}</p>'
    return f'''
    <div class="verre carte pl" data-cle="{cle}" data-nom="{e(p["nom"])}">
      <span class="num">{i:02d}</span>
      <h2>{e(p["nom"])}</h2>
      <p class="son">{e(p["son"])}</p>
      <div class="franc">{e(p["pourquoi"])}</div>
      {chiffres}
      <a class="bouton" href="{url}" target="_blank" rel="noopener">Écouter</a>
      <span class="legende">{e(legende)}</span>
      <div class="notes" aria-label="Note cette session">
        <span class="q">Après la session, ça t'a mis dans ta bulle ?</span>
        <div class="puces">{''.join(f'<button class="puce" data-n="{n}">{n}</button>' for n in range(1, 6))}</div>
        <span class="bilan"></span>
      </div>
    </div>'''

cartes = "".join(carte(p, i + 1) for i, p in enumerate(P)) + carte(TEMOIN, len(P) + 1)
etat = ("Les 7 playlists sont dans ton Spotify, préfixe « TAF »." if dans_spotify
        else "Les 7 listes sont prêtes (titres choisis, durées calées). Elles arrivent dans ton Spotify dès que j'ai l'accès ; en attendant chaque bouton ouvre la playlist publique la plus proche.")

corps = f'''<!doctype html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>TAF · les playlists de concentration</title>
<style>
/*KIT*/
main{{max-width:640px;margin:0 auto;position:relative;z-index:1;padding:0 16px 60px}}
.hero{{padding:60px 4px 26px;position:relative}}
.hero .orbe{{--d:70px;position:absolute;right:6px;top:44px;animation:souffle 6s ease-in-out infinite}}
@keyframes souffle{{0%,100%{{transform:scale(1)}}50%{{transform:scale(1.08)}}}}
.hero h1{{font-size:34px;line-height:1.08;letter-spacing:-.03em;max-width:14ch}}
.hero p{{margin:16px 0 0;font-size:17px;line-height:1.5;max-width:40ch;color:var(--texte-2)}}
.hero p b,.carte p b,.franc b{{color:var(--texte)}}
section{{margin:34px 0}}
section>.etiquette{{display:block;margin:0 4px 10px}}
.carte{{padding:20px;margin-bottom:12px;position:relative}}
.carte h2{{font-size:24px;letter-spacing:-.02em;line-height:1.15;margin-top:6px}}
.carte>p{{margin:10px 0 0;line-height:1.55;color:var(--texte-2)}}
.num{{font:600 12px var(--police-mono);color:var(--pan-3);letter-spacing:.06em}}
.franc{{border-left:2px solid var(--pan-2);padding:12px 16px;margin:14px 0 0;color:var(--texte-2);font-size:16px;line-height:1.5;border-radius:0 var(--r-m) var(--r-m) 0;background:rgba(40,95,255,.06)}}
.meta{{font:600 13px var(--police-mono);letter-spacing:.06em;text-transform:uppercase;color:var(--texte-3)}}
.bouton{{display:inline-block;margin:14px 0 0;background:linear-gradient(135deg,var(--bleu-chat),var(--bleu-renard));color:#fff;text-decoration:none;font:600 16px var(--police);padding:12px 22px;border-radius:var(--r-pilule);box-shadow:0 8px 20px -8px rgba(36,54,184,.6)}}
.legende{{display:block;margin-top:8px;font-size:14px;color:var(--texte-3)}}
.notes{{margin-top:16px;padding-top:14px;border-top:1px solid var(--filet)}}
.notes .q{{display:block;font-size:15px;color:var(--texte-2)}}
.puces{{display:flex;gap:8px;margin:10px 0 0}}
.puce{{flex:1;background:rgba(255,255,255,.7);border:1px solid var(--filet);color:var(--texte-2);font:600 17px var(--police);padding:10px 0;border-radius:var(--r-pilule);cursor:pointer;transition:all .3s var(--ressort)}}
.puce.on{{color:#fff;border-color:transparent;background:linear-gradient(135deg,var(--bleu-chat),var(--bleu-renard));transform:scale(1.06)}}
.bilan{{display:block;margin-top:10px;font-size:14px;color:var(--texte-3);min-height:18px}}
.etapes .spec{{padding:12px 0;border-top:1px solid var(--filet)}}
.etapes .spec:first-of-type{{border-top:0;padding-top:0}}
.spec h3{{font-size:18px;margin-top:4px}}
.spec p{{margin:6px 0 0;font-size:16px;line-height:1.5;color:var(--texte-2)}}
.suivant{{font-family:var(--large);font-size:22px;letter-spacing:-.02em;line-height:1.3;margin:0}}
.suivant b{{color:var(--pan-3);font-weight:600}}
.classement{{margin:12px 0 0;padding:0;list-style:none}}
.classement li{{display:grid;grid-template-columns:1fr auto;gap:12px;padding:10px 0;border-top:1px solid var(--filet);font-size:16px;color:var(--texte-2)}}
.classement li:first-child{{border-top:0}}
.classement li b{{color:var(--texte)}}
.classement .moy{{font:600 18px var(--police-mono);color:var(--pan-3)}}
.classement .barre{{grid-column:1/-1;height:6px;border-radius:3px;background:rgba(36,54,184,.1);overflow:hidden}}
.classement .barre i{{display:block;height:100%;background:linear-gradient(90deg,var(--bleu-chat),var(--bleu-renard));transition:width 1s var(--ressort)}}
.copier{{margin-top:14px;background:none;border:1px solid var(--filet);color:var(--pan-3);font:600 15px var(--police);padding:10px 18px;border-radius:var(--r-pilule);cursor:pointer}}
.vide{{font-size:16px;color:var(--texte-3);margin:10px 0 0}}
.chiffre{{display:flex;gap:14px;align-items:baseline;padding:12px 0;border-top:1px solid var(--filet)}}
.chiffre:first-of-type{{border-top:0;padding-top:2px}}
.chiffre .gros{{font-family:var(--large);font-size:28px;letter-spacing:-.03em;color:var(--pan-3);min-width:96px;line-height:1}}
.chiffre p{{margin:0;font-size:16px;line-height:1.45;color:var(--texte-2)}}
.chiffre p b{{color:var(--texte)}}
.chiffre a{{color:var(--pan-3)}}
.pied{{font-size:14px;color:var(--texte-3);line-height:1.5;margin:40px 4px 0}}
</style>
</head>
<body>
<main>
  <header class="hero">
    <span class="orbe"></span>
    <span class="etiquette">TAF · playlists de concentration · 21/11</span>
    <h1>Sept sons. Un seul te mettra dans ta bulle.</h1>
    <p>Une playlist par session de travail, une note en sortant. <b>En deux semaines tu sais quel son te fait démarrer</b>, et tu arrêtes de choisir.</p>
  </header>

  <section>
    <span class="etiquette">Le test · 3 gestes</span>
    <div class="verre carte etapes">
      <p class="suivant" id="suivant">À tester maintenant : <b>TAF · Classique</b></p>
      <div class="spec"><span class="num">01</span><h3>Lance la playlist du jour, et seulement elle</h3><p>Volume moyen, fondu Spotify à 6 s (Réglages → Lecture → Fondu enchaîné). Pas de saut de titre : le choix casse la bulle.</p></div>
      <div class="spec"><span class="num">02</span><h3>Travaille 45 minutes</h3><p>Même tâche de fond que d'habitude. Le son change, le reste non : sinon on ne sait pas ce qu'on mesure.</p></div>
      <div class="spec"><span class="num">03</span><h3>Note de 1 à 5 sous la carte</h3><p>1 = tu as décroché tout le temps, 5 = tu as oublié la musique. La page te dit ensuite quoi tester, puis quel son gagne.</p></div>
      <div class="franc">{e(etat)}</div>
    </div>
  </section>

  <section>
    <span class="etiquette">Les 7 sons · et ton témoin</span>
    {cartes}
  </section>

  <section>
    <span class="etiquette">Ce qui marche pour toi</span>
    <div class="verre carte">
      <h2>Ton classement</h2>
      <ul class="classement" id="classement"></ul>
      <p class="vide" id="vide">Pas encore de note. Après ta première session, ton classement apparaît ici.</p>
      <button class="copier" id="copier">Copier le bilan pour Claude</button>
      <span class="bilan" id="copie"></span>
    </div>
  </section>

  <section>
    <span class="etiquette">Ce que disent les études</span>
    <div class="verre carte">
      <div class="chiffre"><span class="gros">−0,3</span><p><b>Les paroles coûtent.</b> Musique avec voix pendant une tâche de lecture ou d'écriture : mémoire et compréhension baissent (méta-analyse 2023, <a href="https://pmc.ncbi.nlm.nih.gov/articles/PMC10162369/" target="_blank" rel="noopener">Souza &amp; Barbosa</a>). L'instrumental n'aide ni ne gêne en moyenne.</p></div>
      <div class="chiffre"><span class="gros">+0,25</span><p><b>Le bruit aide les profils TDAH.</b> Bruit blanc ou rose : petit gain mesuré sur 13 études, 335 personnes (<a href="https://pubmed.ncbi.nlm.nih.gov/38428577/" target="_blank" rel="noopener">Nigg 2024</a>). Chez les autres, c'est l'inverse. D'où la playlist « Bruits sourds ».</p></div>
      <div class="chiffre"><span class="gros">Mythe</span><p><b>L'« effet Mozart » n'existe pas.</b> 39 études, effet quasi nul hors des labos d'origine (<a href="https://www.ncbi.nlm.nih.gov/pmc/articles/PMC9988829/" target="_blank" rel="noopener">méta-analyse 2023</a>). Le classique reste un bon fond, pas une potion.</p></div>
      <div class="chiffre"><span class="gros">Faible</span><p><b>Sons binauraux et 40 Hz : preuves molles.</b> Des effets annoncés (g ≈ 0,4) mais des études petites et contradictoires. Pas de playlist dédiée ; à ajouter si tu veux l'essayer.</p></div>
      <div class="chiffre"><span class="gros">Toi</span><p><b>Ce qui compte le plus : ta préférence et l'habitude.</b> Les études convergent : musique choisie soi-même, familière, sans variations ni surprises. C'est exactement ce que ce test mesure.</p></div>
    </div>
  </section>

  <p class="pied">Listes construites le 21/11/2026 à partir des playlists les plus suivies de chaque genre et de recherches par artiste : sans paroles, titres de 1 min 30 à 12 min (bruits jusqu'à 1 h), 3 titres par artiste au plus, 2 h 40 à 3 h 30 par playlist. Tes notes restent sur cet appareil.</p>
</main>
<script>
(function(){{
  const K='taf-notes';const lire=()=>{{try{{return JSON.parse(localStorage.getItem(K)||'{{}}')}}catch(e){{return {{}}}}}};
  const ecrire=d=>localStorage.setItem(K,JSON.stringify(d));
  const cartes=[...document.querySelectorAll('.pl')];
  function moy(a){{return a.length?a.reduce((s,x)=>s+x.n,0)/a.length:0}}
  function maj(){{
    const d=lire();
    cartes.forEach(c=>{{const a=d[c.dataset.cle]||[];const b=c.querySelector('.bilan');
      b.textContent=a.length?`${{a.length}} session${{a.length>1?'s':''}} · moyenne ${{moy(a).toFixed(1).replace('.',',')}}`:'';
      const der=a.length?a[a.length-1].n:0;c.querySelectorAll('.puce').forEach(p=>p.classList.toggle('on',+p.dataset.n===der));}});
    // à tester : la moins notée (hors témoin si déjà 1 note)
    const cand=cartes.map(c=>({{c,n:(d[c.dataset.cle]||[]).length}})).sort((x,y)=>x.n-y.n||cartes.indexOf(x.c)-cartes.indexOf(y.c));
    document.querySelector('#suivant b').textContent=cand[0].c.dataset.nom;
    // classement
    const notes=cartes.map(c=>({{nom:c.dataset.nom,a:d[c.dataset.cle]||[]}})).filter(x=>x.a.length).sort((x,y)=>moy(y.a)-moy(x.a));
    const ul=document.getElementById('classement');ul.innerHTML='';document.getElementById('vide').style.display=notes.length?'none':'';
    notes.forEach(x=>{{const li=document.createElement('li');const m=moy(x.a);
      li.innerHTML=`<span><b>${{x.nom}}</b> · ${{x.a.length}} session${{x.a.length>1?'s':''}}</span><span class="moy">${{m.toFixed(1).replace('.',',')}}</span><span class="barre"><i style="width:${{m/5*100}}%"></i></span>`;ul.appendChild(li)}});
  }}
  cartes.forEach(c=>c.querySelectorAll('.puce').forEach(p=>p.addEventListener('click',()=>{{
    const d=lire();(d[c.dataset.cle]=d[c.dataset.cle]||[]).push({{n:+p.dataset.n,t:Date.now()}});ecrire(d);maj();}})));
  document.getElementById('copier').addEventListener('click',async()=>{{
    const d=lire();const lignes=cartes.map(c=>({{nom:c.dataset.nom,a:d[c.dataset.cle]||[]}})).filter(x=>x.a.length).sort((x,y)=>moy(y.a)-moy(x.a))
      .map(x=>`${{x.nom}} : ${{moy(x.a).toFixed(1)}} sur ${{x.a.length}} session(s)`);
    const txt=lignes.length?'Bilan playlists TAF :\\n'+lignes.join('\\n'):'Bilan playlists TAF : aucune note encore.';
    try{{await navigator.clipboard.writeText(txt);document.getElementById('copie').textContent='Copié. Colle-le dans Tokn.'}}catch(e){{document.getElementById('copie').textContent=txt}}
  }});
  maj();
}})();
</script>
</body>
</html>'''
(ICI / "corps.html").write_text(corps)
print(subprocess.run(["python3", str(pathlib.Path.home() / "Documents/design-system-damien/fabrique-artefact.py"), str(ICI / "corps.html")], capture_output=True, text=True).stdout.strip())
