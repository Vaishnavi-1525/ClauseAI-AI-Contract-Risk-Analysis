# 🚀 ClauseAI – AI-Powered Contract Risk Analysis System

- Multi-Agent LLM System · LangGraph · PDF Generator · Dashboard · Legal/Finance/Compliance Analyzer

- ClauseAI is an advanced AI-based Contract Risk Analysis System that analyzes legal agreements using a multi-agent architecture, identifies legal, financial, and compliance risks, and generates a professional PDF report along with a risk scoring dashboard.

- This project uses LangGraph, Gemini 2.5 Flash AI, and Flask, making it a complete end-to-end intelligent system.

---

## 📘 Project Overview

- Real-world contracts contain hidden risks that non-legal professionals cannot understand easily. ClauseAI solves this by using AI agents that specialize in:

- ✅ Legal Risks
- ✅ Financial Risks 
- ✅ Compliance Risks

- The system reads PDF/DOCX contracts, extracts key clauses, analyzes them using multiple AI agents running in parallel, refines the results, and produces:

- ✔ A complete structured analysis
- ✔ A downloadable PDF report
- ✔ A dashboard with a 0–100 risk score
- ✔ A clear executive summary

---

## 🎯 Why This Project?

- Traditional contract review is:

- ❌ Slow
- ❌ Manual
- ❌ Complex
- ❌ Requires legal expertise

- ClauseAI makes this process:

- ✨ Fast
- ✨ Automated
- ✨ Accurate
- ✨ Beginner-friendly

- Businesses, freelancers, agencies, and legal teams can use it for quick pre-screening of contracts before final review.

---

## ⭐ Key Features
#### 🔹 1. Multi-Agent AI Architecture
- 3 specialized agents:
- Legal Agent
- Finance Agent
- Compliance Agent
- Agents run in parallel for fast analysis.
#### 🔹 2. AI Planning System (LangGraph)
- Automatically detects what domains are required.
- Builds execution path for agents.
#### 🔹 3. AI Clause Extraction
- Extracts meaningful sections from long contracts.
#### 🔹 4. Risk Scoring Engine
- Assigns a 0–100 score based on contract severity.
#### 🔹 5. Beautiful Dashboard
- Displays score visually on a modern UI.
#### 🔹 6. Professional PDF Report Generation
- Fully formatted PDF
- Auto-generated summary
- Clean layout
#### 🔹 7. API Support
- Use /api/analyze to integrate with other applications.
#### 🔹 8. Document Upload Support
- Supports PDF
- Supports DOCX

---

## 🧱 System Architecture
- Contract → Planning → Multi-Agent Analysis → Aggregation → PDF Report → Score Dashboard
- Components
- planning_module.py → Decides required domains
- agents.py → 3 intelligent agents
- analysis_nodes.py → Run agents in parallel
- aggregator.py → Combine results, refine output, generate summary, risk score
- pdf_generator.py → Build professional PDF
- dashboard → Shows risk score
- document_loader.py → Reads PDF/DOCX files
- app.py → Main Flask server

---

## 🧠 Tech Stack
- Category	Technology
- Backend	Python, Flask
- AI	Gemini 2.5 Flash (Google), LangChain, LangGraph
- UI	HTML, TailwindCSS
- File Parsing	PyPDF, python-docx
- Report Generation	ReportLab
- Storage (Optional)	Pinecone Vector DB

---

## 🖥️ How to Run Locally
- 1. Clone Repo
- git clone https://github.com/yourusername/ClauseAI
- cd ClauseAI
- 2. Install Dependencies
- pip install -r requirements.txt
- 3. Add Your API Key

- Create a .env file:

- GOOGLE_API_KEY=your_key_here
- 4. Run App
- python app.py
- 5. Open Browser
- http://127.0.0.1:5000

---

#### 📑 How the System Works (Step-by-Step)
- 1. User uploads PDF/DOCX or enters text.

- → app.py reads it and passes to graph.

- 2. AI Planning

- → Determines required domains
- → Decides execution order

- 3. Clause Extraction

- → Splits contract into meaningful sections

- 4. Multi-Agent Execution

- → 3 agents analyze text in parallel

- 5. Aggregation

- → Combines outputs
- → Improves the writing
- → Creates summary
- → Assigns risk score

- 6. Final Output
- On-screen report
- PDF file
- Dashboard link

#### 🚨 Advantages

- ✔ 100% automated
- ✔ Very fast compared to manual review
- ✔ Multi-agent intelligence
- ✔ Dashboard & PDF output
- ✔ Easy to integrate with company workflows
- ✔ Simple, modern UI
- ✔ Supports real contracts

---

🌟 Future Improvements
#### Live chat with contract ("Ask your contract")
- Clause highlighting inside PDF
- AI suggestions & fixes
- Version comparison
- Multi-model support (OpenAI, Claude, Gemini, Groq)

  ---
  
## 🏆 Conclusion

- ClauseAI transforms complex legal contracts into simple, actionable analysis using advanced AI pipelines.
- It is production-ready, scalable, and demonstrates strong skills in:

- AI agent workflows
- LangGraph automation
- Prompt engineering
- PDF generation
- Backend development
- Full-stack UI integration
