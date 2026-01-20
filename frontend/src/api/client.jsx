export const API_URL = "http://localhost:8000/api";

export async function apiGet(endpoint) {
    const response = await fetch(`${API_URL}${endpoint}`);
    return response.json();
}

export async function apiPost(endpoint, body) {
    const response = await fetch(`${API_URL}${endpoint}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body)
    });
    return response.json();
}
