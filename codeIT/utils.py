import json
import os
import numpy as np
from sentence_transformers import SentenceTransformer, util

# config
EMB_MODEL_NAME = "all-MiniLM-L6-v2"
EMB_CACHE_FILE = "kb_embeddings.npy"
KB_TEXTS_FILE = "kb_texts.json"

# single model instance (used for encoding queries + docs)
model = SentenceTransformer(EMB_MODEL_NAME)

def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def create_or_load_embeddings(kb_texts):
    """
    Creates or loads cached embeddings. Returns numpy array shape (N, D).
    """
    if os.path.exists(EMB_CACHE_FILE) and os.path.exists(KB_TEXTS_FILE):
        try:
            saved_texts = load_json(KB_TEXTS_FILE)
            if saved_texts == kb_texts:
                emb = np.load(EMB_CACHE_FILE)
                if emb.shape[0] == len(kb_texts):
                    return emb
        except Exception:
            pass

    # compute embeddings (batch_size to avoid memory spikes)
    emb = model.encode(kb_texts, convert_to_numpy=True, show_progress_bar=True, batch_size=32)
    np.save(EMB_CACHE_FILE, emb)
    save_json(KB_TEXTS_FILE, kb_texts)
    return emb

def semantic_search(query, kb_embeddings, kb_texts, top_k=3):
    """
    Returns list of (kb_text, score, index) sorted by score desc.
    """
    q_emb = model.encode([query], convert_to_numpy=True)
    scores = util.cos_sim(q_emb, kb_embeddings)[0].cpu().numpy()
    idxs = np.argsort(-scores)[:top_k]
    return [(kb_texts[i], float(scores[i]), int(i)) for i in idxs]
