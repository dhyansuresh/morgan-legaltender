#!/usr/bin/env python3
"""
Quick test script to verify API keys are configured correctly
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_api_keys():
    """Test if API keys are configured"""

    print("=" * 60)
    print("API Key Configuration Check")
    print("=" * 60)
    print()

    # Check OpenAI
    openai_key = os.getenv('OPENAI_API_KEY')
    if openai_key and openai_key != "your-openai-key-here" and openai_key.startswith('sk-'):
        print("✅ OpenAI API Key: Configured")
        print(f"   Key starts with: {openai_key[:20]}...")
        openai_configured = True
    else:
        print("❌ OpenAI API Key: Not configured")
        print("   Get one at: https://platform.openai.com/api-keys")
        openai_configured = False

    print()

    # Check Anthropic
    anthropic_key = os.getenv('ANTHROPIC_API_KEY')
    if anthropic_key and anthropic_key.startswith('sk-ant-'):
        print("✅ Anthropic API Key: Configured")
        print(f"   Key starts with: {anthropic_key[:20]}...")
        anthropic_configured = True
    else:
        print("❌ Anthropic API Key: Not configured")
        print("   Get one at: https://console.anthropic.com/")
        anthropic_configured = False

    print()

    # Check Google
    google_key = os.getenv('GOOGLE_AI_API_KEY')
    if google_key and google_key != "":
        print("✅ Google AI API Key: Configured")
        print(f"   Key starts with: {google_key[:20]}...")
        google_configured = True
    else:
        print("❌ Google AI API Key: Not configured")
        print("   Get one at: https://makersuite.google.com/app/apikey")
        google_configured = False

    print()
    print("=" * 60)

    # Summary
    has_key = openai_configured or anthropic_configured or google_configured

    if has_key:
        print("\n✅ SUCCESS! At least one API key is configured.")
        print("\nYou can now run the server:")
        print("   python app.py")
        print("\nAPI will be available at:")
        print("   http://localhost:8000/docs")

        # Show which provider will be used
        if openai_configured:
            print("\n🤖 Using: OpenAI")
        elif anthropic_configured:
            print("\n🤖 Using: Anthropic Claude")
        elif google_configured:
            print("\n🤖 Using: Google Gemini")

    else:
        print("\n⚠️  WARNING: No API keys configured!")
        print("\nTo fix this:")
        print("1. Open backend/.env file")
        print("2. Add at least one API key:")
        print("   OPENAI_API_KEY=sk-proj-your-key-here")
        print("3. Save the file")
        print("4. Run this test again")
        print("\nFor detailed instructions, see: SETUP_API_KEYS.md")

    print()
    print("=" * 60)

    return has_key


def test_environment():
    """Test overall environment setup"""

    print("\n" + "=" * 60)
    print("Environment Configuration")
    print("=" * 60)
    print()

    env = os.getenv('ENVIRONMENT', 'development')
    port = os.getenv('PORT', '8000')

    print(f"Environment: {env}")
    print(f"Port: {port}")
    print(f"Working Directory: {os.getcwd()}")

    # Check if .env exists
    env_file = os.path.join(os.getcwd(), '.env')
    if os.path.exists(env_file):
        print(f"✅ .env file found at: {env_file}")
    else:
        print(f"❌ .env file NOT found at: {env_file}")
        print(f"   Create it by copying .env.example")

    print("=" * 60)


if __name__ == "__main__":
    print("\n🔍 Testing API Configuration...\n")

    # Test environment
    test_environment()

    # Test API keys
    has_keys = test_api_keys()

    # Exit with appropriate code
    import sys
    sys.exit(0 if has_keys else 1)
