import { useState } from "react";

import Card from "../ui/Card";
import Button from "../ui/Button";
import TextInput from "../ui/TextInput";

import { analyzeProperty } from "../../services/intakeService";

export default function PropertyIntakeForm() {
  const [input, setInput] = useState("");

const [result, setResult] = useState<{
  success: boolean;
  input: string;
  type: string;
} | null>(null);

  async function analyze() {
    if (!input.trim()) {
      alert("Please enter an address, APN, or property link.");
      return;
    }

    try {
      const response = await analyzeProperty(input) as {
        success: boolean;
        input: string;
        type: string;
      } | null;

      setResult(response);
    } catch (error) {
      console.error(error);

      alert("Unable to analyze property.");
    }
  }

  return (
    <Card>
      <h2>Start Property Analysis</h2>

      <p>
        Enter an address, APN, or property link to begin.
      </p>

      <div style={{ marginTop: 20 }}>
        <TextInput
          value={input}
          onChange={setInput}
          placeholder="123 Main St, APN 123-456-789, Zillow URL..."
        />
      </div>

      <div style={{ marginTop: 20 }}>
        <Button onClick={analyze}>
          Analyze Property
        </Button>
      </div>

      {result && (
  <div
    style={{
      marginTop: 30,
      padding: 20,
      borderRadius: 10,
      background: "#f5f5f5",
    }}
  >
    <h3>Analysis Result</h3>

    <p>
      <strong>Input:</strong> {result.input}
    </p>

    <p>
      <strong>Detected Type:</strong> {result.type}
    </p>
  </div>
)}
    </Card>
  );
}