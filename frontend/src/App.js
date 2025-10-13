import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import ProjectView from './pages/ProjectView';
import AnnotateView from './pages/AnnotateView';
import ReviewView from './pages/ReviewView';
import BatchSubmit from './pages/BatchSubmit';
import JobsView from './pages/JobsView';
import AnalyticsView from './pages/AnalyticsView';
import Layout from './components/Layout';

// Protected route wrapper
function ProtectedRoute({ children }) {
  const { currentUser, loading } = useAuth();
  
  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-xl">Loading...</div>
      </div>
    );
  }
  
  return currentUser ? children : <Navigate to="/login" />;
}

function App() {
  return (
    <Router>
      <AuthProvider>
        <Routes>
          <Route path="/login" element={<Login />} />
          
          <Route path="/" element={
            <ProtectedRoute>
              <Layout />
            </ProtectedRoute>
          }>
            <Route index element={<Dashboard />} />
            <Route path="project/:projectId" element={<ProjectView />} />
            <Route path="annotate/:scanId" element={<AnnotateView />} />
            <Route path="review/:scanId" element={<ReviewView />} />
            <Route path="batch-submit" element={<BatchSubmit />} />
            <Route path="jobs" element={<JobsView />} />
            <Route path="analytics/:projectId" element={<AnalyticsView />} />
          </Route>
        </Routes>
      </AuthProvider>
    </Router>
  );
}

export default App;

