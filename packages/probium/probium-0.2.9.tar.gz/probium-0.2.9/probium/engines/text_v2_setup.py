import os
import subprocess
import shutil
from pathlib import Path

def setup_tree_sitter():
    """Set up tree-sitter languages for the text engine."""
    # Create build directory
    build_dir = Path(__file__).parent / "build"
    build_dir.mkdir(exist_ok=True)
    
    # Define languages to support
    languages = {
        "python": "https://github.com/tree-sitter/tree-sitter-python",
        "javascript": "https://github.com/tree-sitter/tree-sitter-javascript",
        "typescript": "https://github.com/tree-sitter/tree-sitter-typescript",
        "cpp": "https://github.com/tree-sitter/tree-sitter-cpp",
        "java": "https://github.com/tree-sitter/tree-sitter-java",
        "ruby": "https://github.com/tree-sitter/tree-sitter-ruby",
        "go": "https://github.com/tree-sitter/tree-sitter-go",
        "rust": "https://github.com/tree-sitter/tree-sitter-rust",
        "php": "https://github.com/tree-sitter/tree-sitter-php",
    }
    
    # Clone and build each grammar
    for lang, repo in languages.items():
        lang_dir = build_dir / f"tree-sitter-{lang}"
        
        # Clone repository if not exists
        if not lang_dir.exists():
            subprocess.run(["git", "clone", repo, str(lang_dir)], check=True)
            
        # Build the grammar using node.js (required by tree-sitter)
        try:
            # Navigate to grammar directory
            original_dir = os.getcwd()
            os.chdir(str(lang_dir))
            
            # Install dependencies and build
            subprocess.run(["npm", "install"], check=True, shell=True)
            subprocess.run(["npx", "tree-sitter", "generate"], check=True, shell=True)
            
            # Copy the compiled grammar to our build directory
            grammar_path = lang_dir / "src"
            if grammar_path.exists():
                shutil.copy2(str(grammar_path / "parser.c"), str(build_dir / f"{lang}.c"))
                shutil.copy2(str(grammar_path / "tree_sitter"), str(build_dir / f"{lang}.h"))
                print(f"Successfully built {lang} grammar")
            else:
                print(f"Grammar source not found for {lang}")
                
            # Return to original directory
            os.chdir(original_dir)
            
        except Exception as e:
            print(f"Failed to build {lang} grammar: {e}")
            os.chdir(original_dir)

if __name__ == "__main__":
    setup_tree_sitter() 