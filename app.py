from flask import Flask, render_template, request, send_file, jsonify, redirect, url_for, session
import os
from markupsafe import Markup
import re
import uuid
from datetime import datetime, timedelta
from functools import wraps

# Your modules
from docx_generator import generate_docx

from document_loader import load_document
from pdf_generator import generate_pdf


# Firebase
from firebase_config import auth
from firebase_admin import firestore
from werkzeug.security import check_password_hash, generate_password_hash


app = Flask(__name__)

@app.route("/test")
def test():
    return "Server working"

db = None

try:
    db = firestore.client()
    print("✅ Firestore connected")
except Exception as e:
    print("❌ Firebase error:", e)

# ============================================
# FLASK SETUP
# ============================================



# IMPORTANT: FIX - secret key first
app.secret_key = "SUPER_SECRET_KEY_123"
app.permanent_session_lifetime = timedelta(days=7)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

LAST_GENERATED_FILE = None
LAST_RESULTS = None


# ============================================
# BASIC ROUTE (FIXED - ONLY ONE / ROUTE)
# ============================================

@app.route("/")
def home():
    return redirect(url_for("login"))   # FIX: Render-safe entry point


# ============================================
# AUTH DECORATOR
# ============================================

def login_required(route_function):
    @wraps(route_function)
    def wrapper(*args, **kwargs):
        if "user" not in session:
            return redirect(url_for("login"))
        return route_function(*args, **kwargs)
    return wrapper


# ============================================
# SESSION LOGIN
# ============================================

@app.route("/sessionLogin", methods=["POST"])
def session_login():
    data = request.get_json()
    email = data.get("email")

    if email:
        session.permanent = True
        session["user"] = email
        return jsonify({"status": "success"})

    return jsonify({"status": "fail"}), 400


# ============================================
# LOGIN
# ============================================

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        import requests
        api_key = os.getenv("FIREBASE_API_KEY")

        url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={api_key}"

        payload = {
            "email": email,
            "password": password,
            "returnSecureToken": True
        }

        response = requests.post(url, json=payload)
        data = response.json()

        if "idToken" in data:
            session.permanent = True
            session["user"] = email
            return redirect(url_for("index"))
        else:
            error_msg = data.get("error", {}).get("message", "Unknown error")
            return render_template("login.html", error=error_msg)

    return render_template("login.html")


# ============================================
# LOGOUT
# ============================================

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


# ============================================
# REGISTER PAGE
# ============================================

@app.route("/register")
def register_page():
    return render_template("registration.html")


# ============================================
# FIRESTORE USER FETCH
# ============================================

def get_user_data(email):
    try:
        users_ref = db.collection("users")
        query = users_ref.where("email", "==", email).get()

        if query:
            return query[0].to_dict()

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

    new_password = request.form.get("new_password")
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
# INDEX
# ============================================

@app.route("/index")
@login_required
def index():
    email = session.get("user")
    user_data = get_user_data(email)

    user_name = "User"
    if user_data:
        user_name = user_data.get("name", "User")

    return render_template("index.html", user_name=user_name)


# ============================================
# DASHBOARD (kept but FIXED)
# ============================================

@app.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html")


# ============================================
# UTIL FUNCTIONS
# ============================================

def summarize_for_web(full_text):
    text = str(full_text).replace("\n\n", "\n").strip()
    lines = text.split("\n")
    summary = []

    KEY_SECTIONS = ["Risk", "Payment", "Penalty", "Cost", "Financial", "Exposure"]

    for line in lines:
        clean = line.strip()
        if any(key.lower() in clean.lower() for key in KEY_SECTIONS):
            summary.append(clean)

    return "\n".join(summary[:10]) if summary else text[:600]


def extract_risky_clauses(analysis_text):
    return re.findall(r'Clause:\s*"(.*?)"', analysis_text)


def highlight_clauses(contract_text, risky_clauses):
    for clause in risky_clauses:
        if clause in contract_text:
            contract_text = contract_text.replace(
                clause,
                f"<mark style='background:#ff4d4d;color:white'>{clause}</mark>"
            )
    return contract_text


# ============================================
# ANALYZE
# ============================================

@app.route('/analyze', methods=['POST'])
@login_required
def analyze():
    from graph_builder import build_graph
    from vector_store import store_data
    global LAST_RESULTS

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

    store_data(str(uuid.uuid4()), contract_text)

    graph = build_graph()
    result_state = graph.invoke({"contract_text": contract_text})
    full_results = result_state.get("final_report", {})

    full_results["Contract Name"] = uploaded_filename

    risky_clauses = []
    for key in ["Legal Analysis", "Finance Analysis", "Compliance Analysis"]:
        if key in full_results:
            risky_clauses += extract_risky_clauses(full_results[key])

    highlighted = highlight_clauses(contract_text, risky_clauses)

    LAST_RESULTS = full_results

    report_id = str(uuid.uuid4())

    db.collection("reports").document(report_id).set({
        "email": session.get("user"),
        "results": full_results,
        "created_at": datetime.now()
    })

    return render_template(
        "result.html",
        results=full_results,
        highlighted_contract=Markup(highlighted),
        report_id=report_id
    )


# ============================================
# CHAT
# ============================================

@app.route("/chat", methods=["POST"])
@login_required
def chat():
    from llm_setup import groq_llm
    global LAST_RESULTS

    user_message = request.json.get("message")

    if not LAST_RESULTS:
        return jsonify({"reply": "Please analyze a contract first."})

    prompt = f"""
You are ClauseAI assistant.

CONTEXT:
{str(LAST_RESULTS)[:3000]}

QUESTION:
{user_message}
"""

    try:
        response = groq_llm.invoke(prompt)
        return jsonify({"reply": response.content})
    except:
        return jsonify({"reply": "AI error"})


# ============================================
# DOWNLOAD
# ============================================

@app.route("/download")
@login_required
def download_file():
    global LAST_RESULTS

    if not LAST_RESULTS:
        return "No analysis", 400

    email = session.get("user").lower()
    folder = f"static/reports/{email}"
    os.makedirs(folder, exist_ok=True)

    filename = f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    path = os.path.join(folder, filename)

    generate_pdf(LAST_RESULTS, path)

    return send_file(path, as_attachment=True)


# ============================================
# HISTORY
# ============================================

@app.route("/history")
@login_required
def history():
    email = session.get("user").lower()
    folder = f"static/reports/{email}"

    history = []

    if os.path.exists(folder):
        for f in os.listdir(folder):
            path = os.path.join(folder, f)
            history.append({
                "name": f,
                "url": f"/static/reports/{email}/{f}",
                "date": datetime.fromtimestamp(os.path.getmtime(path)).strftime("%Y-%m-%d %H:%M")
            })

    return jsonify(history)


@app.route("/history-page")
@login_required
def history_page():
    return render_template("history.html")


# ============================================
# DELETE
# ============================================

@app.route("/delete-report", methods=["POST"])
@login_required
def delete_report():
    data = request.get_json()
    file_name = data.get("file_name")

    email = session.get("user").lower()
    path = os.path.join("static/reports", email, file_name)

    if os.path.exists(path):
        os.remove(path)
        return jsonify({"status": "success"})

    return jsonify({"status": "fail"}), 404


# ============================================
# RUN (IMPORTANT FIX FOR RENDER)
# ============================================

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print("PORT:", port)
    app.run(host="0.0.0.0", port=port)
