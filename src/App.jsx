import { useEffect, useState } from "react";
import api from "./api";

function App() {
  const [status, setStatus] = useState("Checking backend...");

  useEffect(() => {
    api.get("/health")
      .then((res) => setStatus(res.data.status))
      .catch(() => setStatus("Backend NOT reachable ❌"));
  }, []);

  return (
    <div style={{ padding: "2rem", fontFamily: "Arial" }}>
      <h1>Trade Finance Blockchain Explorer</h1>

      <p>
        <strong>Backend status:</strong>{" "}
        {status === "OK" ? "Running ✅" : status}
      </p>
    </div>
  );
}

export default App;
