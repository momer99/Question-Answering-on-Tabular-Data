// app/page.js
"use client";

import React, { useState, useEffect } from "react";
import axios from "axios";

export default function Home() {
  const [datasets, setDatasets] = useState([]);
  const [selectedDataset, setSelectedDataset] = useState("");
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    // Fetch available datasets from the backend
    axios.get("http://localhost:8000/datasets/")
      .then((response) => {
        setDatasets(response.data.datasets);
      })
      .catch((error) => {
        console.error("Error fetching datasets:", error);
      });
  }, []);

  const handleQuestionSubmit = async (event) => {
    event.preventDefault();

    if (!selectedDataset) {
      alert("Please select a dataset.");
      return;
    }

    if (!question.trim()) {
      alert("Please enter a question.");
      return;
    }

    setLoading(true);
    setAnswer("");

    try {
      const response = await axios.post("http://localhost:8000/ask/", {
        dataset_name: selectedDataset,
        question: question.trim(),
      });
      setAnswer(response.data.answer);
    } catch (error) {
      console.error("Error getting answer:", error);
      setAnswer("Error getting answer.");
    }

    setLoading(false);
  };

  return (
    <div style={styles.container}>
      <h1 style={styles.title}>Question Answering over Tabular Data</h1>

      <div style={styles.formGroup}>
        <label htmlFor="dataset" style={styles.label}>Select Dataset:</label>
        <select
          id="dataset"
          value={selectedDataset}
          onChange={(e) => setSelectedDataset(e.target.value)}
          style={styles.select}
        >
          <option value="">-- Select a Dataset --</option>
          {datasets.map((dataset) => (
            <option key={dataset} value={dataset}>
              {dataset}
            </option>
          ))}
        </select>
      </div>

      <form onSubmit={handleQuestionSubmit} style={styles.form}>
        <div style={styles.formGroup}>
          <label htmlFor="question" style={styles.label}>Enter Question:</label>
          <input
            type="text"
            id="question"
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            style={styles.input}
            placeholder="Type your question here..."
          />
        </div>

        <button type="submit" style={styles.button} disabled={loading}>
          {loading ? "Getting Answer..." : "Get Answer"}
        </button>
      </form>

      {answer && (
        <div style={styles.answerContainer}>
          <h2 style={styles.answerTitle}>Answer:</h2>
          <p style={styles.answerText}>{answer}</p>
        </div>
      )}
    </div>
  );
}

const styles = {
  container: {
    fontFamily: "'Arial', sans-serif",
    padding: '20px',
    backgroundColor: '#121212',
    color: '#ffffff',
    minHeight: '100vh',
  },
  title: {
    textAlign: 'center',
  },
  formGroup: {
    marginBottom: '15px',
  },
  label: {
    display: 'block',
    marginBottom: '5px',
  },
  select: {
    width: '100%',
    padding: '10px',
    fontSize: '16px',
    borderRadius: '5px',
  },
  form: {
    maxWidth: '600px',
    margin: '0 auto',
  },
  input: {
    width: '100%',
    padding: '10px',
    fontSize: '16px',
    borderRadius: '5px',
  },
  button: {
    marginTop: '15px',
    padding: '10px 20px',
    fontSize: '16px',
    backgroundColor: '#007BFF',
    color: '#ffffff',
    border: 'none',
    borderRadius: '5px',
    cursor: 'pointer',
  },
  answerContainer: {
    marginTop: '30px',
    textAlign: 'center',
  },
  answerTitle: {
    fontSize: '24px',
  },
  answerText: {
    fontSize: '20px',
  },
};
