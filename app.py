from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import json
from datetime import datetime
import urllib.request
import urllib.error

app = Flask(__name__)
app.secret_key = "bloodnet_secret_2024"

# ================================================================
# PASTE YOUR ANTHROPIC API KEY BELOW (get from console.anthropic.com)
import os
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
# ================================================================

CITIES = sorted([
    "Chennai", "Coimbatore", "Madurai", "Tiruchirappalli", "Salem",
    "Tirunelveli", "Vellore", "Erode", "Thoothukudi", "Dindigul",
    "Thanjavur", "Ranipet", "Sivakasi", "Hosur", "Karur",
    "Mumbai", "Pune", "Nagpur", "Nashik", "Aurangabad",
    "Solapur", "Kolhapur", "Thane", "Navi Mumbai", "Pimpri-Chinchwad",
    "Delhi", "Noida", "Gurgaon", "Faridabad", "Ghaziabad",
    "Agra", "Lucknow", "Kanpur", "Varanasi", "Allahabad",
    "Jaipur", "Jodhpur", "Udaipur", "Kota", "Ajmer",
    "Bangalore", "Mysore", "Hubli", "Mangalore", "Belgaum",
    "Dharwad", "Shimoga", "Tumkur", "Bijapur", "Gulbarga",
    "Hyderabad", "Visakhapatnam", "Vijayawada", "Guntur", "Warangal",
    "Nellore", "Kurnool", "Rajamahendravaram", "Tirupati", "Karimnagar",
    "Kochi", "Thiruvananthapuram", "Kozhikode", "Thrissur", "Kollam",
    "Palakkad", "Alappuzha", "Kannur", "Kottayam", "Malappuram",
    "Kolkata", "Howrah", "Durgapur", "Asansol", "Siliguri",
    "Ahmedabad", "Surat", "Vadodara", "Rajkot", "Bhavnagar",
    "Bhopal", "Indore", "Jabalpur", "Gwalior", "Ujjain",
    "Patna", "Ranchi", "Bhubaneswar", "Cuttack", "Raipur",
    "Chandigarh", "Amritsar", "Ludhiana", "Jalandhar", "Dehradun",
    "Guwahati", "Imphal", "Shillong", "Agartala", "Aizawl",
    "Jammu", "Srinagar", "Leh", "Shimla", "Manali",
    "Puducherry", "Port Blair", "Panaji", "Margao", "Vasco da Gama",
])

HOSPITALS = sorted([
    "Apollo Hospital Chennai", "Apollo Hospital Delhi", "Apollo Hospital Hyderabad",
    "Apollo Hospital Bangalore", "Apollo Hospital Kolkata", "Apollo Hospital Mumbai",
    "Apollo Specialty Hospital", "Apollo Children's Hospital",
    "Fortis Hospital Bangalore", "Fortis Hospital Delhi", "Fortis Hospital Mumbai",
    "Fortis Hospital Kolkata", "Fortis Memorial Research Institute Gurgaon",
    "Fortis Escorts Heart Institute Delhi",
    "AIIMS Delhi", "AIIMS Bhopal", "AIIMS Bhubaneswar", "AIIMS Jodhpur",
    "AIIMS Patna", "AIIMS Raipur", "AIIMS Rishikesh",
    "Max Super Speciality Hospital Delhi", "Max Hospital Noida",
    "Max Hospital Gurgaon", "Max Hospital Patparganj",
    "Narayana Health Bangalore", "Narayana Health Kolkata",
    "Narayana Health Ahmedabad", "Narayana Health Jaipur",
    "Manipal Hospital Bangalore", "Manipal Hospital Delhi",
    "Manipal Hospital Vijayawada", "Manipal Hospital Goa",
    "Medanta - The Medicity Gurgaon", "Medanta Hospital Lucknow",
    "Medanta Hospital Ranchi", "Medanta Hospital Indore",
    "Government General Hospital Chennai", "Government Medical College Kozhikode",
    "JIPMER Puducherry", "NIMHANS Bangalore", "PGI Chandigarh",
    "King George Medical University Lucknow", "Seth GS Medical College Mumbai",
    "Grant Medical College Mumbai", "Osmania General Hospital Hyderabad",
    "Rajiv Gandhi Government General Hospital Chennai",
    "Christian Medical College Vellore", "Christian Medical College Ludhiana",
    "Kauvery Hospital Chennai", "Kauvery Hospital Trichy",
    "MIOT International Chennai", "MGM Healthcare Chennai",
    "Sri Ramachandra Institute Chennai", "Kovai Medical Center Coimbatore",
    "PSG Hospital Coimbatore", "Meenakshi Mission Hospital Madurai",
    "Aravind Eye Hospital Madurai", "SRM Hospital Chennai",
    "Chettinad Health City Chennai", "Gleneagles Global Hospital Chennai",
    "Kokilaben Dhirubhai Ambani Hospital Mumbai", "Lilavati Hospital Mumbai",
    "Breach Candy Hospital Mumbai", "Hinduja Hospital Mumbai",
    "Jaslok Hospital Mumbai", "Bombay Hospital Mumbai",
    "KEM Hospital Mumbai", "Wockhardt Hospital Mumbai",
    "Aster CMI Hospital Bangalore", "Columbia Asia Hospital Bangalore",
    "Vikram Hospital Bangalore", "Sparsh Hospital Bangalore",
    "BGS Gleneagles Global Hospital Bangalore", "Sakra World Hospital Bangalore",
    "Yashoda Hospital Hyderabad", "Care Hospital Hyderabad",
    "Continental Hospital Hyderabad", "Star Hospital Hyderabad",
    "Kamineni Hospital Hyderabad", "KIMS Hospital Hyderabad",
    "Ruby Hall Clinic Pune", "Jehangir Hospital Pune",
    "Deenanath Mangeshkar Hospital Pune", "Sahyadri Hospital Pune",
    "Aster Hospital Kochi", "Lakeshore Hospital Kochi",
    "Amrita Institute of Medical Sciences Kochi",
    "Aster MIMS Kozhikode", "Baby Memorial Hospital Kozhikode",
    "Sunshine Hospital Hyderabad", "Nizam's Institute Hyderabad",
    "Medica Superspecialty Hospital Kolkata", "AMRI Hospital Kolkata",
    "Peerless Hospital Kolkata", "Belle Vue Clinic Kolkata",
    "BM Birla Heart Research Centre Kolkata",
])

