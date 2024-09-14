import argparse
import os
import sys
import subprocess
import datetime
import json
import re

def check_openai_installation():
    try:
        from openai import OpenAI
        return True
    except ImportError:
        return False

def install_openai():
    print("The 'openai' module is not installed or needs to be updated. Would you like to install/update it now? (y/n)")
    choice = input().lower()
    if choice == 'y':
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "openai"])
            print("OpenAI module installed/updated successfully!")
            return True
        except subprocess.CalledProcessError:
            print("Failed to install/update the OpenAI module. Please install it manually using 'pip install --upgrade openai'")
            return False
    else:
        print("OpenAI module is required to run this script. Please install/update it manually using 'pip install --upgrade openai'")
        return False

def generate_text(prompt, api_key):
    from openai import OpenAI
    client = OpenAI(api_key=api_key)
    try:
        chat_completion = client.chat.completions.create(
    messages=[
        {
            "role": "system",
            "content": """You are an expert bash script generator with deep knowledge of various operating systems. Your task is to create fully functional, complete bash scripts based on the user's input. Always return ONLY the bash script code, without any explanations or markdown formatting. Ensure all functions and logic are fully implemented with actual system commands, not placeholder comments."""
        },
        {
            "role": "user",
            "content": f"""Create a complete and fully functional bash script that performs the following tasks:

{prompt}

Implement the entire script logic, including:

1. All necessary functions, fully implemented with actual system commands and logic (NO placeholder comments).
   - For macOS, use appropriate AppleScript commands with 'osascript'.
   - For Linux, use relevant system commands or modify configuration files as needed.
   - For Windows (if using WSL), use appropriate Windows commands through 'wsl.exe' or PowerShell.

2. A main interactive loop that:
   a. Checks and displays the current state or value relevant to the script's purpose using actual system commands.
   b. Presents a menu of actions to the user.
   c. Reads user input.
   d. Performs the chosen action by calling the appropriate function(s) with real system interactions.
   e. Displays the updated state or value after the action, again using actual system commands to check.
   f. Repeats this process until the user chooses to exit.

3. Proper error handling for invalid inputs or potential issues, including checking for necessary permissions or dependencies.
4. Any necessary setup or initialization at the beginning of the script, including checking for required tools or setting up the environment.
5. Appropriate cleanup or finalization at the end of the script if necessary.

Ensure the script:
- Starts with a proper shebang (#!/bin/bash).
- Uses appropriate error handling throughout, including checking the success of system commands.
- Includes comments explaining key sections and complex logic.
- Is fully compatible with the specified operating system, using the correct system-specific commands.
- Uses best practices for bash scripting, including proper variable quoting, error checking, and secure coding practices.

Return ONLY the complete bash script code, without any explanations or markdown formatting. The script should be ready to run as-is, with all functions and logic fully implemented using actual system commands."""
        }
    ],
            model="gpt-4o",
        )
        return chat_completion.choices[0].message.content.strip()
    except Exception as e:
        return f"An error occurred: {e}"

def save_to_file(content, prompt):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    scripts_dir = os.path.join(script_dir, "scripts")
    
    # Create the scripts directory if it doesn't exist
    if not os.path.exists(scripts_dir):
        os.makedirs(scripts_dir)

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Extract keywords from the prompt
    keywords = re.findall(r'\b\w+\b', prompt.lower())
    common_words = set(['the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'from', 'up', 'about', 'into', 'over', 'after'])
    meaningful_words = [word for word in keywords if word not in common_words]
    
    # Use the first two meaningful words for the filename, or 'script' if none are found
    if len(meaningful_words) >= 2:
        name_part = f"{meaningful_words[0]}_{meaningful_words[1]}"
    elif len(meaningful_words) == 1:
        name_part = meaningful_words[0]
    else:
        name_part = "script"
    
    filename = f"{name_part}_{timestamp}.sh"
    filepath = os.path.join(scripts_dir, filename)
    
    with open(filepath, 'w') as file:
        file.write(content)
    
    # Make the file executable
    os.chmod(filepath, 0o755)
    
    return filepath

def get_config_path():
    return os.path.join(os.path.expanduser("~"), ".gpt_cli_config.json")

def load_config():
    config_path = get_config_path()
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            return json.load(f)
    return {}

def save_config(config):
    config_path = get_config_path()
    with open(config_path, 'w') as f:
        json.dump(config, f)

def get_api_key():
    config = load_config()
    api_key = config.get('api_key') or os.environ.get('OPENAI_API_KEY')
    
    if not api_key:
        print("OpenAI API key not found in saved configuration or environment variables.")
        api_key = input("Please enter your OpenAI API key: ").strip()
        if api_key:
            save_api_key = input("Would you like to save this API key for future use? (y/n): ").lower()
            if save_api_key == 'y':
                config['api_key'] = api_key
                save_config(config)
                print("API key saved for future use.")
            
            # Set the API key for the current session
            os.environ['OPENAI_API_KEY'] = api_key
    
    return api_key

def run_script(filepath):
    try:
        subprocess.run([filepath], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running the script: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

def main():
    if not check_openai_installation():
        if not install_openai():
            return

    parser = argparse.ArgumentParser(description="Generate a bash script using OpenAI GPT, save as a .sh file, and run it")
    parser.add_argument("prompt", help="Additional context or requirements for the bash script")
    parser.add_argument("--api_key", help="Your OpenAI API key")
    args = parser.parse_args()

    api_key = args.api_key or get_api_key()
    
    if not api_key:
        print("Error: OpenAI API key not provided. Exiting.")
        return

    response = generate_text(args.prompt, api_key)
    filepath = save_to_file(response, args.prompt)
    print(f"Bash script saved to: {filepath}")
    print("Running the generated script...")
    run_script(filepath)

if __name__ == "__main__":
    main()
