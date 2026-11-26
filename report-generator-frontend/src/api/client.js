const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

export async function apiRequest(endpoint, options = {}) {
  const response = await fetch(`${API_BASE_URL}${endpoint}`, options);

  if (!response.ok) {
    let message = "Something went wrong while communicating with the server.";

    try {
      const result = await response.json();

      if (typeof result.detail === "string") {
        message = result.detail;
      } else if (Array.isArray(result.detail)) {
        message = result.detail.map((error) => error.msg).join(", ");
      } else if (result.message) {
        message = result.message;
      }
    } catch {
      message = response.statusText || message;
    }

    throw new Error(message);
  }

  return response;
}

export async function getJson(endpoint) {
  const response = await apiRequest(endpoint);
  return response.json();
}

export async function postJson(endpoint, data) {
  const response = await apiRequest(endpoint, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(data),
  });

  return response.json();
}

export async function postFile(endpoint, formData) {
  const response = await apiRequest(endpoint, {
    method: "POST",
    body: formData,
  });

  return response.json();
}

export async function deleteRequest(endpoint) {
  const response = await apiRequest(endpoint, {
    method: "DELETE",
  });

  return response.json();
}

export async function postBlob(endpoint, data) {
  const response = await apiRequest(endpoint, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(data),
  });

  return response.blob();
}
