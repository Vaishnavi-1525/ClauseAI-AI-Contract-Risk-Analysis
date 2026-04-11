from flask import Flask, render_template, request, send_file, jsonify, redirect, url_for, session
import os
from markupsafe import Markup
import re
import uuid
from datetime import datetime, timedelta

# Your modules
from docx_generator import generate_docx
from graph_builder import build_graph
from document_loader import load_document
from pdf_generator import generate_pdf
from vector_store import store_data
from llm_setup import groq_llm

# Firebase
from firebase_config import auth
from firebase_admin import firestore
from functools import wraps
from werkzeug.security import check_password_hash, generate_password_hash

db = firestore.client()


import os                                    # store report locally for the  history
from datetime import datetime
from flask import jsonify, session           

# ============================================
# FLASK SETUP
# ============================================

app = Flask(__name__)
app.secret_key = "SUPER_SECRET_KEY_123"
app.permanent_session_lifetime = timedelta(days=7)  # ✅ FIX 1: Set session lifetime

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

LAST_GENERATED_FILE = None
LAST_RESULTS = None


# ============================================
# AUTHENTICATION DECORATOR
# ============================================

def login_required(route_function):
    @wraps(route_function)
    def wrapper(*args, **kwargs):
        if "user" not in session:
            return redirect(url_for("login"))
        return route_function(*args, **kwargs)
    return wrapper


@app.route("/sessionLogin", methods=["POST"])
def session_login():
    data = request.get_json()
    print("SESSION LOGIN DATA:", data)
    email = data.get("email")

    if email:
        session.permanent = True        # ✅ Already correct here
        session["user"] = email
        print("SESSION STORED:", session)
        return jsonify({"status": "success"})

    return jsonify({"status": "fail"}), 400


# ============================================
# FIREBASE LOGIN  ← MAIN FIX IS HERE
# ============================================

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email    = request.form.get("email")
        password = request.form.get("password")

        import requests, os
        api_key = os.getenv("FIREBASE_API_KEY")
        url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={api_key}"

        payload = {"email": email, "password": password, "returnSecureToken": True}
        response = requests.post(url, json=payload)
        data = response.json()

        if "idToken" in data:
            print("Logged in email:", email)
            session.permanent = True    # ✅ FIX 2: Make session permanent here too
            session["user"] = email
            print("SESSION SET:", session.get("user"))  # ✅ Debug confirm
            return redirect(url_for("index"))
        else:
            error_msg = data.get('error', {}).get('message', 'Unknown error')
            print("Login failed:", error_msg)
            return render_template("login.html", error=error_msg)  # ✅ FIX 3: Return to login with error, not raw string

    return render_template("login.html")


# ============================================
# LOGOUT
# ============================================

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


# ============================================
# FIREBASE REGISTER
# ============================================

@app.route("/register")
def register_page():
    return render_template("registration.html")


# ============================================
# FETCH USER FROM FIRESTORE
# ============================================

def get_user_data(email):
    try:
        print("Fetching user:", email)
        users_ref = db.collection("users")
        query = users_ref.where("email", "==", email).get()
        print("Query result:", query)

        if query:
            user = query[0].to_dict()
            print("User found:", user)
            return user

        print("No user found in DB")
        return None

    except Exception as e:
        print("Firestore Error:", e)
        return None


# ============================================
# CHANGE PASSWORD
# ============================================

@app.route("/change-password", methods=["GET", "POST"])
@login_required
def change_password():
    email = session.get("user")

    if request.method == "GET":
        return render_template("change_password.html")

    current_password = request.form.get("current_password")
    new_password     = request.form.get("new_password")
    confirm_password = request.form.get("confirm_password")

    if new_password != confirm_password:
        return "Passwords do not match", 400

    try:
        user = auth.get_user_by_email(email)
        auth.update_user(user.uid, password=new_password)
        return redirect("/index")

    except Exception as e:
        return str(e), 400


# ============================================
# DASHBOARD / HOME
# ============================================

@app.route("/")
def dashboard():
    return render_template("dashboard.html")


