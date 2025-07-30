"""Image indexing and AI processing for Doggo."""

import time
from pathlib import Path
from typing import Dict, Any

from doggo.utils import scan_image_files, extract_file_metadata, validate_image_file
from doggo.database import add_image_to_index, get_indexed_files
from doggo.config import add_indexed_path, update_last_reindex
from doggo.openai_client import get_embeddings, get_metadata


def process_single_image(image_path: Path) -> Dict[str, Any]:
    """Process a single image for indexing."""
    # Validate image
    if not validate_image_file(image_path):
        raise ValueError(f"Invalid or corrupted image: {image_path}")
    
    # Extract metadata
    metadata = extract_file_metadata(image_path)
    
    # Generate AI metadata (description, category, filename)
    ai_metadata = get_metadata(image_path)
    metadata.update(ai_metadata)
    
    # Create searchable text (description + filename)
    searchable_text = f"{ai_metadata['description']} {image_path.name}"
    
    # Generate embedding
    embedding = get_embeddings(searchable_text)
    
    return {
        "file_hash": metadata["file_hash"],
        "embedding": embedding,
        "description": ai_metadata["description"],
        "metadata": metadata
    }


def index_directory(directory: Path, dry_run: bool = False) -> Dict[str, Any]:
    """Index all images in a directory."""
    # Scan for image files
    image_files = scan_image_files(directory)
    
    if not image_files:
        return {
            "total_found": 0,
            "processed": 0,
            "skipped": 0,
            "errors": 0,
            "errors_list": []
        }
    
    # Get already indexed files
    indexed_files = set(get_indexed_files())
    
    # Filter out already indexed files
    new_files = [f for f in image_files if extract_file_metadata(f)["file_hash"] not in indexed_files]
    
    if dry_run:
        return {
            "total_found": len(image_files),
            "processed": 0,
            "skipped": len(image_files) - len(new_files),
            "errors": 0,
            "errors_list": [],
            "would_process": len(new_files)
        }
    
    # Process new files
    processed = 0
    errors = 0
    errors_list = []
    
    for image_path in new_files:
        try:
            result = process_single_image(image_path)
            add_image_to_index(
                result["file_hash"],
                result["embedding"],
                result["description"],
                result["metadata"]
            )
            processed += 1
            
        except Exception as e:
            errors += 1
            errors_list.append(f"{image_path}: {str(e)}")
    
    # Update configuration if indexing was successful
    if processed > 0:
        add_indexed_path(str(directory))
        update_last_reindex()
    
    return {
        "total_found": len(image_files),
        "processed": processed,
        "skipped": len(image_files) - len(new_files),
        "errors": errors,
        "errors_list": errors_list
    } 