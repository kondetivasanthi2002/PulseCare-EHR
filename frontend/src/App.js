import React, { useState } from 'react';
import './App.css';

function App() {
  const [activeTab, setActiveTab] = useState('dashboard');

  return (
    <div className="app-container">
      {/* Sidebar */}
      <div className="sidebar">
        <div className="brand-header">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M12 2v20M2 12h20" />
          </svg>
          PulseCare EHR
        </div>
        <ul className="nav-links">
          <li className={`nav-item ${activeTab === 'dashboard' ? 'active' : ''}`} onClick={() => setActiveTab('dashboard')}>
            Dashboard Analytics
          </li>
          <li className={`nav-item ${activeTab === 'patients' ? 'active' : ''}`} onClick={() => setActiveTab('patients')}>
            Patient Records
          </li>
          <li className={`nav-item ${activeTab === 'encounters' ? 'active' : ''}`} onClick={() => setActiveTab('encounters')}>
            Clinical Encounters
          </li>
          <li className={`nav-item ${activeTab === 'billing' ? 'active' : ''}`} onClick={() => setActiveTab('billing')}>
            Billing & Claims
          </li>
          <li className={`nav-item ${activeTab === 'pharmacy' ? 'active' : ''}`} onClick={() => setActiveTab('pharmacy')}>
            Pharmacy & Prescriptions
          </li>
          <li className={`nav-item ${activeTab === 'laboratory' ? 'active' : ''}`} onClick={() => setActiveTab('laboratory')}>
            Laboratory & LOINC
          </li>
        </ul>
      </div>

      {/* Main Content Area */}
      <div className="main-content">
        <div className="top-header">
          <h2>Metropolitan Healthcare Alliance (EHR Portal)</h2>
          <span className="badge badge-success">HIPAA SECURE</span>
        </div>

        <div className="dashboard-body">
          {/* Key Metrics */}
          <div className="metrics-grid">
            <div className="metric-card">
              <span style={{ color: 'var(--text-muted)' }}>Total Active Patients</span>
              <div className="metric-value">2,480</div>
            </div>
            <div className="metric-card">
              <span style={{ color: 'var(--text-muted)' }}>Clinical Encounters YTD</span>
              <div className="metric-value">14,290</div>
            </div>
            <div className="metric-card">
              <span style={{ color: 'var(--text-muted)' }}>Outstanding Revenue</span>
              <div className="metric-value" style={{ color: 'var(--warning-color)' }}>$142,500</div>
            </div>
            <div className="metric-card">
              <span style={{ color: 'var(--text-muted)' }}>HIPAA Audit Events</span>
              <div className="metric-value" style={{ color: 'var(--success-color)' }}>100% Valid</div>
            </div>
          </div>

          {/* Active Patient Queue */}
          <h3 style={{ marginTop: '1rem' }}>Today's Clinical Patient Queue</h3>
          <table className="data-table">
            <thead>
              <tr>
                <th>MRN</th>
                <th>Patient Name</th>
                <th>Age/Gender</th>
                <th>Chief Complaint</th>
                <th>Status</th>
                <th>Attending Doctor</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td>MRN-984712</td>
                <td>Eleanor Vance</td>
                <td>38 / Female</td>
                <td>Chest tightness and exertional dyspnea</td>
                <td><span className="badge badge-warning">IN PROGRESS</span></td>
                <td>Dr. Sarah Smith (NPI: 1928374650)</td>
              </tr>
              <tr>
                <td>MRN-334109</td>
                <td>Robert Johnson</td>
                <td>51 / Male</td>
                <td>Routine Type 2 Diabetes Follow-up</td>
                <td><span className="badge badge-success">SIGNED OFF</span></td>
                <td>Dr. Michael Davis</td>
              </tr>
              <tr>
                <td>MRN-110293</td>
                <td>Alice Williams</td>
                <td>29 / Female</td>
                <td>Annual Wellness Exam & Immunizations</td>
                <td><span className="badge badge-success">SIGNED OFF</span></td>
                <td>Dr. Sarah Smith</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

export default App;
