import { useState } from "react";
import axios from "axios";
import {
  Container,
  Typography,
  Box,
  CircularProgress,
  Button,
} from "@mui/material";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
} from "recharts";
import "./assets/index.css"; // Import the custom CSS

const App = () => {
  const [url, setUrl] = useState("");
  const [summary, setSummary] = useState([]);
  const [sentimentData, setSentimentData] = useState([]);
  const [ldaTopics, setLdaTopics] = useState([]);
  const [loading, setLoading] = useState(false);

  const handleFetch = async () => {
    if (!url.includes("youtube.com/watch?v=")) {
      alert("Please enter a valid YouTube video URL.");
      return;
    }

    setLoading(true);
    try {
      const response = await axios.post("http://localhost:5000/analyze", {
        url,
      });
      const data = response.data; // ✅ Correct way to access API response

      console.log("API Response:", data); // Debugging step

      const lda_result = data.lda_result;
      const positive = data.positive;
      const negative = data.negative;
      const summarize = data.summarize;
      setSummary(summarize);
      console.log("API Response:", data); // Debugging step
      console.log("LDA Topics:", lda_result);
      setSentimentData([
        { sentiment: "Positive", count: positive },
        { sentiment: "Negative", count: negative },
      ]);

      setLdaTopics(
        data.lda_result.map((keywords, index) => ({
          topic: keywords.slice(0, 5).join(", "), // ✅ Convert keywords list to a readable string (first 5 words)
          count: data.topic_dist[index] || 0, // ✅ Use topic distribution count
        }))
      );
    } catch (error) {
      console.error("Error fetching data:", error);
      alert("Failed to fetch comments or analyze sentiments.");
    }
    setLoading(false);
  };

  const COLORS = ["#0088FE", "#00C49F", "#FFBB28"];

  return (
    <Container maxWidth="lg">
      {/* Header */}
      <Box className="header">
        <Typography variant="h3" component="h1" gutterBottom>
          Hinglish Sentiment Analyzer
        </Typography>
        <Typography variant="subtitle1">
          Analyze YouTube comments with stunning visualizations.
        </Typography>
      </Box>

      {/* Input Section */}
      <Box className="input-section">
        <input
          type="text"
          placeholder="Enter YouTube Video URL"
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          onFocus={(e) => e.target.select()}
        />
        <Button
          variant="contained"
          color="primary"
          onClick={handleFetch}
          disabled={loading}
          fullWidth
          sx={{
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            gap: 1, // Adds spacing between text and loader
          }}
        >
          {loading ? (
            <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
              <CircularProgress size={20} color="inherit" />
              Analyzing...
            </Box>
          ) : (
            "Fetch Comments & Analyze"
          )}
        </Button>
      </Box>

      {/* Cards Section */}
      <Box display="flex" flexWrap="wrap" justifyContent="center">
        {/* Sentiment Analysis Card */}
        <Box
          className="card"
          sx={{
            flex: "1 1 300px",
            maxWidth: "350px",
            padding: "16px",
            borderRadius: "8px",
            boxShadow: "0 4px 8px rgba(0, 0, 0, 0.2)",

            textAlign: "center",
          }}
        >
          <Typography
            variant="h5"
            gutterBottom
            sx={{ fontSize: "1.6rem", marginTop: "1rem" }}
          >
            Sentiment Analysis
          </Typography>
          {sentimentData.length > 0 ? (
            <Box
              className="chart-container"
              sx={{ height: 300, padding: "2rem" }}
            >
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={sentimentData}>
                  <XAxis dataKey="sentiment" />
                  <YAxis />
                  <Tooltip />
                  <Bar dataKey="count" fill="#7684f4" />
                </BarChart>
              </ResponsiveContainer>
            </Box>
          ) : (
            <Typography
              variant="body1"
              sx={{ fontStyle: "italic", textAlign: "center", color: "white" }}
            >
              No data to display.
            </Typography>
          )}
        </Box>

        {/* Topic Modeling Card */}
        <Box
          className="card"
          sx={{
            flex: "1 1 300px",
            maxWidth: "700px",
            padding: "2rem",
            borderRadius: "8px",
            boxShadow: "0 4px 8px rgba(0, 0, 0, 0.2)",
          }}
        >
          <Typography variant="h5" gutterBottom sx={{ fontSize: "1.6rem" }}>
            Topic Modeling
          </Typography>
          {ldaTopics.length > 0 ? (
            <Box
              sx={{
                fontSize: "1rem",
              }}
            >
              {/* Display topic names */}
              {ldaTopics.map((topic, index) => (
                <Typography
                  key={index}
                  variant="body1"
                  sx={{ fontSize: "1.1rem" }}
                >
                  {`Topic ${index + 1}: ${topic.topic.toUpperCase()}`}{" "}
                  {/* ✅ Show topic text */}
                </Typography>
              ))}

              {/* Pie Chart */}
              <Box className="chart-container" sx={{ height: 300 }}>
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={ldaTopics}
                      dataKey="count"
                      nameKey="topic"
                      cx="50%"
                      cy="50%"
                      outerRadius={100}
                      fill="#82ca9d"
                      label={({ name, percent }) =>
                        `${name.toUpperCase()} ${(percent * 100).toFixed(1)}%`
                      }
                    >
                      {ldaTopics.map((entry, index) => (
                        <Cell
                          key={`cell-${index}`}
                          fill={COLORS[index % COLORS.length]}
                        />
                      ))}
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
              </Box>
            </Box>
          ) : (
            <Typography
              variant="body1"
              sx={{ fontStyle: "italic", color: "white" }}
            >
              No data to display.
            </Typography>
          )}
        </Box>
      </Box>
      <Box
        className="card"
        sx={{
          flex: "1 1 300px",
          marginBottom: "7rem",
          padding: "16px",
          borderRadius: "8px",
          boxShadow: "0 4px 8px rgba(0, 0, 0, 0.2)",
          textAlign: "center",
        }}
      >
        <Typography variant="h5" gutterBottom sx={{ fontSize: "2.1rem" }}>
          Summary
        </Typography>
        {summary && summary.length > 0 ? (
          <Box sx={{ textAlign: "left", padding: "1rem" }}>
            <ul
              style={{
                fontSize: "1.4rem",
                lineHeight: "1.6",
                letterSpacing: "0.4px",
                color: "white",
              }}
            >
              {summary.map((point, index) => (
                <li key={index}>{point}</li>
              ))}
            </ul>
          </Box>
        ) : (
          <Typography
            variant="body1"
            sx={{ fontStyle: "italic", color: "white" }}
          >
            No summary available.
          </Typography>
        )}
      </Box>
    </Container>
  );
};

export default App;
