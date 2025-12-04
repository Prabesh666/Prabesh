from chatbot import get_ai_response

if __name__ == "__main__":
    print("AI Chatbot Ready — type 'exit' to quit.")
    while True:
        q = input("You: ").strip()
        if q.lower() == "exit":
            print("Goodbye 👋")
            break
        print("AI:", get_ai_response(q))
