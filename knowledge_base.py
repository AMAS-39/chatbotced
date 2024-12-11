# knowledge_base.py
from sentence_transformers import SentenceTransformer
from department_info import DEPARTMENT_INFO_BILINGUAL

def encode_knowledge_base():
    """Encode the content of DEPARTMENT_INFO_BILINGUAL using SentenceTransformer"""
    # Initialize the SentenceTransformer
    model = SentenceTransformer('all-MiniLM-L6-v2')

    # Encode the knowledge base texts
    knowledge_base_texts = list(DEPARTMENT_INFO_BILINGUAL.values())
    knowledge_base_embeddings = model.encode(knowledge_base_texts)

    return knowledge_base_embeddings