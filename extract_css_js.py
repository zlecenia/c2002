#!/usr/bin/env python3
"""
Skrypt do wyodrębniania CSS i JavaScript z pliku HTML.
Automatycznie tworzy osobne pliki .css i .js i aktualizuje HTML.
"""

import argparse
import os
import re
from pathlib import Path
from bs4 import BeautifulSoup


def extract_css_js(html_file: str, output_dir: str = None):
    """
    Wyodrębnia CSS i JavaScript z pliku HTML i zapisuje w osobnych plikach.
    
    Args:
        html_file: Ścieżka do pliku HTML
        output_dir: Katalog docelowy dla plików CSS/JS (domyślnie: katalog pliku HTML)
    """
    html_path = Path(html_file)
    
    if not html_path.exists():
        print(f"❌ Plik {html_file} nie istnieje!")
        return False
    
    # Określ katalog wyjściowy
    if output_dir is None:
        output_dir = html_path.parent
    else:
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
    
    # Nazwa bazowa pliku (bez rozszerzenia)
    base_name = html_path.stem
    
    # Wczytaj HTML
    with open(html_path, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Wyodrębnienie CSS
    css_content = []
    style_tags = soup.find_all('style')
    
    for i, style_tag in enumerate(style_tags):
        if style_tag.string:
            css_content.append(style_tag.string)
    
    # Wyodrębnienie JavaScript
    js_content = []
    script_tags = soup.find_all('script', src=False)  # Tylko inline scripts (bez src)
    
    for i, script_tag in enumerate(script_tags):
        if script_tag.string and script_tag.string.strip():
            js_content.append(script_tag.string)
    
    # Zapisz CSS jeśli istnieje
    css_file = None
    if css_content:
        css_file = output_dir / f"{base_name}.css"
        with open(css_file, 'w', encoding='utf-8') as f:
            f.write('\n\n'.join(css_content))
        print(f"✅ Zapisano CSS do: {css_file}")
        
        # Usuń tagi <style> i dodaj <link>
        for style_tag in style_tags:
            style_tag.decompose()
        
        # Dodaj link do CSS w <head>
        head = soup.find('head')
        if head is None:
            head = soup.new_tag('head')
            if soup.html:
                soup.html.insert(0, head)
            else:
                soup.insert(0, head)
        
        # Ustal relatywną ścieżkę do pliku CSS
        css_rel_path = os.path.relpath(css_file, html_path.parent)
        link_tag = soup.new_tag('link', rel='stylesheet', href=css_rel_path)
        head.append(link_tag)
    
    # Zapisz JS jeśli istnieje
    js_file = None
    if js_content:
        js_file = output_dir / f"{base_name}.js"
        with open(js_file, 'w', encoding='utf-8') as f:
            f.write('\n\n'.join(js_content))
        print(f"✅ Zapisano JavaScript do: {js_file}")
        
        # Usuń inline script tagi
        for script_tag in script_tags:
            if script_tag.string and script_tag.string.strip():
                script_tag.decompose()
        
        # Dodaj script tag przed zamknięciem </body> lub na końcu
        body = soup.find('body')
        if body is None:
            body = soup.find('html')
        
        if body:
            # Ustal relatywną ścieżkę do pliku JS
            js_rel_path = os.path.relpath(js_file, html_path.parent)
            script_tag = soup.new_tag('script', src=js_rel_path)
            body.append(script_tag)
    
    # Zapisz zaktualizowany HTML
    if css_content or js_content:
        backup_file = html_path.with_suffix('.html.backup')
        
        # Stwórz backup oryginalnego pliku
        with open(backup_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        print(f"📦 Backup oryginalnego pliku: {backup_file}")
        
        # Zapisz zaktualizowany HTML
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(soup.prettify())
        print(f"✅ Zaktualizowano plik HTML: {html_path}")
        
        return True
    else:
        print("ℹ️  Nie znaleziono żadnego inline CSS lub JavaScript do wyodrębnienia.")
        return False


def main():
    parser = argparse.ArgumentParser(
        description='Wyodrębnia CSS i JavaScript z pliku HTML do osobnych plików.'
    )
    parser.add_argument(
        'html_file',
        nargs='?',
        default='index.html',
        help='Ścieżka do pliku HTML (domyślnie: index.html)'
    )
    parser.add_argument(
        '-o', '--output-dir',
        help='Katalog docelowy dla plików CSS/JS (domyślnie: katalog pliku HTML)'
    )
    
    args = parser.parse_args()
    
    print(f"🔍 Przetwarzanie pliku: {args.html_file}")
    print("=" * 60)
    
    success = extract_css_js(args.html_file, args.output_dir)
    
    print("=" * 60)
    if success:
        print("✨ Gotowe! Pliki zostały pomyślnie wyodrębnione.")
    else:
        print("⚠️  Operacja zakończona bez zmian.")


if __name__ == '__main__':
    main()