@app.route("/index")
@login_required
def index():
    email = session.get("user")
    print("SESSION VALUE IN INDEX:", email)

    user_data = get_user_data(email)
    print("USER DATA:", user_data)

    user_name = "User"
    if user_data:
        user_name = user_data.get("name", "User")

    return render_template("index.html", user_name=user_name)


# ============================================
# SUMMARIZER
# ============================================

def summarize_for_web(full_text):
    text = str(full_text).replace("\n\n", "\n").strip()
    lines = text.split("\n")
    summary = []

    KEY_SECTIONS = [
        "Risk", "Payment", "Penalty", "Cost",
        "Financial", "Exposure", "Concern",
        "Issue", "Refund", "Liability", "Recommendation"
    ]

    for line in lines:
        clean = line.strip()
        if any(key.lower() in clean.lower() for key in KEY_SECTIONS):
            summary.append(clean)
        if clean[:1].isdigit() and clean[1:2] == ".":
            summary.append(clean)

    if len(summary) == 0:
        return text[:600] + "..."

    return "\n".join(summary[:10])


# ============================================
# CLAUSE HIGHLIGHTING
# ============================================

def extract_risky_clauses(analysis_text):
    pattern = r'Clause:\s*"(.*?)"'
    return re.findall(pattern, analysis_text)


def highlight_clauses(contract_text, risky_clauses):
    for clause in risky_clauses:
        if clause in contract_text:
            contract_text = contract_text.replace(
                clause,
                f"<mark style='background-color:#ff4d4d; color:white; padding:2px; border-radius:4px'>{clause}</mark>"
            )
    return contract_text


# ============================================
# ANALYZE CONTRACT
# ============================================

@app.route('/analyze', methods=['POST'])
@login_required
def analyze():
    global LAST_GENERATED_FILE, LAST_RESULTS

    # 1. HANDLE INPUT
    file = request.files.get("file")
    if file and file.filename != "":
        filepath = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
        file.save(filepath)
        contract_text = load_document(filepath)
        uploaded_filename = file.filename
    else:
        contract_text = request.form.get("clause")
        uploaded_filename = "Contract.txt"

    if not contract_text:
        return "No contract text provided", 400

    # 2. PROCESS ANALYSIS
    store_data(str(uuid.uuid4()), contract_text)
    graph = build_graph()
    state = {"contract_text": contract_text}
    result_state = graph.invoke(state)
    full_results = result_state.get("final_report", {})

    full_results["Suggestions"] = """
1. Define clear refund policy
2. Add proper IP ownership clause
3. Improve data protection compliance (GDPR/IT Act)
4. Add milestone-based delivery terms
"""
    full_results["Contract Name"] = uploaded_filename

    # 3. CLAUSE HIGHLIGHTING LOGIC
    all_risky_clauses = []
    for key in ["Legal Analysis", "Finance Analysis", "Compliance Analysis"]:
        if key in full_results:
            extracted = extract_risky_clauses(full_results[key])
            all_risky_clauses.extend(extracted)

    highlighted_contract = highlight_clauses(contract_text, all_risky_clauses)

    # 4. SUMMARIZATION FOR WEB
    short_results = full_results.copy()
    for key in ["Legal Analysis", "Finance Analysis", "Compliance Analysis"]:
        if key in full_results:
            short_results[key] = summarize_for_web(full_results[key])

    # 5. PREPARE DOWNLOAD INFO
    filename = f"{uploaded_filename}_Report.pdf"
    LAST_GENERATED_FILE = filename
    LAST_RESULTS = full_results

    # 6. RISK SCORING & CHART DATA (FIXED IMPORT NAME HERE)
    # --- CHANGED LINE BELOW ---
    from risk_scoring import calculate_risk_score
    legal, finance, compliance = calculate_risk_score(contract_text)
    # --------------------------

    risk_score_text = full_results.get("Risk Score", "0/100")
    risk_score = risk_score_text.split("/")[0]
    confidence = str(full_results.get("Confidence", "N/A")) + "%"

    formatted_results = {}
    for key, value in short_results.items():
        formatted_results[key] = Markup(str(value).replace("\n", "<br>"))

    # 7. DATABASE SAVE & ID GENERATION
    report_id = str(uuid.uuid4())
    db.collection("reports").document(report_id).set({
        "email": session.get("user"),
        "results": full_results,
        "created_at": datetime.now()
    })

    # 8. RENDER
    return render_template(
        "result.html",
        results=formatted_results,
        score=risk_score,
        confidence=confidence,
        pdf_ready=True,
        highlighted_contract=Markup(highlighted_contract),
        contract_name=uploaded_filename,
        report_id=report_id,
        chart_data={
            "legal": legal or 0,
            "finance": finance or 0,
            "compliance": compliance or 0
        }
    )



