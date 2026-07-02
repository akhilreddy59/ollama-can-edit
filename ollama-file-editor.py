import os
import sys
import json
import requests
import difflib

CONFIG_FILE = ".local-dev-config.json"

# Folders we should completely skip when mapping the directory
IGNORE_DIRS = {'.git', 'node_modules', '__pycache__', 'dist', 'build', '.next', 'venv', '.venv'}


def load_or_create_config():
    """Architectural Upgrade: Manages interactive terminal setups and securely provisions keys."""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            print("⚠️ Configuration file corrupted. Re-running setup...")

    print("\n⚙️  --- FIRST-TIME CONFIGURATION SETUP ---")
    print("Welcome! Let's configure your AI engine backend for this project workspace.")
    print("1. Local Ollama Instance (Free, Private, Local)")
    print("2. Cloud Provider API (OpenAI, DeepSeek, OpenRouter, Groq, Anthropic, etc.)")
    
    choice = input("\nSelect backend provider option (1 or 2): ").strip()
    
    config = {}
    if choice == "2":
        config["backend"] = "cloud"
        config["api_url"] = input("🌐 Enter API Base URL (e.g., https://api.deepseek.com/v1 or https://api.openai.com/v1): ").strip()
        config["api_key"] = input("🔑 Enter your Secret API Key: ").strip()
        config["model"] = input("🤖 Enter the exact Model identifier code (e.g., deepseek-coder, gpt-4o): ").strip()
    else:
        config["backend"] = "ollama"
        config["api_url"] = input("🌐 Enter Ollama API Base URL [Default: http://localhost:11434]: ").strip() or "http://localhost:11434"
        config["api_key"] = ""
        config["model"] = "" # Will dynamically auto-detect below

    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=4)
        print(f"✅ Configuration successfully saved locally to `{CONFIG_FILE}`!\n")
    except Exception as e:
        print(f"❌ Failed to write configuration to file: {e}")
        sys.exit(1)

    return config


def get_installed_ollama_models(api_url):
    """Fetches list of installed models from local Ollama instance if active."""
    try:
        res = requests.get(f"{api_url}/api/tags", timeout=3)
        if res.status_code == 200:
            return [m['name'] for m in res.json().get('models', [])]
    except Exception:
        pass
    return []


def resolve_best_model(config):
    """Dynamically resolves the AI target model weights matrix."""
    if config["backend"] == "cloud":
        return config["model"]
        
    # Otherwise evaluate local Ollama priority framework
    models = get_installed_ollama_models(config["api_url"])
    if not models:
        print(f"❌ No active models found in your local Ollama app at {config['api_url']}.")
        print("💡 Open your terminal and run: ollama pull qwen2.5-coder:7b")
        sys.exit(1)

    code_keywords = ['coder', 'qwen3', 'qwen2.5', 'deepseek-coder', 'codellama', 'granite', 'devstral']
    reasoning_keywords = ['r1', 'phi4', 'llama3.3']
    general_keywords = ['llama3', 'gemma', 'mistral', 'phi3']

    for kw in code_keywords + reasoning_keywords + general_keywords:
        match = [m for m in models if kw in m.lower()]
        if match:
            return match[0]
            
    return models[0]


def generate_file_tree(root_dir):
    """Walks the directory and creates a clean text-based file tree structure."""
    tree_lines = []
    for root, dirs, files in os.walk(root_dir):
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
        
        level = os.path.relpath(root, root_dir).count(os.sep)
        if level == 0 and root == root_dir:
            level = 0
        else:
            level += 1
            
        indent = '  ' * (level - 1) if level > 0 else ''
        folder_name = os.path.basename(root)
        if folder_name and root != root_dir:
            tree_lines.append(f"{indent}📁 {folder_name}/")
        
        sub_indent = '  ' * level
        for f in files:
            if not f.startswith('.') and not f.endswith(('.png', '.jpg', '.ico', '.pyc', '.gif', '.pdf')):
                relative_path = os.path.relpath(os.path.join(root, f), root_dir)
                tree_lines.append(f"{sub_indent}📄 {relative_path}")
                
    return "\n".join(tree_lines)


def unified_api_chat(messages, config, resolved_model):
    """Polymorphic API Request Handler routing safely to OpenAI standard endpoints or Ollama."""
    headers = {"Content-Type": "application/json"}
    if config["api_key"]:
        headers["Authorization"] = f"Bearer {config['api_key']}"

    # Normalize URLs out to chat completions schemas 
    base_url = config["api_url"].rstrip('/')
    if config["backend"] == "ollama":
        target_url = f"{base_url}/api/chat"
        payload = {"model": resolved_model, "messages": messages, "stream": False, "options": {"temperature": 0.1}}
    else:
        target_url = f"{base_url}/chat/completions"
        payload = {"model": resolved_model, "messages": messages, "stream": False, "temperature": 0.1}

    try:
        response = requests.post(target_url, json=payload, headers=headers, timeout=45)
        if response.status_code == 200:
            res_json = response.json()
            # Handle standard openAI JSON object responses vs Ollama responses
            if "choices" in res_json:
                return res_json["choices"][0]["message"]["content"].strip()
            return res_json['message']['content'].strip()
        else:
            print(f"\n❌ API Server Returned Error Status Code {response.status_code}: {response.text}")
            sys.exit(1)
    except requests.exceptions.RequestException as e:
        print(f"\n❌ Request Error connection to API endpoint failed: {e}")
        sys.exit(1)


