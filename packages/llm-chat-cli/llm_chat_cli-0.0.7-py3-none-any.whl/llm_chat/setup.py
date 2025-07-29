# src/llm_chat/setup.py
import json
import os
from pathlib import Path
from getpass import getpass
from dotenv import load_dotenv


def setup():
    print("Welcome to the LLM Chat setup!")
    print("Choose how to configure your API keys:")
    print("1. Enter API keys manually")
    print("2. Load from .env file")
    
    choice = input("\nEnter your choice (1 or 2): ").strip()
    
    keys = {}
    
    if choice == "2":
        # Try to load from .env file
        env_path = Path(".env")
        if not env_path.exists():
            env_path = Path.home() / ".env"
        
        if env_path.exists():
            load_dotenv(env_path)
            print(f"\nLoading API keys from {env_path}")
            
            # Define the API keys we're looking for
            api_keys_to_load = [
                "GROQ_API_KEY",
                "OPENAI_API_KEY", 
                "ANTHROPIC_API_KEY",
                "CEREBRAS_API_KEY",
                "OPENROUTER_API_KEY",
                "SERPER_API_KEY"
            ]
            
            for key_name in api_keys_to_load:
                value = os.getenv(key_name)
                if value:
                    keys[key_name] = value
                    print(f"✓ Found {key_name}")
                else:
                    print(f"✗ {key_name} not found in .env file")
            
            if not keys:
                print("\nNo API keys found in .env file. Falling back to manual entry.")
                choice = "1"
        else:
            print(f"\nNo .env file found at {env_path} or ~/.env")
            print("Falling back to manual entry.")
            choice = "1"
    
    if choice == "1":
        print("\nWe'll now collect your API keys. These will be stored securely for future use.")
        providers = ["groq", "openai", "anthropic", "cerebras", "openrouter", "serper"]

        for provider in providers:
            provider_name = provider.upper()
            if provider == "serper":
                print("\nSerper API is used for web search functionality.")
                print("You can get a free API key from https://serper.dev")
            elif provider == "openrouter":
                print("\nOpenRouter provides access to multiple AI models through a single API.")
                print("You can get an API key from https://openrouter.ai")

            key = getpass(f"Enter your {provider_name} API key (input will be hidden): ")
            if key:
                keys[f"{provider_name}_API_KEY"] = key

    # Save the configuration
    config_dir = Path.home() / ".llm_cli"
    config_dir.mkdir(exist_ok=True)

    config_file = config_dir / "config.json"
    with open(config_file, "w") as f:
        json.dump(keys, f)

    print(f"\nAPI keys have been saved to {config_file}")
    
    # Show summary of configured providers
    if keys:
        print("\nConfigured providers:")
        for key_name in keys:
            provider = key_name.replace("_API_KEY", "")
            print(f"  ✓ {provider}")
    
    print("\nYou can now use the LLM Chat!")


if __name__ == "__main__":
    setup()
