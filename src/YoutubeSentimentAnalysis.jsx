import { useState } from "react";
import axios from "axios";
import TextField from "@mui/material/TextField";
import Button from "@mui/material/Button";
import Card from "@mui/material/Card";
import Typography from "@mui/material/Typography";
import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer } from "recharts";

export default function YouTubeSentimentAnalysis() {
  const [url, setUrl] = useState("");
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  
  const fetchCommentsAndAnalyze = async () => {
    if (!url.includes("youtube.com/watch?v=")) {
      alert("Please enter a valid YouTube video URL.");
      return;
    }
    
    setLoading(true);
    try {
      const response = await axios.post("http://localhost:5000/analyze", { url });
      setData(response.data);
    } catch (error) {
      console.error("Error fetching data:", error);
      alert("Failed to fetch comments or analyze sentiments.");
    }
    setLoading(false);
  };

  return (
    <div
      style={{
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        padding: "20px",
        minHeight: "100vh",
        backgroundImage: "url('/your-image-path.jpg')",
        backgroundSize: "cover",
        backgroundPosition: "center",
      }}
    >
      <Card style={{ width: "100%", maxWidth: "600px", padding: "20px", textAlign: "center", backgroundColor:"#2c3a8bd9", color: "#fff" }}>
        <Typography variant="h5" gutterBottom>
          YouTube Sentiment Analysis
        </Typography>
        <TextField
          type="text"
          label="Paste YouTube video URL"
          variant="outlined"
          fullWidth
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          sx={{
            mb: 2,
            backgroundColor: "#ffffff6e",
            borderRadius: "5px",
            "& .MuiOutlinedInput-root": {
              "& fieldset": {
                borderColor: "gray", 
              },
              "&:hover fieldset": {
                borderColor: "red", 
              },
              "&.Mui-focused fieldset": {
                borderColor: "red", 
              },
            },
            "& .MuiInputLabel-root": {
              color: "black", 
            },
            "& .MuiInputLabel-root.Mui-focused": {
              color: "red", 
            },
          }}
        />

        <Button 
          variant="contained" 
          color="primary" 
          onClick={fetchCommentsAndAnalyze} 
          disabled={loading} 
          fullWidth
        >
          {loading ? "Analyzing..." : "Fetch Comments & Analyze"}
        </Button>
      </Card>
      
      {data && (
        <Card style={{ width: "100%", maxWidth: "600px", padding: "20px", marginTop: "20px", textAlign: "center", backgroundColor: "rgba(30, 30, 30, 0.8)", color: "#fff" }}>
          <Typography variant="h6" gutterBottom>
            Sentiment Analysis Result
          </Typography>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={data}
                dataKey="value"
                nameKey="name"
                cx="50%"
                cy="50%"
                outerRadius={100}
                label
              >
                <Cell key="positive" fill="#4CAF50" />
                <Cell key="negative" fill="#F44336" />
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </Card>
      )}
    </div>
  );
}
