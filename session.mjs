// Ouvre le lecteur web Spotify SANS fenêtre (Chrome headless, profil jetable) avec le cookie sp_dc de Damien,
// capture les en-têtes d'une requête authentifiée du lecteur et les écrit dans ~/.config/damienprime/spotify/entetes.json (0600).
import { createRequire } from 'module';
import fs from 'fs';
import os from 'os';
import path from 'path';
const require = createRequire('/Users/damienroussel/.npm/_npx/e41f203b7505f1fb/node_modules/');
const { chromium } = require('playwright-core');
const dir = path.join(os.homedir(), '.config/damienprime/spotify');
const spdc = fs.readFileSync(path.join(dir, 'sp_dc'), 'utf8').trim();
const UA = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36';
const b = await chromium.launch({ executablePath: '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', headless: true, args: ['--disable-gpu', '--no-first-run'] });
const fin = async (code, msg) => { console.log(msg); await b.close().catch(() => {}); process.exit(code); };
setTimeout(() => fin(2, 'ERREUR délai 60 s sans en-têtes'), 60000);
try {
  const ctx = await b.newContext({ userAgent: UA, locale: 'fr-FR', viewport: { width: 1280, height: 800 } });
  await ctx.addCookies([{ name: 'sp_dc', value: spdc, domain: '.spotify.com', path: '/', httpOnly: true, secure: true, sameSite: 'Lax' }]);
  const page = await ctx.newPage();
  let entetes = null;
  page.on('request', r => {
    const u = r.url(); const h = r.headers();
    if (!entetes && h['authorization'] && h['authorization'].startsWith('Bearer') && (u.includes('api-partner.spotify.com') || u.includes('spclient.wg.spotify.com') || u.includes('api.spotify.com'))) {
      entetes = { authorization: h['authorization'], 'client-token': h['client-token'] || '', 'spotify-app-version': h['spotify-app-version'] || '', 'app-platform': h['app-platform'] || 'WebPlayer', 'user-agent': UA, pris: Date.now() };
    }
  });
  await page.goto('https://open.spotify.com/', { waitUntil: 'domcontentloaded' });
  for (let i = 0; i < 50 && !entetes; i++) await page.waitForTimeout(600);
  if (!entetes) await fin(1, 'ERREUR aucune requête authentifiée vue (cookie refusé ?) titre=' + (await page.title()));
  fs.writeFileSync(path.join(dir, 'entetes.json'), JSON.stringify(entetes), { mode: 0o600 });
  await fin(0, 'en-têtes capturés : authorization oui, client-token ' + (entetes['client-token'] ? 'oui' : 'non') + ', version ' + entetes['spotify-app-version']);
} catch (e) { await fin(3, 'ERREUR ' + String(e.message).slice(0, 200)); }
