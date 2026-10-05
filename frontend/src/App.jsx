import { useEffect, useState } from "react";
import axios from "axios";

import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";

import "./App.css";

const API = "https://secureiot-ecc-aes.onrender.com";

function App() {
  const [status, setStatus] = useState(null);
  const [history, setHistory] = useState([]);
  const [securityLogs, setSecurityLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [lastSecurityEvent, setLastSecurityEvent] = useState(
    "System initialized successfully"
  );
  const [secureMessages, setSecureMessages] = useState(0);
  const [replayBlocked, setReplayBlocked] = useState(0);
  const [tamperingBlocked, setTamperingBlocked] = useState(0);

  const fetchData = async () => {
    try {
      const [statusResponse, historyResponse, logsResponse] =
        await Promise.all([
          axios.get(`${API}/api/device/status`),
          axios.get(`${API}/api/sensor/history`),
          axios.get(`${API}/api/security/logs`),
        ]);

      const logs = logsResponse.data.logs || [];

      const blockedReplays = logs.filter(
        (log) =>
          log.event === "REPLAY_ATTACK" &&
          log.status === "BLOCKED"
      ).length;

      const blockedTampering = logs.filter(
        (log) =>
          log.event === "TAMPERING_ATTACK" &&
          log.status === "BLOCKED"
      ).length;

      setStatus(statusResponse.data);
      setHistory(historyResponse.data.data || []);
      setSecurityLogs(logs);
      setReplayBlocked(blockedReplays);
      setTamperingBlocked(blockedTampering);

      if (logs.length > 0) {
        setLastSecurityEvent(logs[0].details);
      }

      setLoading(false);
    } catch (error) {
      console.error("Backend connection error:", error);
      setLoading(false);
    }
  };

 const generateSecureReading = async () => {
  console.log("Generate Secure Reading button clicked");

  try {
    setLoading(true);

    console.log("Calling:", `${API}/api/device/data`);

    const response = await axios.get(
      `${API}/api/device/data`,
      {
        timeout: 30000,
      }
    );

    console.log("Secure reading response:", response.data);

    if (response.data.success) {
      setSecureMessages((prev) => prev + 1);

      setLastSecurityEvent(
        "Secure IoT message transmitted successfully"
      );
    }

    await fetchData();

  } catch (error) {
    console.error("Secure reading error:", error);

    setLastSecurityEvent(
      "Secure reading failed"
    );

  } finally {
    setLoading(false);
  }
};

  useEffect(() => {
    fetchData();

    const interval = setInterval(fetchData, 5000);

    return () => clearInterval(interval);
  }, []);

  const chartData = [...history]
    .slice(0, 12)
    .reverse()
    .map((item) => ({
      id: item.id,
      temperature: Number(item.temperature),
      humidity: Number(item.humidity),
    }));

  const totalThreats = replayBlocked + tamperingBlocked;

  const securityScore =
    totalThreats === 0
      ? 100
      : Math.max(85, 100 - totalThreats);

  if (loading && !status) {
    return (
      <div className="loading-screen">
        <div className="loading-card">
          <div className="loading-logo">S</div>
          <div className="loader"></div>
          <h2>Secure IoT</h2>
          <p>Initializing encrypted communication...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="app-shell">

      {/* SIDEBAR */}

      <aside className="sidebar">

        <div className="sidebar-brand">

          <div className="brand-mark">
            S
          </div>

          <div>
            <h1>Secure IoT</h1>
            <span>Security Platform</span>
          </div>

        </div>

        <nav className="sidebar-nav">

          <div className="nav-section">
            <span>MONITORING</span>
          </div>

          <a className="nav-item active">
            <span>◈</span>
            Dashboard
          </a>

          <a className="nav-item">
            <span>◉</span>
            IoT Devices
          </a>

          <a className="nav-item">
            <span>⌁</span>
            Sensor Data
          </a>

          <div className="nav-section">
            <span>SECURITY</span>
          </div>

          <a className="nav-item">
            <span>◆</span>
            Security Events
          </a>

          <a className="nav-item">
            <span>◇</span>
            Cryptography
          </a>

          <a className="nav-item">
            <span>▣</span>
            Audit Logs
          </a>

        </nav>

        <div className="sidebar-bottom">

          <div className="system-mini">

            <span className="online-dot"></span>

            <div>
              <strong>System Online</strong>
              <small>All services operational</small>
            </div>

          </div>

        </div>

      </aside>


      {/* MAIN CONTENT */}

      <main className="main-content">

        {/* TOPBAR */}

        <header className="topbar">

          <div>
            <span className="breadcrumb">
              Security / Dashboard
            </span>

            <h2>
              Security Operations Center
            </h2>
          </div>

          <div className="topbar-right">

            <div className="live-indicator">
              <span></span>
              LIVE MONITORING
            </div>

            <div className="secure-status">
              <span>✓</span>
              SYSTEM SECURE
            </div>

          </div>

        </header>


        {/* HERO */}

        <section className="dashboard-hero">

          <div>

            <span className="hero-label">
              CRYPTOGRAPHIC IoT SECURITY PLATFORM
            </span>

            <h1>
              Secure IoT
              <br />
              Communication Monitor
            </h1>

            <p>
              Real-time visibility into encrypted device
              communication, sensor telemetry and security events.
            </p>

          </div>

          <div className="hero-action">

            <div className="security-score">

              <div className="score-circle">
                <strong>{securityScore}</strong>
                <span>%</span>
              </div>

              <div>
                <strong>Security Score</strong>
                <small>Protection level</small>
              </div>

            </div>

            <button
              className="primary-button"
              onClick={generateSecureReading}
            >
              <span>+</span>
              Generate Secure Reading
            </button>

          </div>

        </section>


        {/* KPI CARDS */}

        <section className="kpi-grid">

          <div className="kpi-card">

            <div className="kpi-icon green-icon">
              ◉
            </div>

            <div>
              <span>DEVICE STATUS</span>

              <h3>
                {status?.status || "UNKNOWN"}
              </h3>

              <small>
                {status?.device_id || "IOT-001"}
              </small>
            </div>

            <div className="kpi-live">
              ONLINE
            </div>

          </div>


          <div className="kpi-card">

            <div className="kpi-icon blue-icon">
              ⇄
            </div>

            <div>
              <span>SECURE MESSAGES</span>

              <h3>
                {secureMessages}
              </h3>

              <small>
                ECC + AES protected
              </small>
            </div>

            <div className="kpi-live blue">
              SECURE
            </div>

          </div>


          <div className="kpi-card">

            <div className="kpi-icon orange-icon">
              !
            </div>

            <div>
              <span>REPLAY ATTACKS</span>

              <h3>
                {replayBlocked}
              </h3>

              <small>
                Messages blocked
              </small>
            </div>

            <div className="kpi-live orange">
              BLOCKED
            </div>

          </div>


          <div className="kpi-card">

            <div className="kpi-icon red-icon">
              ⚠
            </div>

            <div>
              <span>TAMPERING ATTACKS</span>

              <h3>
                {tamperingBlocked}
              </h3>

              <small>
                Integrity violations
              </small>
            </div>

            <div className="kpi-live red">
              BLOCKED
            </div>

          </div>

        </section>


        {/* DEVICE + SECURITY */}

        <section className="dashboard-grid">

          <div className="panel">

            <div className="panel-header">

              <div>

                <span className="panel-label">
                  LIVE TELEMETRY
                </span>

                <h2>
                  Device Monitoring
                </h2>

                <p>
                  Real-time sensor information from IoT-001
                </p>

              </div>

              <span className="live-badge">
                ● LIVE
              </span>

            </div>


            <div className="telemetry-grid">

              <div className="telemetry-card temperature">

                <div className="telemetry-top">
                  <span>Temperature</span>
                  <span className="telemetry-symbol">°</span>
                </div>

                <strong>
                  {status?.temperature ?? "--"}
                  <small>°C</small>
                </strong>

                <p>
                  Current sensor reading
                </p>

              </div>


              <div className="telemetry-card humidity">

                <div className="telemetry-top">
                  <span>Humidity</span>
                  <span className="telemetry-symbol">%</span>
                </div>

                <strong>
                  {status?.humidity ?? "--"}
                  <small>%</small>
                </strong>

                <p>
                  Current sensor reading
                </p>

              </div>

            </div>


            <div className="device-details">

              <div>
                <span>DEVICE ID</span>

                <strong>
                  {status?.device_id || "IOT-001"}
                </strong>
              </div>

              <div>
                <span>STATUS</span>

                <strong className="text-green">
                  ● {status?.status || "ONLINE"}
                </strong>
              </div>

              <div>
                <span>LAST COMMUNICATION</span>

                <strong>
                  {status?.last_updated || "N/A"}
                </strong>
              </div>

            </div>

          </div>


          {/* PROTECTION STACK */}

          <div className="panel">

            <div className="panel-header">

              <div>

                <span className="panel-label">
                  SECURITY ENGINE
                </span>

                <h2>
                  Protection Stack
                </h2>

                <p>
                  Active cryptographic mechanisms
                </p>

              </div>

              <div className="shield-icon">
                ✓
              </div>

            </div>


            <div className="security-stack">

              <div className="security-layer">

                <div className="layer-icon ecc">
                  E
                </div>

                <div>
                  <strong>ECC / ECDH</strong>
                  <span>Secure key exchange</span>
                </div>

                <b>ACTIVE</b>

              </div>


              <div className="security-layer">

                <div className="layer-icon aes">
                  A
                </div>

                <div>
                  <strong>AES-256-GCM</strong>
                  <span>Authenticated encryption</span>
                </div>

                <b>ACTIVE</b>

              </div>


              <div className="security-layer">

                <div className="layer-icon replay">
                  R
                </div>

                <div>
                  <strong>Replay Protection</strong>
                  <span>Unique message validation</span>
                </div>

                <b>ACTIVE</b>

              </div>


              <div className="security-layer">

                <div className="layer-icon log">
                  L
                </div>

                <div>
                  <strong>Security Logging</strong>
                  <span>Persistent audit records</span>
                </div>

                <b>ACTIVE</b>

              </div>

            </div>

          </div>

        </section>


        {/* CHART */}

        <section className="panel chart-panel">

          <div className="panel-header">

            <div>

              <span className="panel-label">
                SENSOR ANALYTICS
              </span>

              <h2>
                Environmental Telemetry
              </h2>

              <p>
                Temperature and humidity trends from recent readings
              </p>

            </div>

            <span className="records-badge">
              {history.length} RECORDS
            </span>

          </div>


          <div className="chart-container">

            {chartData.length > 0 ? (

              <ResponsiveContainer
                width="100%"
                height={350}
              >

                <LineChart data={chartData}>

                  <CartesianGrid
                    strokeDasharray="3 3"
                    stroke="#263247"
                  />

                  <XAxis
                    dataKey="id"
                    stroke="#718096"
                    tick={{ fill: "#718096" }}
                  />

                  <YAxis
                    stroke="#718096"
                    tick={{ fill: "#718096" }}
                  />

                  <Tooltip
                    contentStyle={{
                      background: "#111827",
                      border: "1px solid #263247",
                      borderRadius: "10px",
                      color: "#ffffff",
                    }}
                  />

                  <Legend />

                  <Line
                    type="monotone"
                    dataKey="temperature"
                    name="Temperature °C"
                    stroke="#ff6b6b"
                    strokeWidth={3}
                    dot={{ r: 4 }}
                    activeDot={{ r: 7 }}
                  />

                  <Line
                    type="monotone"
                    dataKey="humidity"
                    name="Humidity %"
                    stroke="#38bdf8"
                    strokeWidth={3}
                    dot={{ r: 4 }}
                    activeDot={{ r: 7 }}
                  />

                </LineChart>

              </ResponsiveContainer>

            ) : (

              <div className="empty-state">
                No sensor data available yet.
              </div>

            )}

          </div>

        </section>


        {/* SECURITY EVENTS + THREAT SUMMARY */}

        <section className="dashboard-grid">

          <div className="panel">

            <div className="panel-header">

              <div>

                <span className="panel-label">
                  THREAT MONITORING
                </span>

                <h2>
                  Security Events
                </h2>

                <p>
                  {lastSecurityEvent}
                </p>

              </div>

              <span className="live-badge">
                LIVE
              </span>

            </div>


            <div className="event-list">

              {securityLogs.length === 0 ? (

                <div className="empty-event">

                  <span>✓</span>

                  <div>
                    <strong>
                      No security events
                    </strong>

                    <p>
                      Waiting for backend activity
                    </p>
                  </div>

                </div>

              ) : (

                securityLogs
                  .slice(0, 7)
                  .map((log) => {

                    const blocked =
                      log.status === "BLOCKED";

                    return (

                      <div
                        className={`security-event ${
                          blocked
                            ? "blocked"
                            : "success-event"
                        }`}
                        key={log.id}
                      >

                        <div className="event-status">
                          {blocked ? "!" : "✓"}
                        </div>

                        <div className="event-content">

                          <div className="event-title-row">

                            <strong>
                              {log.event.replaceAll(
                                "_",
                                " "
                              )}
                            </strong>

                            <span>
                              {log.status}
                            </span>

                          </div>

                          <p>
                            {log.details}
                          </p>

                          <small>
                            {log.timestamp}
                          </small>

                        </div>

                      </div>

                    );

                  })

              )}

            </div>

          </div>


          {/* THREAT SUMMARY */}

          <div className="panel threat-panel">

            <div className="panel-header">

              <div>

                <span className="panel-label">
                  THREAT SUMMARY
                </span>

                <h2>
                  Attack Prevention
                </h2>

                <p>
                  Security mechanisms actively blocking threats
                </p>

              </div>

              <div className="shield-large">
                ✓
              </div>

            </div>


            <div className="threat-stat">

              <div className="threat-number">
                {totalThreats}
              </div>

              <div>

                <strong>
                  Total Threats Blocked
                </strong>

                <span>
                  Across replay and integrity protection
                </span>

              </div>

            </div>


            <div className="threat-bars">

              <div>

                <div className="bar-header">
                  <span>Replay Attacks</span>
                  <strong>{replayBlocked}</strong>
                </div>

                <div className="bar">

                  <span
                    style={{
                      width: `${Math.min(
                        replayBlocked * 20,
                        100
                      )}%`,
                    }}
                  ></span>

                </div>

              </div>


              <div>

                <div className="bar-header">
                  <span>Tampering Attacks</span>
                  <strong>{tamperingBlocked}</strong>
                </div>

                <div className="bar">

                  <span
                    style={{
                      width: `${Math.min(
                        tamperingBlocked * 20,
                        100
                      )}%`,
                    }}
                  ></span>

                </div>

              </div>

            </div>


            <div className="protection-message">

              <span>✓</span>

              <div>

                <strong>
                  Protection Active
                </strong>

                <p>
                  AES-GCM authentication is protecting
                  message integrity.
                </p>

              </div>

            </div>

          </div>

        </section>


        {/* LATEST SECURE READING */}

        {status && (

          <section className="panel">

            <div className="panel-header">

              <div>

                <span className="panel-label">
                  SECURE PAYLOAD
                </span>

                <h2>
                  Latest Secure Reading
                </h2>

                <p>
                  Most recent protected IoT transmission
                </p>

              </div>

              <span className="encrypted-badge">
                🔒 ENCRYPTED
              </span>

            </div>


            <div className="secure-data-grid">

              <div>
                <span>DEVICE ID</span>
                <strong>{status.device_id}</strong>
              </div>

              <div>
                <span>TEMPERATURE</span>
                <strong>
                  {status.temperature} °C
                </strong>
              </div>

              <div>
                <span>HUMIDITY</span>
                <strong>
                  {status.humidity} %
                </strong>
              </div>

              <div>
                <span>DEVICE STATUS</span>

                <strong className="text-green">
                  {status.status}
                </strong>
              </div>

              <div>
                <span>CRYPTOGRAPHY</span>

                <strong className="text-blue">
                  ECC + AES-256-GCM
                </strong>
              </div>

              <div>
                <span>LAST UPDATED</span>

                <strong>
                  {status.last_updated || "N/A"}
                </strong>
              </div>

            </div>

          </section>

        )}


        {/* SENSOR ACTIVITY */}

        <section className="panel">

          <div className="panel-header">

            <div>

              <span className="panel-label">
                DATABASE
              </span>

              <h2>
                Sensor Activity
              </h2>

              <p>
                Historical IoT communication records
              </p>

            </div>

            <span className="records-badge">
              {history.length} RECORDS
            </span>

          </div>


          <div className="table-wrapper">

            <table>

              <thead>

                <tr>
                  <th>ID</th>
                  <th>DEVICE</th>
                  <th>TEMPERATURE</th>
                  <th>HUMIDITY</th>
                  <th>STATUS</th>
                  <th>TIMESTAMP</th>
                </tr>

              </thead>


              <tbody>

                {history.length === 0 ? (

                  <tr>

                    <td
                      colSpan="6"
                      className="table-empty"
                    >
                      No sensor records available
                    </td>

                  </tr>

                ) : (

                  history.slice(0, 12).map((item) => (

                    <tr key={item.id}>

                      <td>
                        <span className="record-id">
                          #{item.id}
                        </span>
                      </td>

                      <td>
                        <strong>
                          {item.device_id}
                        </strong>
                      </td>

                      <td>
                        {item.temperature} °C
                      </td>

                      <td>
                        {item.humidity} %
                      </td>

                      <td>

                        <span className="status-pill">
                          <span></span>
                          {item.status}
                        </span>

                      </td>

                      <td className="timestamp">
                        {item.timestamp}
                      </td>

                    </tr>

                  ))

                )}

              </tbody>

            </table>

          </div>

        </section>


        {/* FOOTER */}

        <footer className="footer">

          <div>

            <strong>
              Secure IoT Communication Platform
            </strong>

            <span>
              ECC + ECDH • AES-256-GCM • Replay Protection
            </span>

          </div>

          <div className="footer-secure">

            <span></span>

            All Security Systems Operational

          </div>

        </footer>

      </main>

    </div>
  );
}

export default App;