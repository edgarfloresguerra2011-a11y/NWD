import React, { useState, useEffect } from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import Layout from './components/Layout';
import Dashboard from './components/Dashboard';
import AccountList from './components/AccountList';
import AccountConnect from './components/AccountConnect';
import CampaignList from './components/CampaignList';
import CampaignEditor from './components/CampaignEditor';
import Analytics from './components/Analytics';
import DNSChecker from './components/DNSChecker';
import LoginForm from './components/LoginForm';
import RegisterForm from './components/RegisterForm';

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const token = localStorage.getItem('token');
  if (!token) return <Navigate to="/login" replace />;
  return <>{children}</>;
}

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<LoginForm />} />
      <Route path="/register" element={<RegisterForm />} />
      <Route
        path="/*"
        element={
          <ProtectedRoute>
            <Layout>
              <Routes>
                <Route path="/dashboard" element={<Dashboard />} />
                <Route path="/accounts" element={<AccountList />} />
                <Route path="/accounts/connect" element={<AccountConnect />} />
                <Route path="/campaigns" element={<CampaignList />} />
                <Route path="/campaigns/:id" element={<CampaignEditor />} />
                <Route path="/analytics" element={<Analytics />} />
                <Route path="/domains" element={<DNSChecker />} />
                <Route path="/" element={<Navigate to="/dashboard" replace />} />
              </Routes>
            </Layout>
          </ProtectedRoute>
        }
      />
    </Routes>
  );
}
