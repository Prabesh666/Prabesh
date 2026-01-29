const DEFAULT_API_BASE = "http://127.0.0.1:8000";
const apiBaseUrl = import.meta.env.VITE_API_BASE_URL || DEFAULT_API_BASE;

/**
 * Send a message to FastAPI chatbot backend
 */
export async function sendMessage({ message, sessionId }) {
  const response = await fetch(`${apiBaseUrl}/chat`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      message: message,           // ✅ REQUIRED by backend
      sessionId: sessionId ?? null // ✅ safe optional
    }),
  });

  if (!response.ok) {
    const detail = await response.json().catch(() => null);
    throw new Error(detail?.detail || "Failed to reach chatbot service.");
  }

  return response.json();
}

/**
 * Health check route
 */
export async function fetchHealth() {
  const response = await fetch(`${apiBaseUrl}/health`);

  if (!response.ok) {
    throw new Error("Health check failed");
  }

  return response.json();
}
