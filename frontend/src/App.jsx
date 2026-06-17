import { useState, useEffect } from "react";
import axios from "axios";
import Navbar from "./components/Navbar";
import SplashScreen from "./components/SplashScreen";
import UploadPage from "./pages/UploadPage";
import LoadingPage from "./pages/LoadingPage";
import ResultsPage from "./pages/ResultsPage";

function App() {
  const [showSplash, setShowSplash] = useState(true);
  const [page, setPage] = useState("upload");
  const [selectedFile, setSelectedFile] = useState(null);
  const [analysisData, setAnalysisData] = useState(null);
  const [error, setError] = useState(null);
  const [loadingStep, setLoadingStep] = useState(0);
  const [visible, setVisible] = useState(true);

  useEffect(() => {
    setVisible(true);
  }, []);

  const handleFileSelect = async (file) => {
    setSelectedFile(file);
    setError(null);
    setLoadingStep(0);
    setPage("loading");

    const stepTimer = setInterval(() => {
      setLoadingStep((prev) => Math.min(prev + 1, 5));
    }, 4000);

    try {
      const formData = new FormData();
      formData.append("file", file);

      const response = await axios.post(`${import.meta.env.VITE_API_URL}/analyze/full`, formData, {
        headers: { "Content-Type": "multipart/form-data" },
        timeout: 120000,
      });

      clearInterval(stepTimer);
      const processedData = {
        ...response.data,
        triage: response.data.ai_analysis?.triage,
        analysis: response.data.ai_analysis?.analysis,
        risk_assessment: response.data.ai_analysis?.risk_assessment,
        report: response.data.ai_analysis?.report,
        final_risk_score: response.data.ai_analysis?.final_risk_score || response.data.final_risk_score,
        risk_level: response.data.ai_analysis?.risk_level || response.data.risk_level,
      };
      setAnalysisData(processedData);
      setPage("results");
    } catch (err) {
      clearInterval(stepTimer);
      setError(
        err.response?.data?.detail || err.message || "Analysis failed. Make sure the backend is running."
      );
      setPage("upload");
    }
  };

  const handleReset = () => {
    setPage("upload");
    setSelectedFile(null);
    setAnalysisData(null);
    setError(null);
    setLoadingStep(0);
  };

  return (
    <>
      {showSplash && <SplashScreen onComplete={() => setShowSplash(false)} />}
      <Navbar />
      <div
        className={`page-transition ${visible ? "fade-in-active" : "fade-out"}`}
        style={{ paddingTop: "65px" }}
      >
        {page === "upload" && (
          <UploadPage onFileSelect={handleFileSelect} error={error} />
        )}
        {page === "loading" && (
          <LoadingPage filename={selectedFile?.name} currentStep={loadingStep} />
        )}
        {page === "results" && analysisData !== null && (
          <ResultsPage data={analysisData} filename={selectedFile?.name} onReset={handleReset} />
        )}
      </div>
    </>
  );
}

export default App;
