from flask import Flask, jsonify, render_template, request

app = Flask(__name__)

BOT_PROFILES = {
    "university": {
        "title": "University Admission Chatbot",
        "subtitle": "Admissions, deadlines, program info, and requirements.",
        "accent": "#6f42c1",
        "sample_prompts": [
            "What are the admission requirements?",
            "When is the application deadline?",
            "Do you offer scholarships?",
        ],
        "rules": [
            {
                "keywords": ["requirement", "requirements", "documents", "eligibility", "admission"],
                "response": "For admission, students usually need academic transcripts, a valid ID, passport-size photos, and the completed application form. Some programs may ask for entry tests or interviews.",
            },
            {
                "keywords": ["deadline", "last date", "apply", "application date"],
                "response": "The application deadline is normally announced before each semester. You should submit your form as early as possible to avoid missing the final date.",
            },
            {
                "keywords": ["program", "course", "degree", "subject"],
                "response": "Available programs can include Computer Science, Business Administration, Education, and other undergraduate or graduate options depending on the department.",
            },
            {
                "keywords": ["fee", "fees", "tuition", "cost", "payment"],
                "response": "Tuition and fees depend on the program. I can help you with general fee guidance, but the official office can confirm the exact amount for your selected program.",
            },
            {
                "keywords": ["scholarship", "financial aid", "aid"],
                "response": "Scholarships may be available based on merit, need, or special categories. Check the admissions office for the current scholarship list and criteria.",
            },
        ],
    },
    "medical": {
        "title": "Medical Center Information Bot",
        "subtitle": "Appointments, departments, doctors, and visiting guidance.",
        "accent": "#0d9488",
        "sample_prompts": [
            "How do I book an appointment?",
            "Which departments are available?",
            "Do you have pediatric doctors?",
        ],
        "rules": [
            {
                "keywords": ["appointment", "book", "schedule", "visit"],
                "response": "Appointments can usually be booked by phone, online portal, or at the reception desk. Bring your previous reports if you are visiting a specialist.",
            },
            {
                "keywords": ["department", "services", "ward"],
                "response": "Common departments include general medicine, pediatrics, gynecology, cardiology, dermatology, and emergency care.",
            },
            {
                "keywords": ["doctor", "specialist", "physician", "consultant"],
                "response": "You can consult the reception desk for doctor availability and specialist schedules. Tell them your symptoms so they can guide you to the right department.",
            },
            {
                "keywords": ["emergency", "urgent", "ambulance"],
                "response": "For emergencies, go directly to the emergency unit or call the hospital hotline immediately. Do not wait for a normal appointment.",
            },
            {
                "keywords": ["timing", "hours", "open", "schedule"],
                "response": "Clinic hours can vary by department, but most outpatient services operate during daytime working hours on weekdays.",
            },
        ],
    },
    "hospital": {
        "title": "Hospital Information Chatbot",
        "subtitle": "Emergency services, rooms, visiting hours, and patient guidance.",
        "accent": "#2563eb",
        "sample_prompts": [
            "What are the visiting hours?",
            "Are private rooms available?",
            "Where is the emergency room?",
        ],
        "rules": [
            {
                "keywords": ["emergency", "er", "icu", "urgent"],
                "response": "The emergency department operates 24/7 for urgent cases. Critical patients may be moved to ICU after evaluation by the medical team.",
            },
            {
                "keywords": ["room", "private", "shared", "availability"],
                "response": "Room availability changes throughout the day. Private, semi-private, and shared rooms may be available depending on current occupancy.",
            },
            {
                "keywords": ["visiting", "visit hours", "hours", "family"],
                "response": "Visiting hours are usually set by the ward to protect patient rest and treatment schedules. Please confirm the latest timing at the reception desk.",
            },
            {
                "keywords": ["billing", "payment", "insurance", "bill"],
                "response": "Billing and insurance support are handled by the accounts counter. Keep your admission slip and policy details ready for faster processing.",
            },
            {
                "keywords": ["pharmacy", "medicine", "drug"],
                "response": "The hospital pharmacy can help with prescribed medicines and dosage instructions. Always follow the doctor's prescription.",
            },
        ],
    },
    "hotel": {
        "title": "Hotel Information Chatbot",
        "subtitle": "Room types, rates, amenities, booking help, and policies.",
        "accent": "#b45309",
        "sample_prompts": [
            "What room types do you offer?",
            "What are the check-in times?",
            "Do you have free Wi-Fi?",
        ],
        "rules": [
            {
                "keywords": ["room type", "room types", "single", "double", "suite"],
                "response": "We can help with single rooms, double rooms, deluxe rooms, and suites depending on availability.",
            },
            {
                "keywords": ["price", "rate", "cost", "tariff", "fare"],
                "response": "Room rates depend on the room type, season, and stay length. Ask for the current daily rate for the exact category you want.",
            },
            {
                "keywords": ["amenity", "wifi", "pool", "breakfast", "gym"],
                "response": "Common amenities include free Wi-Fi, breakfast, air conditioning, room service, parking, and sometimes a gym or pool.",
            },
            {
                "keywords": ["booking", "reserve", "reservation", "availability"],
                "response": "You can book by phone, website, or front desk. Share your dates, guest count, and room preference to check availability.",
            },
            {
                "keywords": ["check-in", "check in", "check-out", "check out"],
                "response": "Standard check-in and check-out times vary by property, but a common pattern is afternoon check-in and late-morning check-out.",
            },
        ],
    },
    "restaurant": {
        "title": "Restaurant Information Bot",
        "subtitle": "Menus, reservations, order tracking, and opening hours.",
        "accent": "#dc2626",
        "sample_prompts": [
            "What is on the menu?",
            "Can I reserve a table?",
            "Where is my order?",
        ],
        "rules": [
            {
                "keywords": ["menu", "dish", "food", "special"],
                "response": "The menu can include burgers, pasta, grilled items, salads, drinks, and daily specials. Ask about the chef's recommendation for today.",
            },
            {
                "keywords": ["reservation", "reserve", "table", "booking"],
                "response": "You can reserve a table by sharing the date, time, and number of guests. Peak hours may require a short wait.",
            },
            {
                "keywords": ["order", "tracking", "status", "delivery"],
                "response": "Order tracking is available using your order number. If delivery is delayed, the restaurant support team can confirm the current status.",
            },
            {
                "keywords": ["opening", "open", "hours", "closing"],
                "response": "Restaurant opening hours vary, but most branches serve lunch through dinner and may offer limited late-night service.",
            },
            {
                "keywords": ["price", "cost", "bill", "payment"],
                "response": "Prices depend on the item ordered. For the most accurate bill, check the menu or ask the cashier for today's rates.",
            },
        ],
    },
    "library": {
        "title": "Library Assistant Bot",
        "subtitle": "Books, due dates, borrowing rules, and opening hours.",
        "accent": "#7c3aed",
        "sample_prompts": [
            "How do I find a book?",
            "When is the library open?",
            "What happens if I return late?",
        ],
        "rules": [
            {
                "keywords": ["find", "search", "book", "catalog"],
                "response": "Use the library catalog to search by title, author, or subject. If needed, I can also help you find a topic area or shelf section.",
            },
            {
                "keywords": ["due", "return", "late", "fine"],
                "response": "Due dates depend on the borrowing policy. Late returns may result in fines, so it is best to renew items before the deadline.",
            },
            {
                "keywords": ["opening", "hours", "open", "close"],
                "response": "Library opening hours may vary by weekday and semester. Please check the notice board or library portal for the latest schedule.",
            },
            {
                "keywords": ["membership", "card", "borrow", "issue"],
                "response": "A student or member card is usually required to borrow books. The circulation desk can explain the issue and renewal process.",
            },
            {
                "keywords": ["print", "computer", "wifi", "study"],
                "response": "Most libraries provide study spaces, internet access, and sometimes printing or scanning services for registered users.",
            },
        ],
    },
    "campus": {
        "title": "Campus Tour Bot",
        "subtitle": "A creative campus guide for visitors and new students.",
        "accent": "#14b8a6",
        "sample_prompts": [
            "Where is the main gate?",
            "Can I visit the science building?",
            "How do I get to the cafeteria?",
        ],
        "rules": [
            {
                "keywords": ["gate", "entrance", "main"],
                "response": "The main gate is the easiest entry point for visitors. Security can guide you to the reception or student affairs office.",
            },
            {
                "keywords": ["science", "lab", "building", "department"],
                "response": "The science building usually hosts labs, classrooms, and faculty offices. Ask at reception for a map if you are visiting for the first time.",
            },
            {
                "keywords": ["cafeteria", "canteen", "food", "eat"],
                "response": "The cafeteria is a good stop for lunch and drinks. It is typically located near the main student activity area.",
            },
            {
                "keywords": ["library", "study", "books"],
                "response": "The library is usually a quiet study zone with books, seating, and computer access. It is one of the most useful places for students.",
            },
            {
                "keywords": ["tour", "visit", "guide"],
                "response": "A campus tour can be arranged with student affairs. They can show you the major buildings, labs, library, and cafeteria.",
            },
        ],
    },
}