# History
@app.route("/history")
@login_required
def history():
    email = session.get("user").lower()
    folder = f"static/reports/{email}"

    history = []

    if os.path.exists(folder):
        for file in os.listdir(folder):
            path = f"/static/reports/{email}/{file}"

            history.append({
                "name": file,
                "url": path,
                "date": datetime.fromtimestamp(
                    os.path.getmtime(os.path.join(folder, file))
                ).strftime("%Y-%m-%d %H:%M")
            })

    history.sort(key=lambda x: x["date"], reverse=True)

    return jsonify(history)





@app.route("/history-page")
@login_required
def history_page():
    return render_template("history.html")



# delete history file 
@app.route("/delete-report", methods=["POST"])
@login_required
def delete_report():
    data = request.get_json()
    file_name = data.get("file_name")

    email = session.get("user").lower()
    folder = f"static/reports/{email}"
    file_path = os.path.join(folder, file_name)

    if os.path.exists(file_path):
        os.remove(file_path)
        return jsonify({"status": "success"})
    else:
        return jsonify({"status": "fail", "message": "File not found"}), 404



# ============================================
# CHATBOT
# ============================================

@app.route("/chat", methods=["POST"])
@login_required
def chat():
    global LAST_RESULTS

    user_message = request.json.get("message")

    if not user_message:
        return jsonify({"reply": "No question received"}), 400

    if not LAST_RESULTS:
        return jsonify({"reply": "Please analyze a contract first."})

    context = f"""
SUMMARY:
{LAST_RESULTS.get("Summary", "")}

LEGAL RISKS:
{LAST_RESULTS.get("Legal Analysis", "")}

FINANCIAL RISKS:
{LAST_RESULTS.get("Finance Analysis", "")}

COMPLIANCE RISKS:
{LAST_RESULTS.get("Compliance Analysis", "")}
"""

    prompt = f"""
You are ClauseAI, a professional AI Contract Assistant.

Rules:
- Answer ONLY using the analysis
- If question is unrelated, respond: "I only answer contract-related questions."
- Keep answers short and professional

CONTEXT:
{context[:3000]}

USER QUESTION:
{user_message}
"""

    try:
        response = groq_llm.invoke(prompt)
        reply = response.content.strip()
        return jsonify({"reply": reply})
    except Exception:
        return jsonify({"reply": "AI is temporarily unavailable."})


# ============================================
# DOWNLOAD
# ============================================

@app.route("/download")
@login_required
def download_file():
    global LAST_RESULTS

    if not LAST_RESULTS:
        return "No analysis found", 400

    tone = request.args.get("tone", "Neutral")
    file_format = request.args.get("format", "pdf")

    email = session.get("user").lower()

    username = "Vaishnavi_A_Kanade"
    now = datetime.now().strftime("%Y-%m-%d_%H-%M")

    project_name = LAST_RESULTS.get("Contract Name", "Contract")
    safe_name = project_name.replace(" ", "_").replace("/", "_")

    final_name = f"{safe_name}_{username}_{now}_{tone}.{file_format}"

    # ✅ SAVE IN USER FOLDER
    folder = f"static/reports/{email}"
    os.makedirs(folder, exist_ok=True)

    save_path = os.path.join(folder, final_name)

    try:
        if file_format == "docx":
            generate_docx(LAST_RESULTS, save_path, tone=tone)
        else:
            generate_pdf(LAST_RESULTS, save_path, tone=tone)
    except Exception as e:
        return f"Error generating file: {e}", 500

    # ✅ DOWNLOAD + SAVE BOTH
    return send_file(save_path, as_attachment=True)


# ============================================
# RUN SERVER
# ============================================

import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
