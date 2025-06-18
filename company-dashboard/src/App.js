import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import CompanyVisualization from "./components/CompanyVisualization";

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<CompanyVisualization />} />
      </Routes>
    </Router>
  );
}

export default App;