DEFAULT_BOT = "hotel"


def normalize_text(text: str) -> str:
    return " ".join((text or "").lower().strip().split())


def build_bot_reply(bot_key: str, message: str) -> str:
    profile = BOT_PROFILES.get(bot_key, BOT_PROFILES[DEFAULT_BOT])
    clean_message = normalize_text(message)

    if not clean_message:
        return "Please type a question so I can help."

    if any(word in clean_message for word in ["hello", "hi", "hey", "greetings"]):
        return f"Hello! I am the {profile['title']}. Ask me anything related to this topic."

    if any(word in clean_message for word in ["thank", "thanks", "thx"]):
        return "You're welcome. If you have another question, send it anytime."

    for rule in profile["rules"]:
        if any(keyword in clean_message for keyword in rule["keywords"]):
            return rule["response"]

    fallback_messages = {
        "university": "I can help with admission requirements, deadlines, programs, fees, and scholarships.",
        "medical": "Try asking about appointments, departments, doctors, emergency care, or clinic hours.",
        "hospital": "You can ask about emergency services, room availability, visiting hours, pharmacy, or billing.",
        "hotel": "You can ask about room types, prices, amenities, booking, or check-in and check-out.",
        "restaurant": "You can ask about the menu, reservations, order tracking, opening hours, or prices.",
        "library": "You can ask about finding books, due dates, opening hours, membership, or study services.",
        "campus": "You can ask about gates, buildings, cafeteria, the library, or campus tours.",
    }
    return fallback_messages.get(bot_key, fallback_messages[DEFAULT_BOT])


@app.route("/")
def index():
    return render_template(
        "index.html",
        bot_options=BOT_PROFILES,
        default_bot=DEFAULT_BOT,
    )


@app.route("/chat", methods=["POST"])
def chat():
    payload = request.get_json(silent=True) or request.form
    bot_key = payload.get("bot", DEFAULT_BOT)
    message = payload.get("message", "")
    profile = BOT_PROFILES.get(bot_key, BOT_PROFILES[DEFAULT_BOT])

    return jsonify(
        {
            "bot": bot_key,
            "bot_title": profile["title"],
            "reply": build_bot_reply(bot_key, message),
        }
    )


if __name__ == "__main__":
    app.run(debug=True)
