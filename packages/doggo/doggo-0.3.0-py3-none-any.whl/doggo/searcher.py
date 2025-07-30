"""Semantic search functionality for Doggo."""

from typing import List, Dict, Any

from doggo.database import get_images_collection
from doggo.openai_client import get_embeddings

def search_similar_images(query: str, limit: int = 10) -> List[Dict[str, Any]]:
    """Search for images using semantic similarity."""
    if not query.strip():
        raise ValueError("Search query cannot be empty")
    
    if limit <= 0:
        raise ValueError("Limit must be positive")
    
    # Generate query embedding
    query_embedding = get_embeddings(query)
    
    # Get images collection
    collection = get_images_collection()
    
    # Perform similarity search
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=limit,
        include=['documents', 'metadatas', 'distances']
    )
    
    # Format results
    formatted_results = []
    for i in range(len(results['ids'][0])):
        formatted_results.append({
            'id': results['ids'][0][i],
            'description': results['documents'][0][i],
            'metadata': results['metadatas'][0][i],
            'similarity_score': 1 - results['distances'][0][i]  # Convert distance to similarity
        })
    
    return formatted_results


def get_top_result_preview(result: Dict[str, Any]) -> str:
    """Generate preview information for top search result."""
    metadata = result['metadata']
    file_path = metadata.get('file_path', 'Unknown')
    file_name = metadata.get('file_name', 'Unknown')
    file_size = metadata.get('file_size', 0)
    similarity = result['similarity_score']
    
    # Format file size
    if file_size > 1024 * 1024:
        size_str = f"{file_size / (1024 * 1024):.1f} MB"
    elif file_size > 1024:
        size_str = f"{file_size / 1024:.1f} KB"
    else:
        size_str = f"{file_size} B"
    
    preview = f"""
📁 File: {file_name}
📍 Path: {file_path}
📏 Size: {size_str}
🎯 Similarity: {similarity:.1%}
📝 Description: {result['description']}
"""
    
    return preview.strip() 