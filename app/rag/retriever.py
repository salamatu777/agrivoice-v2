import os
import glob
import re
import logging
from typing import List

logger = logging.getLogger(__name__)

class KnowledgeRetriever:
    """
    Agricultural Knowledge Retriever for Nigerian Farming Guides.
    Supports FAISS vector search when available, with an automatic
    pure-Python semantic keyword & heading matcher fallback.
    """
    def __init__(self, index_path="data/knowledge/faiss_index.bin", texts_path="data/knowledge/texts.pkl"):
        self.use_vector = False
        self.documents = []
        
        # Try loading FAISS & SentenceTransformers if installed
        try:
            import faiss
            import pickle
            from sentence_transformers import SentenceTransformer
            from app.config import settings
            
            if os.path.exists(index_path) and os.path.exists(texts_path):
                self.model = SentenceTransformer(settings.embedding_model)
                self.index = faiss.read_index(index_path)
                with open(texts_path, 'rb') as f:
                    self.texts = pickle.load(f)
                self.use_vector = True
                logger.info("Loaded FAISS vector index for AgriVoice RAG.")
        except Exception as e:
            logger.info(f"Vector RAG unavailable ({e}). Using pure-Python sovereign document indexer.")
            
        if not self.use_vector:
            self._load_markdown_knowledge()

    def _load_markdown_knowledge(self):
        """Load all Nigerian agronomic markdown guides in data/knowledge/."""
        knowledge_dir = os.path.join(os.path.dirname(__file__), "..", "..", "data", "knowledge")
        knowledge_dir = os.path.abspath(knowledge_dir)
        
        if not os.path.exists(knowledge_dir):
            knowledge_dir = "data/knowledge"

        self.documents = []
        for file_path in glob.glob(os.path.join(knowledge_dir, "*.md")):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                    filename = os.path.basename(file_path)
                    
                    # Split into sections by heading
                    sections = re.split(r'\n(?=##?\s)', content)
                    for sec in sections:
                        sec_clean = sec.strip()
                        if len(sec_clean) > 40:
                            self.documents.append({
                                "source": filename,
                                "text": sec_clean
                            })
            except Exception as e:
                logger.error(f"Error reading knowledge doc {file_path}: {e}")

        logger.info(f"Loaded {len(self.documents)} knowledge sections from {knowledge_dir}.")

    def retrieve(self, query: str, top_k: int = 3) -> str:
        """Retrieve the top matching agricultural knowledge snippets."""
        if self.use_vector:
            try:
                query_embedding = self.model.encode([query], convert_to_numpy=True)
                distances, indices = self.index.search(query_embedding, top_k)
                results = []
                for idx in indices[0]:
                    if idx < len(self.texts):
                        results.append(self.texts[idx])
                return "\n\n".join(results)
            except Exception as e:
                logger.error(f"Vector search failed ({e}), falling back to lexical search.")

        # Lexical relevance search across Nigerian agricultural documents
        if not self.documents:
            self._load_markdown_knowledge()

        # Keyword mapping for indigenous terms to English agronomy guides
        TERM_MAPPINGS = {
            "rogo": ["cassava", "cbb", "cmd", "tme 419"],
            "cassava": ["cassava", "cutting", "mosaic", "stem"],
            "masara": ["maize", "corn", "armyworm", "fertilizer", "npk"],
            "agbado": ["maize", "corn", "armyworm", "fertilizer"],
            "maize": ["maize", "corn", "armyworm", "planting", "npk"],
            "corn": ["maize", "corn", "armyworm", "planting"],
            "ji": ["yam", "tuber", "barn", "rot", "staking"],
            "doya": ["yam", "tuber", "barn", "rot", "staking"],
            "yam": ["yam", "tuber", "storage", "barn", "rot"],
            "taki": ["fertilizer", "npk", "urea", "soil"],
            "ajile": ["fertilizer", "npk", "urea", "soil"],
            "fertilizer": ["fertilizer", "npk", "urea", "application"],
            "kokoro": ["pest", "armyworm", "insect", "chemical"],
            "kwari": ["pest", "insect", "armyworm", "disease"],
            "cuta": ["disease", "blight", "virus", "mosaic", "rot"],
            "pest": ["pest", "stem borer", "armyworm", "control"],
            "farashi": ["price", "market", "dawanau", "bodija", "bag"],
            "owo": ["price", "market", "cost", "bag"],
            "ego": ["price", "market", "cost", "bag"],
            "price": ["price", "market", "wholesale", "bag", "dawanau"]
        }

        q_lower = query.lower()
        search_terms = set(re.findall(r'\b\w+\b', q_lower))
        
        # Expand indigenous search terms
        for term, expansions in TERM_MAPPINGS.items():
            if term in q_lower:
                search_terms.update(expansions)

        scored = []
        for doc in self.documents:
            doc_lower = doc["text"].lower()
            score = sum(3 if term in doc_lower else 0 for term in search_terms)
            if score > 0:
                scored.append((score, doc["text"]))

        scored.sort(key=lambda x: x[0], reverse=True)
        top_chunks = [item[1] for item in scored[:top_k]]
        
        if not top_chunks and self.documents:
            # Fallback to first general guide
            top_chunks = [self.documents[0]["text"]]

        return "\n\n".join(top_chunks)