donors = [
    {"id": 1,  "name": "Arjun Kumar",    "blood_type": "O+",  "phone": "9876543210", "city": "Chennai",   "available": True,  "last_donated": "2024-10-01"},
    {"id": 2,  "name": "Priya Sharma",   "blood_type": "A+",  "phone": "9876543211", "city": "Chennai",   "available": True,  "last_donated": "2024-09-15"},
    {"id": 3,  "name": "Rahul Verma",    "blood_type": "B+",  "phone": "9876543212", "city": "Mumbai",    "available": True,  "last_donated": "2024-08-20"},
    {"id": 4,  "name": "Sneha Patel",    "blood_type": "AB+", "phone": "9876543213", "city": "Chennai",   "available": True,  "last_donated": "2024-11-01"},
    {"id": 5,  "name": "Vikram Singh",   "blood_type": "O-",  "phone": "9876543214", "city": "Delhi",     "available": True,  "last_donated": "2024-07-10"},
    {"id": 6,  "name": "Anita Nair",     "blood_type": "A-",  "phone": "9876543215", "city": "Chennai",   "available": True,  "last_donated": "2024-10-20"},
    {"id": 7,  "name": "Karthik Raj",    "blood_type": "B-",  "phone": "9876543216", "city": "Bangalore", "available": False, "last_donated": "2024-12-01"},
    {"id": 8,  "name": "Divya Menon",    "blood_type": "O+",  "phone": "9876543217", "city": "Chennai",   "available": True,  "last_donated": "2024-09-05"},
    {"id": 9,  "name": "Suresh Babu",    "blood_type": "B+",  "phone": "9876543218", "city": "Bangalore", "available": True,  "last_donated": "2024-08-01"},
    {"id": 10, "name": "Meena Krishnan", "blood_type": "AB-", "phone": "9876543219", "city": "Mumbai",    "available": True,  "last_donated": "2024-07-15"},
    {"id": 11, "name": "Arun Prasad",    "blood_type": "O+",  "phone": "9876543220", "city": "Delhi",     "available": True,  "last_donated": "2024-06-20"},
    {"id": 12, "name": "Lakshmi Devi",   "blood_type": "A+",  "phone": "9876543221", "city": "Hyderabad", "available": True,  "last_donated": "2024-09-10"},
]

emergency_requests = []
users = []

