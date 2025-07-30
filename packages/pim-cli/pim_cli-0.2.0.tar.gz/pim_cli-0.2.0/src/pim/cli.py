#!/usr/bin/env python3
import argparse
import logging
from pathlib import Path
from huggingface_hub import snapshot_download

# Import the pimfile parser
from pim.util.pimfile_parser import load_pimfile

# --- Installation Functions ---

def install_huggingface(model_id: str, models_dir: Path, use_auth: bool):
    """Downloads a model from Hugging Face Hub."""
    logging.info(f"Installing HuggingFace model: {model_id}")
    # Use a safe directory name and pathlib for robust path handling
    target_dir = models_dir / "huggingface" / model_id.replace("/", "__")
    target_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        snapshot_download(
            repo_id=model_id,
            local_dir=target_dir,
            use_auth_token=use_auth
        )
        logging.info(f"Model downloaded to {target_dir}")
    except Exception as e:
        logging.error(f"Failed to download {model_id}: {e}")

def install_torchvision(model_id: str):
    """Provides instructions for using a torchvision model."""
    logging.info(f"Preparing torchvision model: {model_id}")
    logging.info("Torchvision models are downloaded on first use via the library.")
    logging.info(f"To use '{model_id}', import it in your Python code.")

def install_sklearn(model_path: str, project_root: Path):
    """Checks for the existence of a local sklearn model file."""
    logging.info(f"Checking for sklearn model: {model_path}")
    # Resolve the model path relative to the project root (Pimfile location)
    model_file = project_root / Path(model_path)
    if model_file.exists():
        logging.info(f"Model found at: {model_file.resolve()}")
    else:
        logging.warning(f"Model file not found at: {model_file.resolve()}")
        logging.warning("Please ensure the file exists at the specified path.")

# --- CLI Command Handlers ---

def run_install(args):
    """Handler for the 'install' command."""
    try:
        pimfile_path = Path(args.file)
        # The project root is the directory containing the Pimfile.
        # It's used to resolve relative paths for local models (e.g., sklearn).
        project_root = pimfile_path.resolve().parent

        # Determine the installation root for downloaded models.
        if args.target:
            install_root = Path(args.target).resolve()
            logging.info(f"Using user-specified target directory: {install_root}")
        else:
            install_root = Path.home() / ".pim"
            logging.info(f"Using default global directory: {install_root}")

        logging.info(f"Installing models from {pimfile_path.resolve()}...")
        models_to_install = load_pimfile(pimfile_path)
        
        # The directory where downloaded models (e.g., from Hugging Face) will be stored.
        models_dir = install_root / "models"

        if not models_to_install:
            logging.info("No models to install.")
            return

        for framework, models in models_to_install.items():
            logging.info(f"--- Processing framework: {framework} ---")
            if not models:
                logging.info("No models listed for this framework.")
                continue

            for model in models:
                if framework == "huggingface":
                    install_huggingface(model, models_dir, use_auth=args.auth)
                elif framework == "torchvision":
                    install_torchvision(model)
                elif framework == "sklearn":
                    # Pass the project root to resolve the relative path
                    install_sklearn(model, project_root)
    except (FileNotFoundError, ValueError) as e:
        logging.error(e)

def run_list(args):
    """Handler for the 'list' command."""
    try:
        pimfile_path = Path(args.file)
        print(f"Models declared in {pimfile_path.resolve()}:\n")
        models_to_list = load_pimfile(pimfile_path)

        for framework, models in models_to_list.items():
            print(f"  {framework}:")
            if models:
                for model in models:
                    print(f"    - {model}")
            else:
                print("    (no models specified)")
    except (FileNotFoundError, ValueError) as e:
        logging.error(e)

# --- Main Entrypoint ---

def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)s: %(message)s",
    )

    parser = argparse.ArgumentParser(
        description="A CLI to declaratively install and manage machine learning models from a Pimfile."
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands", required=True)

    # --- Install Command ---
    parser_install = subparsers.add_parser("install", help="Install models from a Pimfile")
    parser_install.add_argument("-f", "--file", default="Pimfile", help="Path to the Pimfile (default: ./Pimfile)")
    parser_install.add_argument("--target", help="Directory to install models into (default: ~/.pim)")
    parser_install.add_argument("--auth", action="store_true", help="Use Hugging Face token for private models")
    parser_install.set_defaults(func=run_install)

    # --- List Command ---
    parser_list = subparsers.add_parser("list", help="List models defined in a Pimfile")
    parser_list.add_argument("-f", "--file", default="Pimfile", help="Path to the Pimfile (default: ./Pimfile)")
    parser_list.set_defaults(func=run_list)

    args = parser.parse_args()
    args.func(args)

if __name__ == "__main__":
    main()