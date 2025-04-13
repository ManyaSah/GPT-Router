import React, { useState } from "react";
import "./App.css"; // Ensure styling is linked

function App() {
  const [userInput, setUserInput] = useState("");
  const [apiKey, setApiKey] = useState("");
  const [response, setResponse] = useState(null);
  const [answer, setAnswer] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Define model options based on difficulty
  const modelOptions = {
    easy: 'gpt-3.5-turbo',
    medium: 'gpt-4o-mini',
    hard: 'o3-mini'
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!userInput.trim()) return;
    if (!apiKey.trim()) {
      setError("Please enter your OpenAI API key");
      return;
    }

    setLoading(true);
    setError(null);
    setResponse(null);
    setAnswer(null);

    try {
      // Call the router endpoint to get difficulty assessment
      const routerResponse = await fetch("https://your-backend-url.onrender.com//api/router", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ 
          question: userInput,
          api_key: apiKey 
        }),
      });

      if (!routerResponse.ok) {
        throw new Error("Network response was not ok");
      }

      const data = await routerResponse.json();
      
      // Create a response object with the router result
      setResponse({
        difficulty: data.difficulty || "unknown",
        recommended_model: data.recommended_model || modelOptions.medium,
        category: data.category || "unknown" // This is a placeholder as your backend doesn't currently provide category
      });
    } catch (err) {
      console.error("Error:", err);
      setError("Failed to analyze query. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  const handleGetAnswer = async (model) => {
    setLoading(true);
    setError(null);
    setAnswer(null);
    
    try {
      const answerResponse = await fetch("https://your-backend-url.onrender.com//api/answer", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ 
          question: userInput,
          model: model,
          api_key: apiKey
        }),
      });

      if (!answerResponse.ok) {
        throw new Error("Failed to get answer");
      }

      const data = await answerResponse.json();
      setAnswer(data.answer);
    } catch (err) {
      console.error("Error:", err);
      setError(`Failed to get answer from ${model}. Please try again.`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container">
      <h1 className="title">GPT Router</h1>
      <p className="description">
        Enter your question to determine which GPT model is best suited to answer it.
      </p>

      <form onSubmit={handleSubmit} className="input-form">
        <input
          className="api-key-input"
          type="password"
          value={apiKey}
          onChange={(e) => setApiKey(e.target.value)}
          placeholder="Enter your OpenAI API Key"
          disabled={loading}
        />
        
        <textarea
          className="input-box"
          value={userInput}
          onChange={(e) => setUserInput(e.target.value)}
          placeholder="Type your question here..."
          disabled={loading}
        />

        <button 
          className="submit-button" 
          type="submit" 
          disabled={loading}
        >
          {loading ? "Analyzing..." : "Analyze Question"}
        </button>
      </form>

      {error && <div className="error-message">{error}</div>}

      {response && (
        <div className={`result-box difficulty-${response.difficulty.toLowerCase()}`}>
          <h2 className="result-title">Analysis Result</h2>
          <p><strong>Category:</strong> {response.category}</p>
          <p><strong>Difficulty:</strong> {response.difficulty.charAt(0).toUpperCase() + response.difficulty.slice(1)}</p>
          <p><strong>Recommended Model:</strong> {response.recommended_model}</p>

          <div className="button-group">
            <button 
              className="model-btn easy-btn" 
              onClick={() => handleGetAnswer(modelOptions.easy)}
              disabled={loading}
            >
              Use GPT-3.5
            </button>
            <button 
              className="model-btn medium-btn" 
              onClick={() => handleGetAnswer(modelOptions.medium)}
              disabled={loading}
            >
              Use GPT-4o mini
            </button>
            <button 
              className="model-btn hard-btn" 
              onClick={() => handleGetAnswer(modelOptions.hard)}
              disabled={loading}
            >
              Use o3-mini
            </button>
          </div>
        </div>
      )}

      {answer && (
        <div className="answer-box">
          <h2 className="answer-title">Answer</h2>
          <div className="answer-content">
            {answer.split('\n').map((paragraph, idx) => (
              paragraph ? <p key={idx}>{paragraph}</p> : <br key={idx} />
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

export default App;