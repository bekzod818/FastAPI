"""
Script to compile .po translation files to .mo files using Python.

Run this script after creating or updating translation files.
"""
from pathlib import Path
from babel.messages.pofile import read_po
from babel.messages.mofile import write_mo

from config import settings


def compile_translations():
    """Compile all .po files to .mo files using Babel."""
    locale_dir = Path(settings.locale_dir)
    
    if not locale_dir.exists():
        print(f"Error: Locale directory '{locale_dir}' not found!")
        return
    
    for locale in settings.supported_locales:
        po_file = locale_dir / locale / "LC_MESSAGES" / "messages.po"
        mo_file = locale_dir / locale / "LC_MESSAGES" / "messages.mo"
        
        if not po_file.exists():
            print(f"Warning: {po_file} not found, skipping...")
            continue
        
        try:
            # Read .po file
            with open(po_file, 'rb') as f:
                catalog = read_po(f, locale=locale)
            
            # Write .mo file
            with open(mo_file, 'wb') as f:
                write_mo(f, catalog)
            
            print(f"✓ Compiled {po_file} -> {mo_file}")
        except Exception as e:
            print(f"✗ Error compiling {po_file}: {e}")


if __name__ == "__main__":
    compile_translations()
