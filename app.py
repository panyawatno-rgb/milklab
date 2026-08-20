import os
import json
import uuid
import streamlit as st
import faiss
import numpy as np
from dotenv import load_dotenv
import requests

load_dotenv()

# ==========================================
# 1. Load KB & Chunking (TODO 1)
# ==========================================
def load_and_chunk_kb(filepath="menu_kb.md"):
    if not os.path.exists(filepath):
        # สร้าง KB ตัวอย่างหากหาไฟล์ไม่เจอ
        with open(filepath, "w", encoding="utf-8") as f:
            f.write("# MilkLab° Menu\n\nร้านเปิดบริการทุกวัน 09:00 - 20:00 น.\n\nนมเหนียวดาร์กช็อกโกแลต ราคา 65 บาท หวานน้อย เข้มข้นสะใจ")
    
    with open(filepath, "r", encoding="utf-8") as f:
        text = f.read()
    
    # Chunking ตามบรรทัดว่าง
    chunks = [c.strip() for c in text.split("\n\n") if c.strip()]
    return chunks

# ==========================================
# 2. Embedding & Vector Search (TODO 2 & 3)
# ==========================================
@st.cache_resource
def init_rag():
    chunks = load_and_chunk_kb()
    # โหลด Embedding Model
    from sentence_transformers import SentenceTransformer
    embedder = SentenceTransformer("sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
    embeddings = embedder.encode(chunks, show_progress_bar=False)
    
    # สร้าง FAISS Index
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(np.array(embeddings).astype("float32"))
    
    return chunks, embedder, index

chunks, embedder, index = init_rag()

def retrieve_top_k(query, k=3):
    query_vec = embedder.encode([query]).astype("float32")
    distances, indices = index.search(query_vec, k)
    retrieved_chunks = [chunks[i] for i in indices[0] if i < len(chunks)]
    return retrieved_chunks

# ==========================================
# 3. Gemini Generation + Observability (TODO 5 & 6)
# ==========================================
def generate_answer(query, context_chunks, trace_id):
    context_text = "\n---\n".join(context_chunks)
    prompt = f"""คุณคือผู้ช่วยตอบคำถามประจำร้าน MilkLab° จงตอบคำถามลูกค้าโดยใช้ข้อมูลจาก Context ด้านล่างนี้เท่านั้น หากไม่มีข้อมูลให้ตอบว่าไม่ทราบอย่างสุภาพ

[Context]
{context_text}

[คำถามลูกค้า]
{query}"""

    api_key = os.getenv("GEMINI_API_KEY")
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    payload = {
        "model": "google/gemini-2.5-flash",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.2
    }
    
    try:
        res = requests.post(url, headers=headers, json=payload, timeout=20).json()
        answer = res['choices'][0]['message']['content']
    except Exception as e:
        answer = f"ขออภัยค่ะ เกิดข้อผิดพลาดในการเชื่อมต่อระบบ: {e}"

    trace_data = {
        "trace_id": trace_id,
        "query": query,
        "retrieved_chunks": context_chunks,
        "response": answer
    }
    
    # เขียนลง traces.jsonl
    with open("traces.jsonl", "a", encoding="utf-8") as f:
        f.write(json.dumps(trace_data, ensure_ascii=False) + "\n")

    return answer, trace_data

# ==========================================
# 4. Streamlit UI (TODO 4)
# ==========================================
st.set_page_config(page_title="MilkLab° RAG Chatbot", page_icon="🥛")
st.title("🥛 MilkLab° RAG Chatbot")

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if "trace" in msg:
            with st.expander("🔍 Trace Log"):
                st.json(msg["trace"])

if user_input := st.chat_input("สอบถามเมนู เวลาทำการ หรือโปรโมชัน..."):
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        trace_id = str(uuid.uuid4())
        retrieved_chunks = retrieve_top_k(user_input, k=3)
        answer, trace_info = generate_answer(user_input, retrieved_chunks, trace_id)
        
        st.markdown(answer)
        with st.expander("🔍 Trace Log"):
            st.json(trace_info)
            
    st.session_state.messages.append({"role": "assistant", "content": answer, "trace": trace_info})