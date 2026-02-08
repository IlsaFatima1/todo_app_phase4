#!/usr/bin/env python3
"""
Setup script to help configure the GEMINI_API_KEY environment variable
"""

import os
import sys
from pathlib import Path

def check_env_file():
    """Check if .env file exists and contains GEMINI_API_KEY"""
    env_path = Path("D:/gemini_cli/hackathon2/.env")

    if env_path.exists():
        with open(env_path, 'r') as f:
            content = f.read()
            if 'GEMINI_API_KEY' in content:
                print("[OK] .env file exists and contains GEMINI_API_KEY")
                return True
            else:
                print("[WARN] .env file exists but does NOT contain GEMINI_API_KEY")
                return False
    else:
        print("[WARN] .env file does not exist")
        return False

def create_env_file_with_template():
    """Create a .env file with a template for GEMINI_API_KEY"""
    env_path = Path("D:/gemini_cli/hackathon2/.env")

    # Check if .env.example exists to use as template
    example_path = Path("D:/gemini_cli/hackathon2/.env.example")

    if example_path.exists():
        with open(example_path, 'r') as f:
            content = f.read()

        # Add GEMINI_API_KEY if not already present
        if 'GEMINI_API_KEY' not in content:
            content += "\n# Google Gemini API Key\nGEMINI_API_KEY=\n"
    else:
        # Create basic template
        content = """# Database
DATABASE_URL=

# Google Gemini API Key
GEMINI_API_KEY=
"""

    with open(env_path, 'w') as f:
        f.write(content)

    print(f"[OK] Created .env file at {env_path}")
    print("Please edit the file to add your actual GEMINI_API_KEY")

def main():
    print("GEMINI_API_KEY Setup Helper")
    print("=" * 40)

    # Check current status
    has_key = check_env_file()

    if not has_key:
        print("\nSetting up .env file...")
        create_env_file_with_template()

        print(f"\nNext steps:")
        print("1. Open D:/gemini_cli/hackathon2/.env in a text editor")
        print("2. Add your Google Gemini API key to the GEMINI_API_KEY variable")
        print("3. Save the file")
        print("4. Restart your application")
    else:
        print("\n[OK] Environment appears to be properly configured")

        # Verify the actual value
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key or api_key.strip() == '' or 'your_' in api_key.lower() or 'placeholder' in api_key.lower() or api_key.strip() == 'AIzaSyCxi3ZJY_DK9NN_5CbPgMGPRCPWSRSviO4':
            print("[WARN] GEMINI_API_KEY is set in .env but has placeholder/invalid value")
            print("  Please add your actual API key to the .env file")
        else:
            print("[OK] GEMINI_API_KEY is set with a non-empty value")

if __name__ == "__main__":
    main()