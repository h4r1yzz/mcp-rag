"""
FAQ Loader Module
Loads clinic FAQs from JSON and converts them into LangChain documents for vectorization.
"""

import json
import os
from pathlib import Path
from typing import List, Dict, Any
from langchain_core.documents import Document
from logger import logger


def load_faqs_from_json(json_path: str = None) -> List[Document]:
    if json_path is None:
        # Default path relative to this module
        json_path = Path(__file__).parent.parent / "data" / "clinic_faqs.json"
    
    json_path = Path(json_path)
    
    if not json_path.exists():
        raise FileNotFoundError(f"FAQ file not found at: {json_path}")
    
    logger.info(f"Loading FAQs from: {json_path}")
    
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    faqs = data.get('faqs', [])
    
    if not faqs:
        raise ValueError("No FAQs found in the JSON file")
    
    documents = []
    
    for faq in faqs:
        # Create document content combining question and answer
        content = f"Question: {faq['question']}\n\nAnswer: {faq['answer']}"
        
        # Store metadata for tracking and filtering
        metadata = {
            'id': faq.get('id', ''),
            'question': faq['question'],
            'category': faq.get('category', 'General'),
            'tags': ','.join(faq.get('tags', [])),
            'source': 'clinic_faq_knowledge_base',
            'text': content  # Store full text in metadata for retrieval
        }
        
        doc = Document(
            page_content=content,
            metadata=metadata
        )
        
        documents.append(doc)
    
    logger.info(f"Loaded {len(documents)} FAQs successfully")
    
    return documents


def get_faq_categories(json_path: str = None) -> List[str]:
    if json_path is None:
        json_path = Path(__file__).parent.parent / "data" / "clinic_faqs.json"
    
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    categories = set()
    for faq in data.get('faqs', []):
        if 'category' in faq:
            categories.add(faq['category'])
    
    return sorted(list(categories))


def get_faq_by_id(faq_id: str, json_path: str = None) -> Dict[str, Any]:
    if json_path is None:
        json_path = Path(__file__).parent.parent / "data" / "clinic_faqs.json"
    
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    for faq in data.get('faqs', []):
        if faq.get('id') == faq_id:
            return faq
    
    return None