COMPATIBILITY = {
    "O-":  ["O-", "O+", "A-", "A+", "B-", "B+", "AB-", "AB+"],
    "O+":  ["O+", "A+", "B+", "AB+"],
    "A-":  ["A-", "A+", "AB-", "AB+"],
    "A+":  ["A+", "AB+"],
    "B-":  ["B-", "B+", "AB-", "AB+"],
    "B+":  ["B+", "AB+"],
    "AB-": ["AB-", "AB+"],
    "AB+": ["AB+"],
}

def get_compatible_donors(needed_type, city=None):
    result = []
    for donor in donors:
        if donor["available"] and needed_type in COMPATIBILITY.get(donor["blood_type"], []):
            if not city or donor["city"].lower() == city.lower():
                result.append(donor)
    return result

def is_logged_in():
    return session.get("logged_in", False)

# ── PAGES ──────────────────────────────────────────────────────

@app.route("/")
def index():
    if not is_logged_in():
        return redirect(url_for("login_page"))
    return render_template("index.html",
        user=session.get("user_name", ""),
        user_role=session.get("user_role", "seeker"),
        cities=CITIES,
        hospitals=HOSPITALS
    )

@app.route("/login")
def login_page():
    if is_logged_in():
        return redirect(url_for("index"))
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login_page"))

# ── AUTH ───────────────────────────────────────────────────────

@app.route("/api/login", methods=["POST"])
def login():
    data = request.json
    phone = data.get("phone", "").strip()
    password = data.get("password", "").strip()
    user = next((u for u in users if u["phone"] == phone and u["password"] == password), None)
    if user:
        session["logged_in"] = True
        session["user_name"] = user["name"]
        session["user_phone"] = user["phone"]
        session["user_role"] = user.get("role", "seeker")
        return jsonify({"success": True, "message": f"Welcome back, {user['name']}!"})
    return jsonify({"success": False, "error": "Invalid phone number or password."}), 401

# ── REGISTER SEEKER (just wants to find blood, no donor info needed) ──
@app.route("/api/register-seeker", methods=["POST"])
def register_seeker():
    data = request.json
    for field in ["name", "phone", "password"]:
        if not data.get(field):
            return jsonify({"error": f"{field} is required"}), 400
    if any(u["phone"] == data["phone"] for u in users):
        return jsonify({"error": "Phone already registered. Please login."}), 400
    users.append({
        "name": data["name"],
        "phone": data["phone"],
        "password": data["password"],
        "role": "seeker",
        "blood_type": None,
        "city": data.get("city", "")
    })
    return jsonify({"success": True, "message": "Account created! Please login now."})

# ── REGISTER DONOR ─────────────────────────────────────────────
@app.route("/api/register-donor", methods=["POST"])
def register_donor():
    data = request.json
    for field in ["name", "blood_type", "phone", "city", "password"]:
        if not data.get(field):
            return jsonify({"error": f"{field} is required"}), 400
    if any(u["phone"] == data["phone"] for u in users):
        return jsonify({"error": "Phone already registered. Please login."}), 400
    donors.append({
        "id": len(donors) + 1,
        "name": data["name"], "blood_type": data["blood_type"],
        "phone": data["phone"], "city": data["city"],
        "available": True, "last_donated": data.get("last_donated", "Not yet")
    })
    users.append({
        "name": data["name"], "phone": data["phone"],
        "password": data["password"],
        "role": "donor",
        "blood_type": data["blood_type"],
        "city": data["city"]
    })
    return jsonify({"success": True, "message": "Registered as donor! Please login now."})

# ── FIND DONORS ────────────────────────────────────────────────

@app.route("/api/find-donors", methods=["POST"])
def find_donors():
    if not is_logged_in():
        return jsonify({"error": "Please login first.", "redirect": "/login"}), 401
    data = request.json
    blood_type = data.get("blood_type")
    city = data.get("city", "").strip()
    if not blood_type:
        return jsonify({"error": "Blood type is required"}), 400
    matched = get_compatible_donors(blood_type, city or None)
    exact = [d for d in matched if d["blood_type"] == blood_type]
    compatible = [d for d in matched if d["blood_type"] != blood_type]
    return jsonify({
        "success": True, "exact_matches": exact,
        "compatible_donors": compatible, "total": len(matched),
        "blood_type": blood_type, "city": city
    })

# ── EMERGENCY ──────────────────────────────────────────────────

