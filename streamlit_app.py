import json
import requests
import streamlit as st
import streamlit.components.v1 as components

from utils.pdf_generator import generate_pdf

API_URL = "http://127.0.0.1:8000/apply-loan"
CHAT_URL = "http://127.0.0.1:8000/chat-about-application"

st.set_page_config(page_title="Multi-Agent Loan Approval", page_icon="🏦", layout="wide")

DEFAULT_SESSION_VALUES = {
    "is_logged_in": False,
    "logged_in_name": "",
    "logged_in_email": "",
    "last_result": None,
    "chat_history": [],
    "chat_prompt_buffer": "",   # single source of truth for textarea pre-fill
    "_last_vb": "",
    "_last_vp": "",
}

for key, value in DEFAULT_SESSION_VALUES.items():
    if key not in st.session_state:
        st.session_state[key] = value


def speak_text(text: str):
    escaped_text = json.dumps(text)
    components.html(
        f"""
        <script>
        const utterance = new SpeechSynthesisUtterance({escaped_text});
        utterance.rate = 1;
        utterance.pitch = 1;
        window.speechSynthesis.cancel();
        window.speechSynthesis.speak(utterance);
        </script>
        """,
        height=0,
    )


def build_chat_context(result: dict) -> dict:
    return {
        "decision": result["decision"],
        "risk_score": result["risk_score"],
        "risk_band": result["risk_band"],
        "interest_rate": result["interest_rate"],
        "emi": result["emi"],
        "kyc_status": result["kyc_status"],
        "foir": result["foir"],
        "loan_to_value_ratio": result["loan_to_value_ratio"],
        "message": result["message"],
        "explanation": result["explanation"],
        "underwriting_reasons": result["underwriting_reasons"],
        "risk_factors": result["risk_factors"],
        "recommendations": result["recommendations"],
        "verification": result["verification"],
        "macro_signals": result["macro_signals"],
        "application_snapshot": result["application_snapshot"],
    }