def locate_target_file(file_tree, user_request, config, model):
    """Step 1: Ask engine to pick the single best match file path out of the file tree."""
    system_prompt = (
        "You are a repository mapping assistant. Analyze the given project file tree and the user request.\n"
        "Identify the SINGLE exact file path from the list that needs to be modified to fulfill the request.\n"
        "Return ONLY the relative file path string itself, with no markdown, no quotes, and no extra explanation."
    )
    user_prompt = f"PROJECT FILE TREE:\n{file_tree}\n\nUSER REQUEST: {user_request}\n\nTarget File Path:"
    
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]
    return unified_api_chat(messages, config, model)


def generate_file_edits(file_path, original_content, user_request, config, model):
    """Step 2: Send the specific target file contents to AI to perform the edits."""
    system_prompt = (
        "You are an expert local code editor. You modify existing files based on user prompts.\n"
        "Output the complete modified file contents. Do not include markdown code block styling wrappers like ```js.\n"
        "Start your response instantly with the raw file content code, and output nothing else."
    )
    user_prompt = f"FILE PATH: {file_path}\n\nORIGINAL CONTENT:\n{original_content}\n\nUSER REQUEST: {user_request}\n\nUPDATED COMPLETE FILE CONTENT:"
    
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]
    return unified_api_chat(messages, config, model)


def is_safe_path(base_dir, path, follow_symlinks=True):
    """Architectural Security: Ensures the resolved path stays inside the intended folder."""
    if follow_symlinks:
        matchpath = os.path.realpath(path)
    else:
        matchpath = os.path.abspath(path)
    return base_dir == os.path.commonpath((base_dir, matchpath))


def main():
    print("⚡ Welcome to Local-Dev Open Source Code Engine ⚡")
    
    # Run or load interactive onboarding configuration matrix
    config = load_or_create_config()
    selected_model = resolve_best_model(config)
    
    print(f"🤖 Active Framework Target Model: \033[95m{selected_model}\033[0m")

    user_request = input("\n💡 What code modification do you want to make? -> ")
    if not user_request:
        print("Empty instruction. Exiting.")
        return

    current_dir = os.path.realpath(os.getcwd())
    print("🔍 Indexing repository workspace layout...")
    file_tree = generate_file_tree(current_dir)
    
    print("🧠 Asking AI to locate target file path...")
    raw_target_path = locate_target_file(file_tree, user_request, config, selected_model)
    
    target_path = raw_target_path.strip().replace("`", "").replace("📄 ", "")
    full_target_file_path = os.path.abspath(os.path.join(current_dir, target_path))

    if not is_safe_path(current_dir, full_target_file_path):
        print(f"❌ Security Block: AI attempted to access a path outside working directory: '{target_path}'")
        return

    if not os.path.exists(full_target_file_path) or os.path.isdir(full_target_file_path):
        print(f"❌ AI tried to select path '{target_path}', but it does not exist locally.")
        return

    print(f"🎯 AI identified target file: \033[94m{target_path}\033[0m")
    
    with open(full_target_file_path, "r", encoding="utf-8") as f:
        original_content = f.read()

    print("🛠️ Generating updated code refactor...")
    updated_content = generate_file_edits(target_path, original_content, user_request, config, selected_model)

    if not updated_content:
        print("❌ Failed to generate updated code variations.")
        return

    print("\n--- 📊 PROPOSED CODE CHANGES (DIFF) ---")
    diff = difflib.unified_diff(
        original_content.splitlines(), 
        updated_content.splitlines(), 
        fromfile=f"a/{target_path}", 
        tofile=f"b/{target_path}", 
        lineterm=""
    )
    
    has_changes = False
    for line in diff:
        has_changes = True
        if line.startswith('+') and not line.startswith('+++'):
            print(f"\033[92m{line}\033[0m") 
        elif line.startswith('-') and not line.startswith('---'):
            print(f"\033[91m{line}\033[0m") 
        else:
            print(line)

    if not has_changes:
        print("No structural changes detected by the model.")
        return

    confirm = input("\n💾 Do you want to apply these file modifications to disk? (y/N): ")
    if confirm.lower() == 'y':
        with open(full_target_file_path, "w", encoding="utf-8") as f:
            f.write(updated_content)
        print("✅ Changes applied successfully!")
    else:
        print("❌ Operation aborted by user.")

if __name__ == "__main__":
    main()