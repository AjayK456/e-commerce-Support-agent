import os

def clean_policy_files():
    folder_path = 'policy_knowledge_base'
    if not os.path.exists(folder_path):
        print(f"Folder {folder_path} not found!")
        return

    for filename in os.listdir(folder_path):
        if filename.endswith('.md'):
            file_path = os.path.join(folder_path, filename)
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # This identifies the repetitive "This section outlines..." block and trims it
            marker = "This section outlines the arbitration agreement and liability limitations."
            if content.count(marker) > 2:
                new_content = content.split(marker)[0] + marker + "\n[REMAINDER OF LEGAL TEXT TRUNCATED FOR TOKEN EFFICIENCY]"
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                print(f"✅ Cleaned: {filename}")

if __name__ == "__main__":
    clean_policy_files()