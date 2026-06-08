#!/usr/bin/env python3
"""
Skript pro automatickou aktualizaci seznamu repozitářů v README.md
"""

import requests
import os
import re
import time
from datetime import datetime

# GitHub API endpoint
GITHUB_API = "https://api.github.com"
USERNAME = "Ypsilonx"
README_PATH = "README.md"

# Počet repozitářů k zobrazení
REPO_COUNT = 6


def get_latest_repos(username, count=6):
    """Získá repozitáře uživatele seřazené dle posledního commitu."""
    url = f"{GITHUB_API}/users/{username}/repos"
    headers = {}
    
    # Použití GITHUB_TOKEN pokud je dostupný
    token = os.environ.get('GITHUB_TOKEN')
    if token:
        headers['Authorization'] = f'token {token}'
    
    params = {
        'sort': 'pushed',       # řadit dle posledního commitu
        'direction': 'desc',
        'per_page': 100,        # stáhneme víc, pak filtrujeme
        'type': 'public'
    }
    
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        repos = response.json()
        
        # Vyřaď profilový repozitář (stejné jméno jako uživatel) a forky
        repos = [
            r for r in repos
            if r['name'].lower() != username.lower() and not r.get('fork')
        ]
        
        return repos[:count]
    except Exception as e:
        print(f"Chyba při získávání repozitářů: {e}")
        return []


def get_code_stats(owner, repo_name, headers):
    """Získá celkové součty přidaných a smazaných řádků přes stats/code_frequency.
    
    GitHub API tuto statistiku počítá asynchronně – při prvním dotazu vrátí 202.
    Funkce opakuje dotaz max. 5× s čekáním, aby data stihla být připravena.
    Vrátí tuple (additions, deletions) nebo None při chybě.
    """
    url = f"{GITHUB_API}/repos/{owner}/{repo_name}/stats/code_frequency"
    for attempt in range(5):
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            if not data:
                return None
            additions = sum(week[1] for week in data)
            deletions = abs(sum(week[2] for week in data))
            return additions, deletions
        if response.status_code == 202:
            # Data se teprve počítají, počkej a zkus znovu
            wait = 5 * (attempt + 1)
            print(f"  [{repo_name}] Stats se počítají, čekám {wait}s...")
            time.sleep(wait)
        else:
            print(f"  [{repo_name}] Nepodařilo se načíst stats: {response.status_code}")
            return None
    print(f"  [{repo_name}] Stats nedostupné ani po opakování, přeskakuji.")
    return None


def format_repo_list(repos, headers):
    """Vytvoří markdown formát pro seznam repozitářů včetně stats."""
    if not repos:
        return "<!-- Zatím žádné veřejné repozitáře -->"
    
    markdown = ""
    for repo in repos:
        name = repo['name']
        description = repo['description'] or "Bez popisu"
        url = repo['html_url']
        language = repo['language'] or "N/A"
        pushed = datetime.strptime(repo['pushed_at'], '%Y-%m-%dT%H:%M:%SZ')
        pushed_str = pushed.strftime('%d.%m.%Y')
        
        # Emoji pro jazyky
        lang_emoji = {
            'Python': '🐍',
            'JavaScript': '📜',
            'TypeScript': '💙',
            'C#': '💜',
            'C++': '⚡',
            'Rust': '🦀',
            'HTML': '🌐',
            'CSS': '🎨',
            'Java': '☕',
            'Go': '🔵',
        }
        emoji = lang_emoji.get(language, '📁')
        
        print(f"  Načítám stats pro {name}...")
        stats = get_code_stats(USERNAME, name, headers)
        
        markdown += f"### {emoji} [{name}]({url})\n"
        markdown += f"**{description}**\n\n"
        markdown += f"- 💻 Jazyk: `{language}`\n"
        markdown += f"- 📅 Poslední commit: {pushed_str}\n"
        if stats:
            additions, deletions = stats
            markdown += f"- 📈 Celkem: +{additions:,} / -{deletions:,} řádků\n"
        markdown += "\n---\n\n"
    
    return markdown.strip()


def update_readme(repo_list_markdown):
    """Aktualizuje README.md se seznamem repozitářů."""
    try:
        with open(README_PATH, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Najdi sekci mezi komentáři
        pattern = r'<!-- REPO-LIST:START -->.*?<!-- REPO-LIST:END -->'
        replacement = f'<!-- REPO-LIST:START -->\n\n{repo_list_markdown}\n\n<!-- REPO-LIST:END -->'
        
        new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)
        
        # Pokud se obsah změnil, ulož ho
        if new_content != content:
            with open(README_PATH, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print("✅ README.md byl úspěšně aktualizován!")
            return True
        else:
            print("ℹ️ Žádné změny v README.md")
            return False
            
    except Exception as e:
        print(f"❌ Chyba při aktualizaci README: {e}")
        return False


def main():
    print(f"🔍 Získávám posledních {REPO_COUNT} repozitářů pro {USERNAME}...")
    
    token = os.environ.get('GITHUB_TOKEN')
    headers = {}
    if token:
        headers['Authorization'] = f'token {token}'
    
    repos = get_latest_repos(USERNAME, REPO_COUNT)
    
    if repos:
        print(f"✅ Nalezeno {len(repos)} repozitářů, načítám statistiky...")
        repo_list = format_repo_list(repos, headers)
        update_readme(repo_list)
    else:
        print("⚠️ Nebyly nalezeny žádné repozitáře")


if __name__ == "__main__":
    main()
