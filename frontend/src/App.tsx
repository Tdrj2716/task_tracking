import "./App.css";

import { useState } from "react";

import apiClient from "./services/apiClient";

function App() {
  const [healthStatus, setHealthStatus] = useState<string>("");
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string>("");

  const checkHealth = async () => {
    setLoading(true);
    setError("");
    setHealthStatus("");

    try {
      const response = await apiClient.get("/health/");
      setHealthStatus(JSON.stringify(response.data));
    } catch (err: unknown) {
      if (typeof err === "object" && err !== null && "message" in err) {
        setError((err as { message: string }).message);
      } else {
        setError("Unknown error occurred");
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ padding: "2rem" }}>
      <h1>Task Time Tracking - API Test</h1>
      <div style={{ marginTop: "2rem" }}>
        <button
          onClick={checkHealth}
          disabled={loading}
          style={{
            padding: "0.5rem 1rem",
            fontSize: "1rem",
            cursor: loading ? "not-allowed" : "pointer",
          }}
        >
          {loading ? "Loading..." : "Check API Health"}
        </button>
      </div>

      {healthStatus && (
        <div style={{ marginTop: "1rem" }}>
          <h2>Success:</h2>
          <pre
            style={{
              background: "#f0f0f0",
              padding: "1rem",
              borderRadius: "4px",
            }}
          >
            {healthStatus}
          </pre>
        </div>
      )}

      {error && (
        <div style={{ marginTop: "1rem" }}>
          <h2>Error:</h2>
          <pre
            style={{
              background: "#fee",
              padding: "1rem",
              borderRadius: "4px",
              color: "red",
            }}
          >
            {error}
          </pre>
        </div>
      )}
    </div>
  );
}

export default App;
