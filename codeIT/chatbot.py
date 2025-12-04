import json
from difflib import get_close_matches

from utils import load_json, create_or_load_embeddings, semantic_search
from kbuilder import build_kb_texts_from_dataset
from llm import generate_llm_answer

DATA_FILE = "codeit_dataset.json"
SIMILARITY_THRESHOLD = 0.56
TOP_K = 3

# load dataset
dataset = load_json(DATA_FILE)

# build KB and embeddings (done once on import)
kb_texts, kb_answers = build_kb_texts_from_dataset(dataset)
kb_embeddings = create_or_load_embeddings(kb_texts)

# small memory store
memory = {"last_person": None, "last_topic": None}

def find_course_name(user_text, courses_list):
    titles = [c["title"].lower() for c in courses_list]
    match = get_close_matches(user_text, titles, n=1, cutoff=0.5)
    return match[0] if match else None


def chatbot(question: str, history=None) -> str:
    """
    Main chatbot function. Backend should call get_ai_response(query, history).
    """
    if not question:
        return "Can you please rephrase that? 😊"

    q = question.lower().strip()
    if len(q) < 2:
        return "Can you please rephrase that? 😊"

    company = dataset.get("company", {})
    courses_info = dataset.get("courses", {})
    cs = dataset.get("course_structure", {})
    projects_list = dataset.get("projects", [])

    # --- quick exact rules ---
    if q.startswith(("hi", "hello", "hey")):
        return "Hey there! 😊 How can I help you today?"

    if "what is codeit ai" in q or "codeit ai" in q:
        return "CodeIt AI is a smart learning assistant created to help students explore courses, mentors, and everything about CodeIt Institute in a simple way! 🤖✨"

    if "who are you" in q or "who r u" in q:
        return "I'm CodeIt AI 🤖 — your friendly learning assistant here to help you explore courses, mentors, and all things CodeIt Institute!"

    if "thank" in q or "thanks" in q:
        return "You're very welcome! 💫"

    if "how are you" in q:
        return "I'm great and ready to help you learn! What about you?"

    # contact
    if any(phrase in q for phrase in [
        "contact number", "contact info", "how do i contact", "institute contact",
        "contact details", "phone number", "contact us", "how to contact"
    ]):
        contact = company.get("contact", {})
        return f"Email: {contact.get('email','')} | Phones: {', '.join(contact.get('phones',[]))} | Working hours: {contact.get('working_hours','')}"

    # location
    if any(phrase in q for phrase in [
        "where are you located", "where is your institute", "your location",
        "institute location", "center location", "where is codeit", "located at"
    ]):
        return f"Our company is located at {company.get('location', '')}."

    # CEO/Owner/Founder
    if any(word in q for word in ["ceo", "owner", "founder"]):
        mentors = company.get("mentors", [])
        for m in mentors:
            role = (m.get("role") or "").lower()
            if any(r in role for r in ["ceo", "founder", "owner"]):
                memory["last_person"] = m
                return f"{m.get('name')} is the {m.get('role')} of {company.get('name')} with {m.get('experience','')} experience."
        return "Sorry, I couldn't find information about the owner."

    # mentors
    if "mentor" in q and not ("who is" in q):
        mentors = company.get("mentors", [])
        if mentors:
            return "Some mentors:\n" + "\n".join([f"{m.get('name')} - {m.get('role')} ({m.get('experience','')})" for m in mentors])
        else:
            return "No mentor info available."

    # short FAQ
    if "demo" in q:
        return "Yes, demo classes are available."
    if "certificate" in q or "certification" in q:
        return "Yes! You will receive an official completion certificate after finishing the course. 🎓"
    if "beginner" in q:
        return "Yes, we have beginner-friendly courses."
    if "payment" in q:
        return "We accept eSewa, Khalti, bank deposits, and in-person payments."

    # projects - Specific Intent Check
    if "project" in q and not "price" in q:
        # Try to find specific project mentions
        found_projects = []
        for p in projects_list:
            if p.get("title", "").lower() in q or p.get("course", "").lower() in q:
                found_projects.append(f"- {p.get('title')} ({p.get('course')})")
        
        if found_projects:
             return "Here are some relevant projects:\n" + "\n".join(found_projects[:3])
        
        if "what projects" in q or "list projects" in q:
             return "We have many projects like: " + ", ".join([p["title"] for p in projects_list[:4]]) + "..."

        return "Yes — students work on real projects during the course. Ask me about projects in a specific course!"

    # --- Course name rule ---
    for category, course_list in courses_info.items():
        cname = find_course_name(q, course_list)
        if cname:
            for c in course_list:
                if (c.get("title") or "").lower() == cname:
                    memory["last_topic"] = c.get("title")
                    return f"{c.get('title')} — Price: {c.get('price','N/A')}. {c.get('url','') or ''}"

    # --- Semantic fallback ---
    sem = semantic_search(question, kb_embeddings, kb_texts, top_k=TOP_K)
    if sem:
        top_text, top_score, top_idx = sem[0]
        if top_score >= SIMILARITY_THRESHOLD:
            return kb_answers[top_idx]

        # --- LLM fallback using Groq ---
        context = "\n".join([r[0] for r in sem])
        llm_answer = generate_llm_answer(question, context, history)
        if llm_answer:
            return llm_answer

    # --- Courses fallback ---
    if "course" in q or "training" in q or "offer" in q:
        for category in courses_info.keys():
            if category.replace("_", " ") in q:
                items = [f"- {c.get('title')} ({c.get('price')})" for c in courses_info[category]]
                return f"{category.replace('_',' ').title()} Courses:\n" + "\n".join(items)

        out = []
        for cat, clist in courses_info.items():
            for c in clist:
                out.append(f"- {c.get('title')} ({cat.replace('_',' ').title()})")

        return "Available courses:\n" + "\n".join(out[:12]) + "\n...and more!"

    # --- Instructor fallback ---
    if "teach" in q or "trainer" in q or "instructor" in q:
        for category, course_list in courses_info.items():
            for c in course_list:
                if (c.get("title") or "").lower() in q:
                    instructor = c.get("instructor") or c.get("mentor")
                    return f"{instructor} teaches {c.get('title')}." if instructor else f"I don't have instructor info for {c.get('title')}."
        return "Which course are you asking about?"

    # --- Course structure fallback ---
    if "structure" in q or "duration" in q or "benefits" in q:
        return f"Session: {cs.get('session_length','')}, Daily: {cs.get('daily_duration','')}"

    # final fallback
    return "I'm still learning — I don't have an answer for that yet. 😊"


def get_ai_response(query: str, history=None) -> str:
    return chatbot(query, history)
