def build_kb_texts_from_dataset(ds):
    texts = []
    answers = []

    company = ds.get("company", {})
    if company:
        name = company.get("name", "")
        tagline = company.get("tagline", "")
        about = company.get("about", "")
        location = company.get("location") or company.get("contact", {}).get("address", "")
        contact = company.get("contact", {})
        phones = ", ".join(contact.get("phones", []))
        email = contact.get("email", "")

        # Core company Q/A
        if name:
            texts.append(f"what is {name}")
            answers.append(f"{name} - {tagline}. {about}")

            texts.append("what is codeit")
            answers.append(f"{name} - {tagline}. {about}")

            texts.append("who are you")
            answers.append("I am CodeIt AI 🤖 — your friendly learning assistant!")

            texts.append("what is codeit ai")
            answers.append("CodeIt AI is a smart assistant that helps students learn about courses, mentors, fees, and more!")

        texts.append("where are you located")
        answers.append( location)

        texts.append("contact")
        answers.append(f"Email: {email}. Phones: {phones}")

        texts.append("working hours")
        answers.append(contact.get("working_hours", ""))

    # Mentors list + individual mentor Q/A
    mentors = company.get("mentors", []) if company else []
    if mentors:
        texts.append("mentors")
        answers.append("\n".join([f"{m.get('name')} — {m.get('role')} ({m.get('experience')})" for m in mentors]))

    for m in mentors:
        name = m.get("name", "")
        role = m.get("role", "")
        exp = m.get("experience", "")
        if name:
            texts.append(f"who is {name}")
            answers.append(f"{name} — {role} ({exp})")

            texts.append(f"who is {role}")
            answers.append(f"{name} — {role} ({exp})")

        # common owner/ceo patterns
        if role and any(k in role.lower() for k in ["ceo", "founder", "owner"]):
            texts.append("who is the ceo")
            answers.append(f"{name} — {role} ({exp})")
            texts.append("who is the founder")
            answers.append(f"{name} — {role} ({exp})")
            texts.append("who is the owner")
            answers.append(f"{name} — {role} ({exp})")

    # Course structure
    cs = ds.get("course_structure", {})
    if cs:
        texts.append("course duration")
        answers.append(f"Session length: {cs.get('session_length','')} , Daily: {cs.get('daily_duration','')}")
        benefits = cs.get("benefits", [])
        if benefits:
            texts.append("course benefits")
            answers.append("Benefits: " + "; ".join(benefits))

    # Courses and course-specific prompts
    courses = ds.get("courses", {})
    for category, course_list in courses.items():
        for c in course_list:
            title = c.get("title", "").strip()
            price = c.get("price", "")
            url = c.get("url", "")
            desc = c.get("description", "") or c.get("short_description", "") or c.get("summary", "")

            if title:
                texts.append(title)
                answers.append(f"{title} — Price: {price}. URL: {url}")

                texts.append(f"price of {title}")
                answers.append(f"The price of '{title}' is {price}.")

                texts.append(f"what is {title}")
                answers.append(f"{title}: {desc} Price: {price}. URL: {url}" if desc else f"{title} — Price: {price}. URL: {url}")

                texts.append(f"{category} course {title}")
                answers.append(f"{title} — {price}. {url}")

    # Common FAQ
    faq = {
        "online classes": "Yes, we offer online and onsite classes.",
        "demo class": "Yes, demo classes are available.",
        "certificate": "A completion certificate is provided after finishing the course.",
        "refund": "Refunds depend on institute policy. Please contact the admin office for details.",
        "internship": "Internship opportunities are provided to top-performing students.",
        "payment methods": "We accept eSewa, Khalti, bank deposits, and in-person payments.",
        "beginner": "Yes, we have courses suitable for beginners with no prior experience.",
        "support": "We provide doubt-support during and after the course.",
        "enroll": "You can enroll via our website or by visiting our institute.",
        "projects": "Yes — students work on real projects during the course."
    }

    for q, a in faq.items():
        texts.append(q)
        answers.append(a)

    # Projects
    projects = ds.get("projects", [])
    if projects:
        texts.append("what projects will i do")
        answers.append("You will work on real-world projects like E-Commerce Platforms, Management Systems, and Portfolios depending on your course.")

        for p in projects:
            title = p.get("title", "")
            course = p.get("course", "")
            desc = p.get("description", "")
            
            if title:
                texts.append(f"project {title}")
                answers.append(f"Project: {title} (Course: {course}) — {desc}")
                
                texts.append(f"projects in {course}")
                answers.append(f"In {course}, you might work on projects like: {title} — {desc}")

    return texts, answers
