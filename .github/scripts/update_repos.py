#!/usr/bin/env python3
"""
Skript pro automatickou aktualizaci seznamu repozitářů v README.md
"""

import requests
import os
import re
from datetime import datetime

# GitHub API endpoint
GITHUB_API = "https://api.github.com"
USERNAME = "Ypsilonx"
README_PATH = "README.md"

# Počet repozitářů k zobrazení
REPO_COUNT = 6


def get_latest_repos(username, count=6):
    """Získá nejnovější veřejné repozitáře uživatele."""
    url = f"{GITHUB_API}/users/{username}/repos"
    headers = {}
    
    # Použití GITHUB_TOKEN pokud je dostupný
    token = os.environ.get('GITHUB_TOKEN')
    if token:
        headers['Authorization'] = f'token {token}'
    
    params = {
        'sort': 'created',
        'direction': 'desc',
        'per_page': count,
        'type': 'public'
    }
    
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        repos = response.json()
        
        # Filtrovat pouze non-fork repozitáře nebo zahrnout i forky podle potřeby
        # repos = [r for r in repos if not r['fork']]
        
        return repos[:count]
    except Exception as e:
        print(f"Chyba při získávání repozitářů: {e}")
        return []


def format_repo_list(repos):
    """Vytvoří markdown formát pro seznam repozitářů."""
    if not repos:
        return "<!-- Zatím žádné veřejné repozitáře -->"
    
    markdown = ""
    for repo in repos:
        name = repo['name']
        description = repo['description'] or "Bez popisu"
        url = repo['html_url']
        language = repo['language'] or "N/A"
        stars = repo['stargazers_count']
        created = datetime.strptime(repo['created_at'], '%Y-%m-%dT%H:%M:%SZ')
        created_str = created.strftime('%d.%m.%Y')
        
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
        
        markdown += f"### {emoji} [{name}]({url})\n"
        markdown += f"**{description}**\n\n"
        markdown += f"- 💻 Jazyk: `{language}`\n"
        markdown += f"- ⭐ Stars: {stars}\n"
        markdown += f"- 📅 Vytvořeno: {created_str}\n\n"
        markdown += "---\n\n"
    
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
    repos = get_latest_repos(USERNAME, REPO_COUNT)
    
    if repos:
        print(f"✅ Nalezeno {len(repos)} repozitářů")
        repo_list = format_repo_list(repos)
        update_readme(repo_list)
    else:
        print("⚠️ Nebyly nalezeny žádné repozitáře")


if __name__ == "__main__":
    main()
