import os
import glob
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import pickle
from app.config import settings

class KnowledgeIndexer:
    def __init__(self):
        self.model = SentenceTransformer(settings.embedding_model)
        self.knowledge_dir = settings.knowledge_dir
        self.chunk_size = 500

    def load_documents(self):
        docs = []
        for filepath in glob.glob(os.path.join(self.knowledge_dir, "*.md")):
            with open(filepath, 'r', encoding='utf-8') as f:
                text = f.read()
                # simple chunking by paragraphs
                paragraphs = text.split('\n\n')
                for p in paragraphs:
                    p = p.strip()
                    if len(p) > 50:
                        docs.append(p)
        return docs

    def build_index(self, index_path="data/knowledge/faiss_index.bin", texts_path="data/knowledge/texts.pkl"):
        docs = self.load_documents()
        if not docs:
            print("No documents found to index.")
            return

        embeddings = self.model.encode(docs, convert_to_numpy=True)
        dimension = embeddings.shape[1]
        
        index = faiss.IndexFlatL2(dimension)
        index.add(embeddings)
        
        faiss.write_index(index, index_path)
        with open(texts_path, 'wb') as f:
            pickle.dump(docs, f)
        print(f"Successfully indexed {len(docs)} chunks.")

if __name__ == "__main__":
    indexer = KnowledgeIndexer()
    indexer.build_index()
