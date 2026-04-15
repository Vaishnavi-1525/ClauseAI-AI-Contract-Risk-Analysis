# 🚀 ClauseAI – AI-Powered Contract Risk Analysis System

- An end-to-end Multi-Agent AI system that analyzes contracts, detects risks, and generates structured insights using RAG (Retrieval-Augmented Generation) and LLM orchestration.

- Built as part of the Infosys Springboard 6.0 Virtual Internship.

### 📌 Overview

- ClauseAI is designed to automate contract analysis, which is traditionally time-consuming and requires domain expertise.

### This system:

- Reads contracts (PDF/DOCX)
- Identifies risks across multiple domains
- Highlights risky clauses
- Generates structured reports
- Allows users to interact with the contract via chatbot

  
### ⚙️ Architecture

- The system follows a Multi-Agent AI Pipeline:
  
```
User Input (Contract)
        ↓
Planning Agent (Decides domains)
        ↓
Parallel AI Agents:
   - Legal Agent
   - Finance Agent
   - Compliance Agent
   - Operations Agent
        ↓
RAG (Context Retrieval via Pinecone)
        ↓
Aggregation Layer:
   - Combines outputs
   - Generates summary
   - Calculates risk score
        ↓
Output:
   - Risk Analysis
   - Highlighted Clauses
   - Chatbot Interaction
   - PDF/DOCX Reports
```


### ✨ Features
#####  🤖 AI & Analysis
- Multi-Agent AI architecture (LangGraph-based execution)
- Domain-wise risk detection:
- Legal
- Finance
- Compliance
- Operations
- Clause-level risk extraction & highlighting
- AI-powered summarization
- Context-aware analysis using RAG (Pinecone + embeddings)
##### 💬 Chatbot
- Ask questions directly from your contract
- Context-aware responses using analyzed results
##### 📄 Document Handling
- Upload PDF / DOCX contracts
- Automatic text extraction
- Highlight risky clauses visually
##### 📊 Reporting
- Risk score generation
- Structured analysis report
- Export as:
- PDF (with tone control)
- DOCX (with formatting & pagination)
##### 🔐 User Features
- Firebase Authentication (Login/Register)
- Session management
- User-specific report history
- Download previous reports
##### 🎨 UI/UX
- Clean web interface
- Real-time processing pipeline
- Visual risk insights
##### 🧠 Tech Stack
- Backend
- Python (Flask)
- LangGraph (multi-agent orchestration)
- AI / ML
- Google Gemini (planning, finance)
- Groq (LLaMA 3) (legal, compliance, chatbot)
- Sentence Transformers (embeddings)
- RAG Pipeline
- Pinecone (vector database)
- Frontend
- HTML, Tailwind CSS
- Database & Auth
- Firebase (Authentication + Firestore)
- Document Processing
- PyPDF
- python-docx
- ReportLab (PDF generation)

  ---
  
### 🚀 How It Works
- User uploads a contract (PDF/DOCX)
- Text is extracted and stored in vector database
- Planning Agent determines required analysis domains
- Multiple AI agents run in parallel
- Relevant context is retrieved using RAG
- Results are aggregated and refined
- Final output includes:
- Risk analysis
- Summary
- Risk score
- Highlighted contract
- User can:
- Download report
- Ask questions via chatbot

---

### 🔗 Live Demo

- 🌐 https://clauseai-ai-contract-risk-analysis.onrender.com

---

# 📦 Installation

```
git clone https://github.com/Vaishnavi-1525/ClauseAI-AI-Contract-Risk-Analysis.git
```


```
cd ClauseAI-AI-Contract-Risk-Analysis
```


Install dependencies


```
pip install -r requirements.txt
```


- Setup Environment Variables (.env)
- GOOGLE_API_KEY=your_key
- GROQ_API_KEY=your_key
- PINECONE_API_KEY=your_key



Run the app

```
python app.py
```



---

### 🔮 Future Improvements
- Multi-document comparison (which contract is better)
- Faster processing with async pipelines
- Advanced ML-based risk scoring
- Voice-based interaction
- Real-time collaboration
- Fine-tuned domain-specific models

---

### 💡 What I Learned

-This project helped me move beyond basic development and start thinking in terms of system design and real-world AI architecture, including multi-agent orchestration, RAG pipelines, parallel execution, and building end-to-end AI-powered applications.
