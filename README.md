# Spletni obrazec

Obrazec sprejema ime, priimek in e-pošto.

## GitHub Pages

Stran je v mapi `site/`. Po objavi prek GitHub Pages se vnosi zbirajo samo v odprtem zavihku brskalnika; gumb **Prenesi data.txt** prenese CSV datoteko na napravo. Podatki se ne pošiljajo na GitHub ali drug strežnik.

Delovni tok za objavo je v `.github/workflows/pages.yml`. V repozitoriju odprite **Settings → Pages** in pri **Build and deployment → Source** izberite **GitHub Actions**. Po uspešnem zagonu delovnega toka bo stran na naslovu `https://medvesceke.github.io/codexRepo/`.

## Lokalni strežnik

Python različica shrani poslane vnose kot vrstice CSV v `data.txt` v trenutni delovni mapi:

```bash
python3 app.py
```

Nato odprite <http://127.0.0.1:8000/>. Python 3 uporablja samo standardno knjižnico.
