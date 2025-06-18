import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import CompanyVisualization from "./components/CompanyVisualization";

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<div>홈페이지 내용 또는 랜딩 페이지</div>} />
        <Route
          path="/company-visualization"
          element={<CompanyVisualization />}
        />
      </Routes>
    </Router>
  );
}

export default App;
