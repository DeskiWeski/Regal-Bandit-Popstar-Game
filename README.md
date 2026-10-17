# CLEVELAND BOY ADVENTURES

An 8-bit Cleveland adventure. A Sicilian popstar in an orange headband and a bandit eye mask, guitar on his back, drives a white Buick Regal at 2 AM. He gets pulled over. Snitch on Lukey? Blame Tom B? Keep the code? Then go home and fight the final boss: nAna.

18 endings, a leaderboard saved to a JSON file, and controls drawn right inside the game screen so nothing gets cut off on a phone (portrait or landscape).

```
index.html          the whole game (pixel art, chiptune audio, story, boss fight)
app.py              Flask server: serves the game + saves the leaderboard to leaderboard.json
og.png              link-preview image shown when you text the URL
requirements.txt    Flask + gunicorn
render.yaml         one-click Render blueprint
Procfile            for Heroku-style hosts
```

`leaderboard.json` is created automatically the first time someone submits a score. It holds the top scores and how many players got each ending. The server recalculates every score itself, so nobody can post a fake one.

## Run it locally

```
pip install -r requirements.txt
python app.py          # http://localhost:5000
```

## Host it free, option A: PythonAnywhere (recommended: shared leaderboard that never sleeps)

1. pythonanywhere.com > create a free **Beginner** account.
2. **Files** tab > open your home folder > make a folder `mysite` > upload `app.py`, `index.html` and `og.png` into it.
3. **Web** tab > **Add a new web app** > **Manual configuration** (or Flask) > Python 3.x.
4. On the Web tab open the **WSGI configuration file**, delete what is there and paste (use your real username):
   ```python
   import sys
   path = '/home/YOURNAME/mysite'
   if path not in sys.path:
       sys.path.insert(0, path)
   from app import app as application
   ```
5. Hit the green **Reload** button. Your link is `https://YOURNAME.pythonanywhere.com`. Scores save to `/home/YOURNAME/mysite/leaderboard.json`.

Free-tier facts: it doesn't sleep, but you must press the **Run until 3 months from today** button on the Web tab every few months or the site is turned off. One web app only.

## Host it free, option B: GitHub Pages (no server)

Put `index.html` and `og.png` in a public GitHub repo and turn on Pages (Settings > Pages > main / root). The game works fully, but there is no server to save a shared leaderboard, so each phone keeps its own scores in a JSON list in its browser.

To share one leaderboard while using Pages, host `app.py` on PythonAnywhere (option A) and, in `index.html`, change the line near the top of the leaderboard section from `const API_BASE='';` to `const API_BASE='https://YOURNAME.pythonanywhere.com';`.

## Host it free, option C: Render

New > Blueprint > pick the repo. The free plan sleeps after 15 idle minutes and its disk resets on every redeploy, so the leaderboard file starts over each time. PythonAnywhere is better for the leaderboard.

## Controls

- Tap or Space/Enter advances dialogue. Number keys or taps pick choices.
- Driving: tap the arrow buttons on the screen, swipe up/down, or tap the top/bottom half of the screen (keyboard: W/S or arrow keys). Pierogies = cred. Potholes and cones hurt.
- Lie detector: tap the button when the needle is in the green.
- Final boss (unlocks after any good ending): arrows move, THROW (Space) throws a beer can when her purse is down, LUKEY (L) blames Lukey for a few seconds of double damage. Weed leaves and cigarettes heal you.

Fiction, for laughs. Don't drink and drive in real life.
