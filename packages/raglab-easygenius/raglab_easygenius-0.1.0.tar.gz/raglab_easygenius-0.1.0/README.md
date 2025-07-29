# 🧠 MyRAGProject

**Now with interactive setup!**

- On first use, you'll be prompted to choose your embedding model (HuggingFace or Gemini) and vector database (Qdrant or FAISS).
- The setup wizard will create a `.env` file for your configuration and install only the dependencies you need.
- Supports Gemini API key and Qdrant port via `.env`.

---

## 📦 Features

- 🔍 Smart chunking of input documents
- 🤖 Embedding generation via HuggingFace
- 🧠 Vector storage using Qdrant
- 💬 Ready for question-answering and search
- 🚀 Modular and easy to extend

---

## 🗂️ Folder Structure

myragproject/
├── main.py
├── data/
│ └── sample.txt
├── app/
│ ├── config.py
│ └── ingest.py
├── raglib/
│ ├── chunking/
│ │ └── smart_chunker.py
│ ├── embeddings/
│ │ └── huggingface.py
│ └── vector_stores/
│ └── qdrant_store.py

yaml
Copy
Edit

---

## 🔧 Setup Instructions

### 1. Clone the repository

```bash
git clone https://github.com/your-username/myragproject.git
cd myragproject
2. Install dependencies
bash
Copy
Edit
pip install -r requirements.txt
Or manually install:

bash
Copy
Edit
pip install sentence-transformers qdrant-client requests
3. Start Qdrant (vector DB)
bash
Copy
Edit
docker run -p 6333:6333 -v qdrant_data:/qdrant/storage qdrant/qdrant
This ensures persistent vector storage.

4. Add your document
Place a .txt file inside the data/ folder, e.g.:

bash
Copy
Edit
data/sample.txt
🚀 Run the RAG Ingest Pipeline
bash
Copy
Edit
python main.py
It will:

Read the file

Split it into chunks

Generate embeddings

Store in Qdrant with payloads

📖 Example Output
bash
Copy
Edit
📄 Starting ingestion for: data/sample.txt
🧩 Created 4 chunks
🔢 Generated embeddings
✅ Stored 4 points in Qdrant.
✅ Embeddings stored successfully in Qdrant.
🔍 Coming Soon
❓ Ask questions and retrieve top relevant chunks

📚 Support for PDFs and multiple file types

🧪 FastAPI-based chatbot API

🧠 Tech Stack
Python 3.10+

HuggingFace (sentence-transformers)

Qdrant vector store

Docker (for Qdrant server)

🧩 Credits
Built with ❤️ by [Abhishek]

Inspired by modern RAG systems like LangChain, LlamaIndex

📄 License
MIT License

yaml
Copy
Edit

---

## ✅ To Use It Now

Just create a `README.md` file in your root folder and paste the above content.

---

Would you like me to generate:

- `requirements.txt` for you?
- Add FastAPI interface?
- Publish this to GitHub with a badge?

Let’s make this production-ready 🚀

