#!/usr/bin/env python3
"""
anthropic_file_upload.py
~~~~~~~~~~~~~~~~~~~~~~~~
Upload files to Anthropic's file service.

Usage:
    python anthropic_file_upload.py --dir ./docs
    python anthropic_file_upload.py --file ./docs/whitepaper.txt
"""
import argparse
import json
import os
import sys
from pathlib import Path
from typing import List, Dict, Any
import anthropic
from dotenv import load_dotenv

load_dotenv()

def gather_files(directory: Path) -> List[Path]:
    """Return a list of files beneath *directory* (non-recursive)."""
    if not directory.is_dir():
        sys.exit(f"❌  '{directory}' is not a directory.")
    return [p for p in directory.iterdir() if p.is_file()]

def get_mime_type(file_path: Path) -> str:
    """Get MIME type based on file extension."""
    extension = file_path.suffix.lower()
    mime_types = {
        '.txt': 'text/plain',
        '.md': 'text/markdown',
        '.pdf': 'application/pdf',
        '.json': 'application/json',
        '.csv': 'text/csv',
        '.doc': 'application/msword',
        '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    }
    return mime_types.get(extension, 'text/plain')

def upload_file_to_anthropic(client: anthropic.Anthropic, file_path: Path) -> Dict[str, Any]:
    """Upload a single file to Anthropic."""
    mime_type = get_mime_type(file_path)
    
    print(f"   Uploading {file_path.name} ({mime_type})...")
    
    with open(file_path, "rb") as f:
        uploaded_file = client.beta.files.upload(
            file=(file_path.name, f, mime_type)
        )
    
    return {
        "id": uploaded_file.id,
        "filename": uploaded_file.filename,
        "size_bytes": uploaded_file.size_bytes,
        "created_at": uploaded_file.created_at,
        "type": uploaded_file.type
    }

def upload_files_to_anthropic(file_paths: List[Path]) -> List[Dict[str, Any]]:
    """Upload multiple files to Anthropic."""
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        sys.exit("❌  ANTHROPIC_API_KEY environment variable not set.")
    
    client = anthropic.Anthropic(api_key=api_key)
    uploaded_files = []
    
    print(f"⬆️  Uploading {len(file_paths)} files to Anthropic...")
    
    for file_path in file_paths:
        try:
            file_info = upload_file_to_anthropic(client, file_path)
            uploaded_files.append(file_info)
            print(f"✅  Uploaded {file_path.name} → {file_info['id']}")
        except Exception as e:
            print(f"❌  Failed to upload {file_path.name}: {e}")
            continue
    
    return uploaded_files

def save_manifest(path: Path, uploaded_files: List[Dict[str, Any]]) -> None:
    """Save upload manifest to JSON file."""
    data = {
        "uploaded_files": uploaded_files,
        "total_files": len(uploaded_files),
        "upload_timestamp": str(Path().stat().st_mtime) if Path().exists() else None
    }
    path.write_text(json.dumps(data, indent=2, default=str))
    print(f"✅  Wrote manifest → {path}")

def main() -> None:
    ap = argparse.ArgumentParser(description="Upload files to Anthropic")
    group = ap.add_mutually_exclusive_group(required=True)
    group.add_argument("--dir", 
                       help="Directory of files to upload")
    group.add_argument("--file", 
                       help="Single file to upload")
    ap.add_argument("--manifest", default="anthropic_uploads.json",
                    help="Where to write the resulting JSON manifest")
    args = ap.parse_args()

    # Gather files to upload
    if args.dir:
        files = gather_files(Path(args.dir))
    else:
        file_path = Path(args.file)
        if not file_path.is_file():
            sys.exit(f"❌  '{file_path}' is not a file.")
        files = [file_path]
    
    if not files:
        sys.exit("❌  No files found to upload.")
    
    print(f"📁  Found {len(files)} files to upload:")
    for f in files:
        print(f"   • {f.name} ({f.stat().st_size} bytes)")
    
    # Upload files
    try:
        uploaded_files = upload_files_to_anthropic(files)
        if uploaded_files:
            save_manifest(Path(args.manifest), uploaded_files)
            print(f"🎉  Successfully uploaded {len(uploaded_files)} files to Anthropic!")
        else:
            print("❌  No files were successfully uploaded.")
    except Exception as e:
        sys.exit(f"❌  Upload failed: {e}")

if __name__ == "__main__":
    main() 