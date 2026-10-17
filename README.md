# REGAL BANDIT POPSTAR

An 8-bit Cleveland pull-over. A Sicilian popstar in an orange headband and a bandit eye mask, guitar on his back, drives a white Buick Regal at 2 AM, smoking and sipping a tall boy. The cops light him up. Snitch on Lukey? Blame Tom B? Keep the code? 15 endings.

Flask serves one HTML page. The game runs in the browser and works on phones. Flask also keeps a global "what % of players got this ending" counter.

```
app.py              Flask server (page + tiny stats API)
index.html          the whole game (canvas pixel art, chiptune audio, story)
og.png              link-preview image shown when you text the URL
requirements.txt    Flask + gunicorn
render.yaml         one-click Render blueprint
Procfile            for Heroku-style hosts
```

## Run it locally

```bash
pip install -r requirements.txt
python app.py          # http://localhost:5000
```

## Host it free, option A: Render (recommended)

1. Put this folder in a GitHub repo (github.com > New repository > upload the files).
2. render.com > sign up with GitHub > **New +** > **Blueprint** > pick the repo. (Or **New Web Service**, runtime Python, build `pip install -r requirements.txt`, start `gunicorn app:app --workers 1 --threads 4`.)
3. In a couple of minutes you get `https://regal-bandit-popstar.onrender.com`. Text that link.

Free-tier facts: the service sleeps after 15 minutes idle and the first visit afterward takes about 30-60 seconds to wake. The ending-percentage counter is kept on a disk that resets on every redeploy or restart, so it starts over. The game itself never depends on it.

Optional: make a free UptimeRobot monitor that pings `/healthz` every 5 minutes so it stays awake.

## Host it free, option B: PythonAnywhere

1. pythonanywhere.com > create a free **Beginner** account.
2. **Web** tab > **Add a new web app** > Flask > Python 3.x.
3. Upload `app.py`, `index.html` and `og.png` into the web app's folder (replace the sample `flask_app.py`, or point the WSGI file at `app`).
4. Hit **Reload**. Your link is `https://YOURNAME.pythonanywhere.com`.

Free-tier facts: it doesn't sleep, but the free web app has to be re-extended every 3 months from the Web tab, and the free plan has one web app only.

## Texting it

Send the link. iMessage and WhatsApp show the preview image (`og.png`) and title. The end screen has a **CHALLENGE A FRIEND** button that opens the phone's share sheet.

## Controls

- Tap or Space/Enter advances dialogue. Number keys or taps pick choices.
- Driving: tap top/bottom of the screen or the arrow buttons (or W/S/arrows) to change lanes. Pierogies and golden picks raise STREET CRED. Potholes and cones hurt.
- Lie detector: tap when the needle is in the green.
- Some choices need enough STREET CRED (e.g. the guitar solo needs 5+), so grab pierogies.

Fiction, for laughs. Don't drink and drive in real life.
