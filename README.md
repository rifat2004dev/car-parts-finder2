# Western Cape Car Parts Finder

This version keeps the working scraper structure from the stronger build, but the app interface is simpler.

## Sources included
- Gumtree
- Facebook Marketplace
- Modern Auto Parts
- Berlin Car Parts
- Online Car Parts
- Takealot
- AutoZone Online
- Midas
- Masterparts
- Boss Auto Spares
- Atlantic Auto Spares

## Run it in VS Code

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
streamlit run app.py
```

## Notes
- Gumtree is usually the strongest source.
- Facebook Marketplace is best-effort and may return zero if Facebook blocks the session.
- The other sources use the same scraper logic from the previous working build.
- If a website changes its HTML, only that source file usually needs a small update.