@app.route("/api/emergency-request", methods=["POST"])
def emergency_request():
    if not is_logged_in():
        return jsonify({"error": "Please login first.", "redirect": "/login"}), 401
    data = request.json
    for field in ["patient_name", "blood_type", "hospital", "contact"]:
        if not data.get(field):
            return jsonify({"error": f"{field} is required"}), 400
    req = {
        "id": len(emergency_requests) + 1,
        "patient_name": data["patient_name"], "blood_type": data["blood_type"],
        "hospital": data["hospital"], "contact": data["contact"],
        "city": data.get("city", ""), "units_needed": data.get("units_needed", 1),
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "status": "active"
    }
    emergency_requests.append(req)
    matched = get_compatible_donors(data["blood_type"], data.get("city") or None)
    return jsonify({"success": True,
        "message": f"Emergency posted! Found {len(matched)} potential donors nearby.",
        "donors_found": len(matched)
    })

# ── AI CHAT ────────────────────────────────────────────────────

def smart_chat_engine(user_message, donors):
    msg = user_message.lower().strip()
    available = [d for d in donors if d["available"]]

    greetings = ["hi", "hello", "hey", "good morning", "good evening", "good afternoon", "hii", "helo"]
    if any(msg == g or msg.startswith(g + " ") for g in greetings):
        return "👋 Hello! I'm Blood Net AI Assistant.\n\nI can help you:\n🔍 Find blood donors by type and city\n🩸 Explain blood compatibility\n🚨 Guide you during emergencies\n\nJust tell me what you need! Example: \"I need O+ blood in Chennai\""

    if any(w in msg for w in ["thank", "thanks", "thank you", "thx", "ty"]):
        return "You're welcome! 🙏 Stay safe. If you need blood donors anytime, I'm here 24/7.\n\n📞 Emergency helpline: **104**"

    if msg in ["help", "what can you do", "how to use", "?"]:
        return "🤖 I can help you with:\n\n1️⃣ **Find donors** — say \"I need A+ blood in Mumbai\"\n2️⃣ **Check compatibility** — say \"Who can donate to O+?\"\n3️⃣ **Emergency help** — say \"Emergency O- blood needed\"\n4️⃣ **List donors** — say \"Show all donors\"\n5️⃣ **City search** — say \"Donors in Chennai\"\n\nWhat do you need?"

    blood_types = ["o+", "o-", "a+", "a-", "b+", "b-", "ab+", "ab-"]
    found_blood = None
    for bt in blood_types:
        variants = [bt, "o positive" if bt=="o+" else "", "o negative" if bt=="o-" else "",
                    "a positive" if bt=="a+" else "", "a negative" if bt=="a-" else "",
                    "b positive" if bt=="b+" else "", "b negative" if bt=="b-" else "",
                    "ab positive" if bt=="ab+" else "", "ab negative" if bt=="ab-" else ""]
        if any(v and v in msg for v in variants):
            found_blood = bt.upper()
            break

    found_city = None
    city_list = ["chennai", "mumbai", "delhi", "bangalore", "hyderabad", "kolkata",
                 "pune", "ahmedabad", "jaipur", "coimbatore", "madurai", "kochi",
                 "bhopal", "indore", "lucknow", "nagpur", "surat", "visakhapatnam",
                 "patna", "ranchi", "vellore", "erode", "salem", "trichy", "mysore",
                 "hubli", "mangalore", "noida", "gurgaon", "agra", "varanasi"]
    for city in city_list:
        if city in msg:
            found_city = city.title()
            break

    if any(w in msg for w in ["show all", "list all", "all donors", "how many donors", "total donors"]):
        if not available:
            return "😔 No donors are currently available.\n\nPlease post an Emergency Request!"
        reply = f"📋 **{len(available)} Available Donors:**\n\n"
        for d in available:
            reply += f"🩸 **{d['name']}** — {d['blood_type']} — 📍{d['city']} — 📞{d['phone']}\n"
        return reply

    compat_keywords = ["compatible", "compatibility", "who can donate", "can donate to", "receive from", "give blood to", "donate to"]
    if any(w in msg for w in compat_keywords):
        COMPAT_INFO = {
            "O-":  "O- (Universal Donor) can donate to: **ALL types!**",
            "O+":  "O+ can donate to: **O+, A+, B+, AB+**",
            "A-":  "A- can donate to: **A-, A+, AB-, AB+**",
            "A+":  "A+ can donate to: **A+, AB+**",
            "B-":  "B- can donate to: **B-, B+, AB-, AB+**",
            "B+":  "B+ can donate to: **B+, AB+**",
            "AB-": "AB- can donate to: **AB-, AB+**",
            "AB+": "AB+ can only donate to: **AB+**",
        }
        if found_blood and found_blood in COMPAT_INFO:
            return f"🩸 **{found_blood} Compatibility:**\n\n{COMPAT_INFO[found_blood]}\n\nNeed donors? Tell me your city!"
        reply = "🩸 **Blood Compatibility Chart:**\n\n"
        for bt, info in COMPAT_INFO.items():
            reply += f"• {info}\n"
        reply += "\n💡 O- is the Universal Donor | AB+ is the Universal Recipient"
        return reply

    emergency_words = ["emergency", "urgent", "critical", "immediately", "asap", "dying", "surgery", "accident", "operation"]
    is_emergency = any(w in msg for w in emergency_words)
    need_words = ["need", "require", "want", "looking for", "find", "search", "get", "blood"]
    donor_words = ["donor", "donate", "blood", "type"]
    is_donor_search = found_blood or any(w in msg for w in need_words + donor_words)

    if is_donor_search and found_blood:
        matched = [d for d in available if found_blood in COMPATIBILITY.get(d["blood_type"], [])]
        city_matched = [d for d in matched if d["city"].lower() == found_city.lower()] if found_city else matched
        exact = [d for d in city_matched if d["blood_type"] == found_blood]
        compatible = [d for d in city_matched if d["blood_type"] != found_blood]
        reply = f"{'🚨 **EMERGENCY — ' if is_emergency else '🔍 **Search Results: '}{found_blood} Blood{' in ' + found_city if found_city else ''}**\n\n"
        if not city_matched:
            reply += f"😔 No donors found for **{found_blood}**{' in ' + found_city if found_city else ''}.\n"
            reply += "\n👉 Please post an **Emergency Request** using the Emergency tab!\n📞 Call **104** for help."
            return reply
        if exact:
            reply += f"✅ **Exact Match ({found_blood}):**\n"
            for d in exact:
                reply += f"👤 **{d['name']}** | {d['blood_type']} | 📍{d['city']} | 📞 **{d['phone']}**\n"
        if compatible:
            reply += f"\n🔄 **Compatible Donors:**\n"
            for d in compatible:
                reply += f"👤 **{d['name']}** | {d['blood_type']} | 📍{d['city']} | 📞 **{d['phone']}**\n"
        reply += f"\n✅ Found **{len(exact)+len(compatible)} donor(s)** total."
        if is_emergency:
            reply += "\n\n🚨 Call them NOW and also post an Emergency Request!\n📞 Helpline: **104**"
        return reply

    if found_city and not found_blood:
        city_donors = [d for d in available if d["city"].lower() == found_city.lower()]
        if not city_donors:
            return f"😔 No donors currently available in **{found_city}**.\n\n📞 Call **104** for help."
        reply = f"📍 **Donors in {found_city} ({len(city_donors)} found):**\n\n"
        for d in city_donors:
            reply += f"🩸 **{d['name']}** — {d['blood_type']} — 📞{d['phone']}\n"
        reply += "\n💡 Tell me which blood type you need for a better match!"
        return reply

    if any(w in msg for w in ["donate", "how to donate", "want to donate", "become donor", "register"]):
        return "💉 **How to Become a Blood Donor:**\n\n1. Go to Login page → Register tab\n2. Choose **'I want to donate blood'**\n3. Fill your blood type, phone, city\n4. You're registered! People in need can contact you.\n\n✅ Donating blood saves up to **3 lives** per donation!\n📞 For camps & drives: Call **104**"

    return f"🤖 I'm here to help you find blood donors!\n\nTry asking me:\n• \"I need O+ blood in Chennai\"\n• \"Show donors in Mumbai\"\n• \"Who can donate to AB+?\"\n• \"Emergency B- blood needed\"\n\nCurrently **{len(available)} donors** are available. What do you need? 🩸"


@app.route("/api/chat", methods=["POST"])
def chat():
    if not is_logged_in():
        return jsonify({"error": "Please login first.", "redirect": "/login"}), 401
    data = request.json
    user_message = data.get("message", "").strip()
    if not user_message:
        return jsonify({"reply": "Please type a message."})
    reply = smart_chat_engine(user_message, donors)
    return jsonify({"reply": reply})

@app.route("/api/donors", methods=["GET"])
def get_all_donors():
    return jsonify({"donors": donors, "total": len(donors)})

if __name__ == "__main__":
    app.run(debug=True)
