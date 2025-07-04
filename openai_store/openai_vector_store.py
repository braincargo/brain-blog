#!/usr/bin/env python3
"""
openai_vector_store.py
~~~~~~~~~~~~~~~~~~~~~~
Create (or reuse) an OpenAI Vector Store and upload a directory of files.

Usage:
    python openai_vector_store.py --dir ./vector_store_docs --name braincargo_knowledge
    python openai_vector_store.py --dir ./updates --store-id vs_abc123...
"""
import argparse
import json
import os
import sys
from pathlib import Path
from typing import List
import requests

from openai import OpenAI
from openai._exceptions import OpenAIError
from dotenv import load_dotenv

load_dotenv()

# ---------- helpers ---------------------------------------------------------

def gather_files(directory: Path) -> List[Path]:
    """Return a list of files beneath *directory* (non-recursive)."""
    if not directory.is_dir():
        sys.exit(f"❌  '{directory}' is not a directory.")
    return [p for p in directory.iterdir() if p.is_file()]

def save_manifest(path: Path, store_id: str, file_ids: List[str]) -> None:
    data = {"vector_store_id": store_id, "file_ids": file_ids}
    path.write_text(json.dumps(data, indent=2))
    print(f"✅  Wrote manifest → {path}")

def get_headers():
    """Get headers for HTTP requests to OpenAI API"""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        sys.exit("❌  OPENAI_API_KEY environment variable not set.")
    return {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "OpenAI-Beta": "assistants=v2"
    }

def list_vector_stores():
    """List existing vector stores using HTTP API"""
    url = "https://api.openai.com/v1/vector_stores"
    response = requests.get(url, headers=get_headers())
    response.raise_for_status()
    return response.json()

def create_vector_store(name: str):
    """Create a new vector store using HTTP API"""
    url = "https://api.openai.com/v1/vector_stores"
    data = {"name": name}
    response = requests.post(url, headers=get_headers(), json=data)
    response.raise_for_status()
    return response.json()

def get_vector_store(store_id: str):
    """Get vector store by ID using HTTP API"""
    url = f"https://api.openai.com/v1/vector_stores/{store_id}"
    response = requests.get(url, headers=get_headers())
    response.raise_for_status()
    return response.json()

def upload_files_to_vector_store(store_id: str, file_paths: List[Path]):
    """Upload files to vector store using file batches"""
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    # First upload files to OpenAI
    file_ids = []
    print(f"⬆️  Uploading {len(file_paths)} files to OpenAI...")
    for file_path in file_paths:
        print(f"   Uploading {file_path.name}...")
        with open(file_path, "rb") as f:
            file_obj = client.files.create(file=f, purpose="assistants")
            file_ids.append(file_obj.id)
    
    # Create file batch using HTTP API
    url = f"https://api.openai.com/v1/vector_stores/{store_id}/file_batches"
    data = {"file_ids": file_ids}
    response = requests.post(url, headers=get_headers(), json=data)
    response.raise_for_status()
    batch = response.json()
    
    # Poll for completion
    batch_id = batch["id"]
    print(f"⏳  Processing file batch {batch_id}...")
    
    while True:
        # Check batch status
        status_url = f"https://api.openai.com/v1/vector_stores/{store_id}/file_batches/{batch_id}"
        status_response = requests.get(status_url, headers=get_headers())
        status_response.raise_for_status()
        batch_status = status_response.json()
        
        if batch_status["status"] == "completed":
            print(f"✅  Upload complete: {batch_status['file_counts']}")
            break
        elif batch_status["status"] == "failed":
            sys.exit(f"❌  Upload failed: {batch_status}")
        else:
            print(f"   Status: {batch_status['status']}")
            import time
            time.sleep(2)
    
    return file_ids

# ---------- main ------------------------------------------------------------

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", required=True,
                    help="Directory of files to upload")
    group = ap.add_mutually_exclusive_group(required=True)
    group.add_argument("--name",
                       help="Name of the vector store to create or reuse", default="braincargo_knowledge")
    group.add_argument("--store-id",
                       help="Existing vector store ID (vs_...)")
    ap.add_argument("--manifest", default="openai_vector_store.json",
                    help="Where to write the resulting JSON manifest")
    args = ap.parse_args()

    files = gather_files(Path(args.dir))
    if not files:
        sys.exit("❌  No files found to upload.")

    # 1️⃣  Get or create the vector store
    if args.store_id:
        store_id = args.store_id
        try:
            vs = get_vector_store(store_id)
            print(f"ℹ️  Reusing vector store '{vs['name']}' ({store_id})")
        except requests.RequestException as e:
            sys.exit(f"❌  Could not retrieve store {store_id}: {e}")
    else:
        # Try to find by name first (cheaper than creating duplicates)
        try:
            existing_stores = list_vector_stores()
            match = next((s for s in existing_stores["data"] if s["name"] == args.name), None)
            if match:
                store_id = match["id"]
                print(f"ℹ️  Reusing existing store '{args.name}' ({store_id})")
            else:
                vs = create_vector_store(args.name)
                store_id = vs["id"]
                print(f"🆕  Created vector store '{args.name}' ({store_id})")
        except requests.RequestException as e:
            sys.exit(f"❌  Could not access vector stores: {e}")

    # 2️⃣  Upload files
    try:
        file_ids = upload_files_to_vector_store(store_id, files)
        save_manifest(Path(args.manifest), store_id, file_ids)
    except requests.RequestException as e:
        sys.exit(f"❌  Upload failed: {e}")
    except Exception as e:
        sys.exit(f"❌  Unexpected error: {e}")

if __name__ == "__main__":
    main() 