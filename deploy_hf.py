"""
Deploy to Hugging Face Spaces.

Usage:
    python deploy_hf.py --token YOUR_HF_TOKEN --space-name YOUR_SPACE_NAME

Example:
    python deploy_hf.py --token hf_xxxxx --space-name sales-analyzer
"""
import argparse
import os
from huggingface_hub import HfApi, create_repo

# Files to upload to the Space
DEPLOY_FILES = [
    "app.py",
    "db.py",
    "supabase_client.py",
    "pdf_report.py",
    "email_service.py",
    "extract_pdf.py",
    "requirements.txt",
    "Dockerfile",
    "README.md",
    ".streamlit/config.toml",
]


def deploy(token: str, space_name: str):
    api = HfApi(token=token)
    user = api.whoami()["name"]
    repo_id = f"{user}/{space_name}"

    print(f"Deploying to: https://huggingface.co/spaces/{repo_id}")

    # Create the Space (Docker SDK)
    try:
        create_repo(
            repo_id=repo_id,
            repo_type="space",
            space_sdk="docker",
            token=token,
            exist_ok=True,
        )
        print(f"Space '{repo_id}' created/verified.")
    except Exception as e:
        print(f"Repo creation note: {e}")

    # Set Supabase secrets
    env_vars = {}
    supabase_url = os.getenv("SUPABASE_URL", "")
    supabase_key = os.getenv("SUPABASE_KEY", "")
    supabase_service_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")
    admin_emails = os.getenv("ADMIN_EMAILS", "")

    if supabase_url:
        env_vars["SUPABASE_URL"] = supabase_url
    if supabase_key:
        env_vars["SUPABASE_KEY"] = supabase_key
    if supabase_service_key:
        env_vars["SUPABASE_SERVICE_ROLE_KEY"] = supabase_service_key
    if admin_emails:
        env_vars["ADMIN_EMAILS"] = admin_emails

    if env_vars:
        print("Setting secrets (environment variables)...")
        for key, value in env_vars.items():
            api.add_space_secret(repo_id=repo_id, key=key, value=value)
            print(f"  Set secret: {key}")

    # Upload files
    print("Uploading files...")
    base_dir = os.path.dirname(os.path.abspath(__file__))
    for filepath in DEPLOY_FILES:
        full_path = os.path.join(base_dir, filepath)
        if os.path.exists(full_path):
            api.upload_file(
                path_or_fileobj=full_path,
                path_in_repo=filepath,
                repo_id=repo_id,
                repo_type="space",
            )
            print(f"  Uploaded: {filepath}")
        else:
            print(f"  SKIPPED (not found): {filepath}")

    print(f"\nDeployment complete!")
    print(f"Your app will be live at: https://huggingface.co/spaces/{repo_id}")
    print("Note: First build may take a few minutes.")


if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()

    parser = argparse.ArgumentParser(description="Deploy to Hugging Face Spaces")
    parser.add_argument("--token", required=True, help="Hugging Face access token (write)")
    parser.add_argument("--space-name", default="sales-analyzer", help="Name for the Space")
    args = parser.parse_args()

    deploy(args.token, args.space_name)
