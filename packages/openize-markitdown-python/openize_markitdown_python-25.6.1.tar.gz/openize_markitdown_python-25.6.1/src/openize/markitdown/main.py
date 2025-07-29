import argparse
import os
import sys
import logging
from core import MarkItDown
from license_manager import LicenseManager

def ask_user_boolean(question):
    """Ask the user a yes/no question and return True/False."""
    while True:
        response = input(f"{question} (yes/no): ").strip().lower()
        if response in ["yes", "y"]:
            return True
        elif response in ["no", "n"]:
            return False
        else:
            print("Invalid input. Please enter 'yes' or 'no'.")

def ensure_env_variable(var_name, prompt_message, default=None):
    """Ensure an environment variable is set, otherwise ask the user and persist it."""
    value = os.getenv(var_name)

    if not value:
        value = input(prompt_message).strip() or default
        if value:
            set_env_variable(var_name, value)
        else:
            print(f"Warning: {var_name} is not set. This may cause issues.")

    return value

def set_env_variable(var_name, value):
    """Set an environment variable persistently on Windows and Linux/macOS."""
    os.environ[var_name] = value  # Set for the current session

    if os.name == "nt":  # Windows
        os.system(f'setx {var_name} "{value}"')
    else:  # Linux/macOS
        os.system(f'echo "export {var_name}={value}" >> ~/.bashrc')
        os.system(f'echo "export {var_name}={value}" >> ~/.profile')

def main():
    """Entry point for the CLI tool."""
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

    parser = argparse.ArgumentParser(description="Convert documents to Markdown.")
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument("--input-file", help="Path to the input document (PDF, Word, etc.)")
    input_group.add_argument("--input-dir", help="Path to a directory containing supported documents")
    parser.add_argument("-o", "--output-dir", required=True, help="Directory to save the converted Markdown file(s)")
    parser.add_argument("--llm", choices=["none", "openai", "claude", "gemini", "mistral"], default="none",
                        help="Choose LLM client to process output")

    args = parser.parse_args()

    try:
        # Setup Aspose License if needed
        if ask_user_boolean("Do you want to use the Aspose Paid APIs?"):
            license_path = ensure_env_variable("ASPOSE_LICENSE_PATH", "Enter the full path of your Aspose license file: ")
            if license_path:
                LicenseManager().apply_license()

        # Setup LLM credentials only if required
        if args.llm == "openai":
            ensure_env_variable("OPENAI_API_KEY", "Enter your OpenAI API key: ")
            ensure_env_variable("OPENAI_MODEL", "Enter OpenAI model name (default: gpt-4): ", default="gpt-4")
        elif args.llm == "claude":
            ensure_env_variable("CLAUDE_API_KEY", "Enter your Claude API key: ")
            ensure_env_variable("CLAUDE_MODEL", "Enter Claude model name (default: claude-v1): ", default="claude-v1")
        elif args.llm == "gemini":
            ensure_env_variable("GEMINI_API_KEY", "Enter your Gemini API key: ")
            ensure_env_variable("GEMINI_MODEL", "Enter Gemini model name (default: gemini-pro): ", default="gemini-pro")
        elif args.llm == "mistral":
            ensure_env_variable("MISTRAL_API_KEY", "Enter your Mistral API key: ")
            ensure_env_variable("MISTRAL_MODEL", "Enter Mistral model name (default: mistral-medium): ",
                                default="mistral-medium")

        # Initialize MarkItDown with selected LLM
        llm_client_name = args.llm if args.llm != "none" else None
        markitdown = MarkItDown(args.output_dir, llm_client_name)

        # Run conversion for either a single file or a directory
        if args.input_file:
            markitdown.convert_document(args.input_file)
        elif args.input_dir:
            markitdown.convert_directory(args.input_dir)

    except Exception as e:
        logging.error(f"Error: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