st.markdown(
    """
    <style>
    .stApp {
        background:
            radial-gradient(circle at top left, rgba(253, 186, 116, 0.22), transparent 28%),
            radial-gradient(circle at top right, rgba(125, 211, 252, 0.18), transparent 24%),
            linear-gradient(160deg, #f8fafc 0%, #fff7ed 42%, #ecfeff 100%);
    }
    .hero {
        padding: 24px;
        border-radius: 24px;
        background: rgba(255,255,255,0.82);
        border: 1px solid rgba(15, 23, 42, 0.08);
        box-shadow: 0 18px 60px rgba(15, 23, 42, 0.08);
        margin-bottom: 18px;
    }
    .metric-card {
        padding: 16px;
        border-radius: 18px;
        background: rgba(255,255,255,0.9);
        border: 1px solid rgba(15, 23, 42, 0.08);
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="hero">
        <h1 style="margin:0;color:#0f172a;">Multi-Agent Loan Approval System</h1>
        <p style="margin:8px 0 0;color:#334155;">
            LangGraph multiagent with master, KYC, verification, underwriting, risk, recommendation, explanation, and sales agents.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

if not st.session_state.is_logged_in:
    with st.form("login_form"):
        st.subheader("Login")
        login_name = st.text_input("Full Name")
        login_email = st.text_input("Email")
        login_submitted = st.form_submit_button("Continue")

        if login_submitted:
            if not login_name.strip() or not login_email.strip():
                st.error("Enter both name and email to continue.")
            else:
                st.session_state.is_logged_in = True
                st.session_state.logged_in_name = login_name.strip()
                st.session_state.logged_in_email = login_email.strip()
                st.rerun()
    st.stop()

with st.form("loan_form"):
    st.subheader("Applicant Profile")
    col1, col2, col3 = st.columns(3)
    with col1:
        name = st.text_input("Name", value=st.session_state.logged_in_name)
        email = st.text_input("Email", value=st.session_state.logged_in_email)
        phone = st.text_input("Phone", value="9876543210")
        age = st.number_input("Age", min_value=18, max_value=70, value=29)
        address = st.text_input("Address", value="12 MG Road")
    with col2:
        city = st.text_input("City", value="Bengaluru")
        state_name = st.text_input("State", value="Karnataka")
        income = st.number_input("Monthly Income (INR)", min_value=0.0, value=85000.0, step=1000.0)
        monthly_expenses = st.number_input("Monthly Expenses (INR)", min_value=0.0, value=25000.0, step=1000.0)
        bank_balance = st.number_input("Bank Balance (INR)", min_value=0.0, value=175000.0, step=1000.0)
    with col3:
        credit_score = st.number_input("Credit Score", min_value=300, max_value=900, value=742)
        loan_amount = st.number_input("Loan Amount (INR)", min_value=0.0, value=650000.0, step=10000.0)
        loan_tenure_years = st.number_input("Tenure (Years)", min_value=1, max_value=30, value=5)
        existing_loans = st.number_input("Existing Loans Count", min_value=0, max_value=20, value=1)
        existing_emi = st.number_input("Existing EMI (INR)", min_value=0.0, value=7000.0, step=500.0)

    st.subheader("Employment and Security")
    col4, col5, col6 = st.columns(3)
    with col4:
        employment_type = st.selectbox(
            "Employment Type",
            ["salaried", "self-employed", "business", "freelancer", "student"],
            index=0,
        )
        employer_name = st.text_input("Employer / Business Name", value="Acme Tech")
        work_experience_years = st.number_input("Work Experience", min_value=0.0, max_value=50.0, value=4.0, step=0.5)
    with col5:
        collateral_type = st.selectbox("Collateral Type", ["none", "property", "vehicle", "fixed deposit", "gold"], index=1)
        collateral_value = st.number_input("Collateral Value (INR)", min_value=0.0, value=1200000.0, step=10000.0)
        loan_purpose = st.text_input("Loan Purpose", value="home renovation")
    with col6:
        has_pan = st.checkbox("PAN Available", value=True)
        has_aadhaar = st.checkbox("Aadhaar Available", value=True)
        consent_to_verify_contacts = st.checkbox("Use contact verification APIs", value=True)
        consent_to_fetch_financial_signals = st.checkbox("Use macro financial APIs", value=True)

    submitted = st.form_submit_button("Evaluate Application")

if submitted:
    payload = {
        "name": name,
        "email": email,
        "phone": phone,
        "age": age,
        "income": income,
        "credit_score": credit_score,
        "loan_amount": loan_amount,
        "loan_tenure_years": loan_tenure_years,
        "existing_loans": existing_loans,
        "existing_emi": existing_emi,
        "monthly_expenses": monthly_expenses,
        "bank_balance": bank_balance,
        "employment_type": employment_type,
        "employer_name": employer_name,
        "work_experience_years": work_experience_years,
        "collateral_type": collateral_type,
        "collateral_value": collateral_value,
        "loan_purpose": loan_purpose,
        "address": address,
        "city": city,
        "state": state_name,
        "country": "India",
        "has_pan": has_pan,
        "has_aadhaar": has_aadhaar,
        "consent_to_verify_contacts": consent_to_verify_contacts,
        "consent_to_fetch_financial_signals": consent_to_fetch_financial_signals,
    }

    try:
        with st.spinner("Running LangGraph multi-agent assessment..."):
            response = requests.post(API_URL, json=payload, timeout=60)
            response.raise_for_status()
            st.session_state.last_result = response.json()
            st.session_state.chat_history = []
            st.session_state.chat_prompt_buffer = ""
    except requests.RequestException as exc:
        st.error(f"Could not reach the backend API at {API_URL}. Details: {exc}")

result = st.session_state.last_result

if result:
    decision_color = {"APPROVED": "#166534", "REVIEW": "#92400e", "REJECTED": "#b91c1c"}.get(
        result["decision"], "#1d4ed8"
    )
    st.markdown(
        f"""
        <div class="metric-card">
            <h2 style="margin:0;color:{decision_color};">{result['decision']}</h2>
        </div>
        """,
        unsafe_allow_html=True,
    )

    speak_col, pdf_col = st.columns([1, 1])
    with speak_col:
        if st.button("Read Decision Aloud"):
            spoken_summary = (
                f"Decision: {result['decision']}. "
                f"Risk score: {result['risk_score']}. "
                f"KYC status: {result['kyc_status']}. "
                f"Estimated EMI: {result['emi']}. "
                f"{result['message']}"
            )
            speak_text(spoken_summary)
    with pdf_col:
        pdf_buffer = generate_pdf(
            {
                "name": result["application_snapshot"]["name"],
                "decision": result["decision"],
                "risk_score": result["risk_score"],
                "risk_band": result["risk_band"],
                "interest_rate": result["interest_rate"],
                "emi": result["emi"],
                "kyc_status": result["kyc_status"],
                "explanation": result["explanation"],
            }
        )
        st.download_button(
            "Download PDF Report",
            pdf_buffer,
            file_name="loan_decision_report.pdf",
            mime="application/pdf",
        )

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Risk Score", result["risk_score"])
    col2.metric("Risk Band", result["risk_band"])
    col3.metric("Interest Rate", f"{result['interest_rate']}%")
    col4.metric("Estimated EMI", f"INR {result['emi']}")

    col5, col6, col7 = st.columns(3)
    col5.metric("KYC Status", result["kyc_status"])
    col6.metric("FOIR", f"{result['foir']}%")
    ltv_value = "N/A" if result["loan_to_value_ratio"] is None else f"{result['loan_to_value_ratio']}%"
    col7.metric("LTV", ltv_value)

    st.subheader("Customer Message")
    st.write(result["message"])

    st.subheader("What To Improve")
    st.write(result["recommendations"])

    st.subheader("Underwriting Reasons")
    st.write(result["underwriting_reasons"])

    st.subheader("Risk Factors")
    st.write(result["risk_factors"])

    st.subheader("Verification Snapshot")
    st.json(result["verification"])

    st.subheader("KYC Summary")
    st.json({"checks": result["kyc_checks"], "flags": result["kyc_flags"], "status": result["kyc_status"]})

    st.subheader("Macro Signals")
    st.json(result["macro_signals"])

   # ── Loan Decision Chatbot ──────────────────────────────────────────────────
    st.subheader("Loan Decision Chatbot")
    st.caption(
        "Ask follow-up questions about the current decision, risk profile, "
        "or how to improve future approval chances."
    )
    if "chat_prompt_buffer" not in st.session_state:
        st.session_state["chat_prompt_buffer"] = ""

    if "chat_error_flash" not in st.session_state:
        st.session_state["chat_error_flash"] = ""

    if "_last_vb" not in st.session_state:
        st.session_state["_last_vb"] = ""
    # 1. Display Chat History
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    # 2. Define the Send Callback (The Core Fix)
    def handle_chat_submission():
    # ✅ Read directly from buffer (this is what your UI uses)
        question = st.session_state.chat_prompt_buffer.strip()
        if not question:
            st.session_state["chat_error_flash"] = "Enter or dictate a question first."
            return

        if "chat_error_flash" in st.session_state:
            del st.session_state["chat_error_flash"]

        st.session_state.chat_history.append({"role": "user", "content": question})

        try:
            chat_response = requests.post(
                CHAT_URL,
                json={"question": question, "context": build_chat_context(result)},
                timeout=45,
            )
            chat_response.raise_for_status()
            answer = chat_response.json().get("answer", "I could not generate an answer right now.")
        except Exception as exc:
            answer = f"Could not reach the chatbot backend. Details: {exc}"

        st.session_state.chat_history.append({"role": "assistant", "content": answer})

        # ✅ Clear ONLY buffer (not widget key)
        st.session_state["clear_input"] = True
        st.session_state["_last_vb"] = ""

        st.rerun()

    # 3. Hidden voice bridge
    st.markdown(
        "<style>"
        "div[data-testid='stTextInput']:has(input[placeholder='__vb__'])"
        "{visibility:hidden;height:0;overflow:hidden;margin:0;padding:0;}"
        "</style>",
        unsafe_allow_html=True,
    )
    
    voice_bridge = st.text_input(
        "_vb",
        value="",
        placeholder="__vb__",
        label_visibility="collapsed",
        key="voice_bridge",
    )

    if voice_bridge and voice_bridge != st.session_state.get("_last_vb", ""):
        st.session_state["chat_prompt_buffer"] = voice_bridge
        st.session_state["_last_vb"] = voice_bridge
        st.rerun()

    # URL-param fallback
    if "voice" in st.query_params:
        vp = st.query_params["voice"]
        if vp and vp != st.session_state.get("_last_vp", ""):
            st.session_state["chat_prompt_buffer"] = vp
            st.session_state["_last_vp"] = vp
            st.query_params.clear()
            st.rerun()

    # 4. Mic button (Web Speech API via components.html)
    mic_html = """
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { background: transparent; font-family: 'Segoe UI', -apple-system, sans-serif; }
        #micBtn {
            display: inline-flex; align-items: center; justify-content: center; gap: 7px;
            width: 100%; height: 38px; padding: 0 14px; border-radius: 10px;
            border: 1.5px solid #cbd5e1; background: #ffffff; color: #334155;
            font-size: 13px; font-weight: 500; cursor: pointer; font-family: inherit;
            transition: background 0.18s, border-color 0.18s, box-shadow 0.18s;
        }
        #micBtn:hover { background: #f8fafc; border-color: #94a3b8; }
        #micBtn.listening {
            border-color: #ef4444; background: #fff5f5; color: #dc2626;
            animation: pulse 1.2s infinite;
        }
        #micBtn:disabled { opacity: 0.45; cursor: not-allowed; }
        @keyframes pulse {
            0%   { box-shadow: 0 0 0 0 rgba(239,68,68,0.35); }
            70%  { box-shadow: 0 0 0 7px rgba(239,68,68,0); }
            100% { box-shadow: 0 0 0 0 rgba(239,68,68,0); }
        }
        #hint { margin-top: 4px; font-size: 11px; color: #94a3b8; text-align: center; min-height: 14px; }
        #hint.active { color: #ef4444; }
        #hint.done   { color: #16a34a; }
        #hint.err    { color: #dc2626; }
    </style>

    <button id="micBtn" onclick="toggleMic()">🎤 Speak</button>
    <div id="hint"></div>

    <script>
        var SR = window.SpeechRecognition || window.webkitSpeechRecognition;
        var rec = null, going = false, final_ = "";
        var btn  = document.getElementById("micBtn");
        var hint = document.getElementById("hint");

        if (!SR) {
            hint.textContent = "Voice needs Chrome/Edge";
            hint.className = "err";
            btn.disabled = true;
        }

        function sh(t, c) { hint.textContent = t; hint.className = c || ""; }
        function toggleMic() { going ? stopRec() : startRec(); }

        function startRec() {
            final_ = "";
            rec = new SR();
            rec.lang = "en-IN";
            rec.continuous = true;
            rec.interimResults = true;

            rec.onstart = function () {
                going = true;
                btn.classList.add("listening");
                btn.innerHTML = "⏹ Stop";
                sh("Listening…", "active");
            };

            rec.onresult = function (e) {
                var interim = "";
                for (var i = e.resultIndex; i < e.results.length; i++) {
                    if (e.results[i].isFinal) final_ += e.results[i][0].transcript + " ";
                    else interim += e.results[i][0].transcript;
                }
                fillTextarea((final_ + interim).trim());
            };

            rec.onend = function () {
                resetBtn();
                var t = final_.trim();
                if (t) {
                    sh("", "");
                    fillTextarea(t);
                    pushBridge(t);
                } else {
                    sh("Nothing heard", "err");
                }
            };
            rec.start();
        }

        function stopRec() { if (rec) rec.stop(); }
        function resetBtn() {
            going = false;
            btn.classList.remove("listening");
            btn.innerHTML = "🎤 Speak";
        }

        function fillTextarea(text) {
            try {
                var doc = window.parent.document;
                var tas = doc.querySelectorAll("textarea");
                var ta = null;
                for (var i = 0; i < tas.length; i++) {
                    if (tas[i].placeholder && tas[i].placeholder.includes("loan rejected")) {
                        ta = tas[i]; break;
                    }
                }
                if (!ta && tas.length) ta = tas[tas.length - 1];
                if (ta) {
                    var setter = Object.getOwnPropertyDescriptor(window.HTMLTextAreaElement.prototype, "value").set;
                    setter.call(ta, text);
                    ta.dispatchEvent(new Event("input", { bubbles: true }));
                    ta.dispatchEvent(new Event("change", { bubbles: true }));
                }
            } catch (e) { console.log("fillTextarea error:", e); }
        }

        function pushBridge(text) {
            try {
                var doc = window.parent.document;
                var inp = null;
                var all = doc.querySelectorAll("input");
                for (var i = 0; i < all.length; i++) {
                    if (all[i].placeholder === "__vb__") { inp = all[i]; break; }
                }
                if (inp) {
                    var s = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, "value").set;
                    s.call(inp, text);
                    inp.dispatchEvent(new Event("input", { bubbles: true }));
                    inp.dispatchEvent(new Event("change", { bubbles: true }));
                }
            } catch (e) { console.log("pushBridge error:", e); }
        }
    </script>
    """
    if "clear_input" not in st.session_state:
        st.session_state["clear_input"] = False

    if st.session_state["clear_input"]:
        st.session_state["chat_prompt_buffer"] = ""
        st.session_state["clear_input"] = False
    # 5. The Text Input Area
    st.text_area(
    "Ask about this loan decision",
    key="chat_prompt_buffer",   # ✅ MAKE THIS THE KEY
    height=120,
    placeholder="Why was the loan rejected? What should improve first?"
)
    # Error message if the user tried to send an empty prompt
    if st.session_state.get("chat_error_flash"):
        st.warning(st.session_state["chat_error_flash"])

    # 6. Action Buttons
    mic_col, send_col, clear_col = st.columns([2, 3, 2])
    with mic_col:
        components.html(mic_html, height=58)
    
    with send_col:
        # THE FINAL FIX: Using on_click triggers the logic immediately before the rerun
        send_clicked = st.button("Send ➤", use_container_width=True)

        if send_clicked:
            handle_chat_submission()
            
    with clear_col:
        if st.button("Clear Chat", use_container_width=True):
            st.session_state.chat_history = []
            st.session_state["_last_vb"] = ""
            st.session_state["chat_error_flash"] = ""
            st.session_state["clear_input"] = True   # ✅ USE FLAG INSTEAD
            st.rerun()