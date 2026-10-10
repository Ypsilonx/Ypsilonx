# Generátor profilu

Profil (`README.md` v angličtině, `README.cs.md` v češtině) a veškerá grafika v `assets/`
se generují skriptem `profile_gen` v GitHub Action. Nepoužívá žádné externí služby ani
závislosti mimo standardní knihovnu Pythonu.

## Co se kde upravuje

| Chci změnit…                         | Soubor                                  |
|--------------------------------------|-----------------------------------------|
| texty profilu                        | `templates/README.en.md`, `templates/README.cs.md` |
| technologie, kontakty, podpora, řádky hlavičky | `profile_gen/config.py`        |
| výchozí jazyk profilu                | `DEFAULT_LANG` v `profile_gen/config.py` |
| popisky karet a tabulky              | `profile_gen/i18n.py`                   |
| barvy (světlý/tmavý režim)           | `profile_gen/svg/theme.py`              |

`README.md`, `README.cs.md` a `assets/` **needituj ručně** – při dalším běhu se přepíšou.

## Značky v šablonách

| Značka                                | Výsledek                                         |
|---------------------------------------|--------------------------------------------------|
| `{{switch}}`                          | přepínač jazyků                                  |
| `{{repos}}`                           | tabulka naposledy aktivních repozitářů           |
| `{{contacts}}`                        | kontaktní odznaky s odkazy                       |
| `{{support}}`                         | odznak s odkazem na podporu (Buy me a coffee)    |
| `{{picture:<asset>\|<alt>[\|<šířka>]}}` | obrázek s variantou pro světlý a tmavý režim     |

Dostupné obrázky: `header`, `tech`, `stats`, `languages`, `activity` (jazykové verze),
`divider`, `contact-<klíč>`, `support-<klíč>` (společné). Neznámá značka ukončí generování chybou.

## Struktura balíčku

```
profile_gen/
  __main__.py    orchestrace: stažení dat → sestavení → zápis změněných souborů
  config.py      ručně udržovaná data profilu
  i18n.py        překlady, formát čísel a dat
  github_api.py  GraphQL klient (urllib), stažení repozitářů, kalendáře a commitů
  models.py      datové třídy
  stats.py       čisté výpočty (série, jazyky, týdenní součty)
  markdown.py    tabulka repozitářů, <picture>, přepínač jazyků
  readme.py      vykreslení šablon
  build.py       sestavení všech výstupů bez síťové komunikace
  svg/           hlavička, karty, odznaky, sparkline, oddělovač, palety
tests/           unittest testy nad ukázkovými daty
```

## Token

Workflow používá automatický `GITHUB_TOKEN`. Pokud by GraphQL dotaz na kalendář
příspěvků s ním selhal, nebo chceš započítat i příspěvky do soukromých repozitářů:

1. Vytvoř *fine-grained personal access token* (Settings → Developer settings) s přístupem
   jen ke čtení veřejných repozitářů.
2. Ulož ho jako secret `PROFILE_TOKEN` v nastavení tohoto repozitáře. Workflow ho použije přednostně.

## Lokální spuštění

```bash
python -m unittest discover -s tests -t .                 # testy
GITHUB_TOKEN=<token> python -m profile_gen                # vygeneruje profil
```
