import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Layout from './layouts/Layout';
import LandingPage from './pages/LandingPage';
import AnalyzePage from './pages/AnalyzePage';
import SessionPage from './pages/SessionPage';
import AgentsPage from './pages/AgentsPage';
import ConflictsPage from './pages/ConflictsPage';
import ReportPage from './pages/ReportPage';
import { AnalysisProvider } from './context/AnalysisContext';

const App = () => {
  return (
    <Router>
      <AnalysisProvider>
        <Routes>
          <Route path="/" element={<Layout />}>
            <Route index element={<LandingPage />} />
            <Route path="analyze" element={<AnalyzePage />} />
            <Route path="session/:id" element={<SessionPage />} />
            <Route path="agents" element={<AgentsPage />} />
            <Route path="conflicts" element={<ConflictsPage />} />
            <Route path="report" element={<ReportPage />} />
          </Route>
        </Routes>
      </AnalysisProvider>
    </Router>
  );
};

export default App;
