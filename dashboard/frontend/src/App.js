import { useState, useEffect } from "react";
import axios from "axios";
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell, Legend
} from "recharts";

const API = "http://localhost:8000";
const COLORS = ["#1F4E79", "#e74c3c"];

function StatCard({ title, value, sub, color }) {
  return (
    <div style={{
      background: "#fff", borderRadius: 12, padding: "24px 28px",
      boxShadow: "0 2px 12px rgba(0,0,0,0.08)", flex: 1, minWidth: 180
    }}>
      <div style={{ fontSize: 13, color: "#888", marginBottom: 6 }}>{title}</div>
      <div style={{ fontSize: 32, fontWeight: 700, color: color || "#1F4E79" }}>{value}</div>
      {sub && <div style={{ fontSize: 12, color: "#aaa", marginTop: 4 }}>{sub}</div>}
    </div>
  );
}

export default function App() {
  const [stats, setStats] = useState(null);
  const [fraudByHour, setFraudByHour] = useState([]);
  const [recentFraud, setRecentFraud] = useState([]);
  const [amountDist, setAmountDist] = useState([]);

  useEffect(() => {
    const fetchAll = async () => {
      const [s, h, r, a] = await Promise.all([
        axios.get(`${API}/stats`),
        axios.get(`${API}/fraud-by-hour`),
        axios.get(`${API}/recent-fraud`),
        axios.get(`${API}/amount-distribution`),
      ]);
      setStats(s.data);
      setFraudByHour(h.data);
      setRecentFraud(r.data);
      setAmountDist(a.data);
    };
    fetchAll();
    const interval = setInterval(fetchAll, 5000); // refresh every 5s
    return () => clearInterval(interval);
  }, []);

  if (!stats) return (
    <div style={{ display: "flex", justifyContent: "center", alignItems: "center", height: "100vh", background: "#f0f4f8" }}>
      <div style={{ fontSize: 18, color: "#1F4E79" }}>Loading dashboard...</div>
    </div>
  );

  const pieData = [
    { name: "Legitimate", value: stats.total_transactions - stats.total_fraud },
    { name: "Fraud", value: stats.total_fraud },
  ];

  return (
    <div style={{ minHeight: "100vh", background: "#f0f4f8", fontFamily: "Arial, sans-serif" }}>
      {/* Header */}
      <div style={{ background: "#1F4E79", padding: "20px 40px", color: "#fff" }}>
        <h1 style={{ margin: 0, fontSize: 24, fontWeight: 700 }}>
          💳 Real-Time Payment Fraud Detection
        </h1>
        <div style={{ fontSize: 13, opacity: 0.7, marginTop: 4 }}>
          Live pipeline · Kafka + XGBoost + PostgreSQL · Refreshes every 5s
        </div>
      </div>

      <div style={{ padding: "32px 40px" }}>
        {/* Stat Cards */}
        <div style={{ display: "flex", gap: 20, marginBottom: 32, flexWrap: "wrap" }}>
          <StatCard
            title="Total Transactions"
            value={Number(stats.total_transactions).toLocaleString()}
            sub="processed by pipeline"
          />
          <StatCard
            title="Fraud Detected"
            value={Number(stats.total_fraud).toLocaleString()}
            sub="flagged by ML model"
            color="#e74c3c"
          />
          <StatCard
            title="Fraud Rate"
            value={`${stats.fraud_rate}%`}
            sub="of all transactions"
            color="#e67e22"
          />
          <StatCard
            title="Avg Transaction"
            value={`$${stats.avg_amount}`}
            sub="across all transactions"
          />
        </div>

        {/* Charts Row */}
        <div style={{ display: "flex", gap: 24, marginBottom: 32, flexWrap: "wrap" }}>
          {/* Fraud by Hour */}
          <div style={{ background: "#fff", borderRadius: 12, padding: 24, flex: 2, minWidth: 300, boxShadow: "0 2px 12px rgba(0,0,0,0.08)" }}>
            <h3 style={{ margin: "0 0 20px", color: "#1F4E79", fontSize: 15 }}>Fraud Count by Hour of Day</h3>
            <ResponsiveContainer width="100%" height={220}>
              <BarChart data={fraudByHour}>
                <XAxis dataKey="hour_of_day" tick={{ fontSize: 11 }} label={{ value: "Hour", position: "insideBottom", offset: -2, fontSize: 11 }} />
                <YAxis tick={{ fontSize: 11 }} />
                <Tooltip />
                <Bar dataKey="fraud_count" fill="#e74c3c" radius={[4, 4, 0, 0]} name="Fraud" />
                <Bar dataKey="total" fill="#1F4E79" radius={[4, 4, 0, 0]} name="Total" />
              </BarChart>
            </ResponsiveContainer>
          </div>

          {/* Pie Chart */}
          <div style={{ background: "#fff", borderRadius: 12, padding: 24, flex: 1, minWidth: 250, boxShadow: "0 2px 12px rgba(0,0,0,0.08)" }}>
            <h3 style={{ margin: "0 0 20px", color: "#1F4E79", fontSize: 15 }}>Transaction Breakdown</h3>
            <ResponsiveContainer width="100%" height={220}>
              <PieChart>
                <Pie data={pieData} cx="50%" cy="50%" outerRadius={80} dataKey="value" label={({percent }) => `${(percent * 100).toFixed(1)}%`} labelLine={false} fontSize={11}>
                  {pieData.map((_, i) => <Cell key={i} fill={COLORS[i]} />)}
                </Pie>
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          </div>

          {/* Amount Distribution */}
          <div style={{ background: "#fff", borderRadius: 12, padding: 24, flex: 1, minWidth: 250, boxShadow: "0 2px 12px rgba(0,0,0,0.08)" }}>
            <h3 style={{ margin: "0 0 20px", color: "#1F4E79", fontSize: 15 }}>Amount Distribution</h3>
            <ResponsiveContainer width="100%" height={220}>
              <BarChart data={amountDist}>
                <XAxis dataKey="range" tick={{ fontSize: 11 }} />
                <YAxis tick={{ fontSize: 11 }} />
                <Tooltip />
                <Bar dataKey="count" fill="#1F4E79" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Recent Fraud Table */}
        <div style={{ background: "#fff", borderRadius: 12, padding: 24, boxShadow: "0 2px 12px rgba(0,0,0,0.08)" }}>
          <h3 style={{ margin: "0 0 20px", color: "#1F4E79", fontSize: 15 }}>🚨 Recent Fraud Detections</h3>
          <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 13 }}>
            <thead>
              <tr style={{ background: "#f0f4f8" }}>
                {["Transaction ID", "Amount", "Merchant", "Currency", "Hour", "International", "Fraud Score"].map(h => (
                  <th key={h} style={{ padding: "10px 12px", textAlign: "left", color: "#555", fontWeight: 600 }}>{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {recentFraud.map((t, i) => (
                <tr key={i} style={{ borderBottom: "1px solid #f0f4f8" }}>
                  <td style={{ padding: "10px 12px", color: "#888", fontSize: 11 }}>{t.transaction_id.slice(0, 8)}...</td>
                  <td style={{ padding: "10px 12px", fontWeight: 600, color: "#e74c3c" }}>${t.amount}</td>
                  <td style={{ padding: "10px 12px" }}>{t.merchant}</td>
                  <td style={{ padding: "10px 12px" }}>{t.currency}</td>
                  <td style={{ padding: "10px 12px" }}>{t.hour_of_day}:00</td>
                  <td style={{ padding: "10px 12px" }}>{t.is_international ? "Yes" : "No"}</td>
                  <td style={{ padding: "10px 12px" }}>
                    <span style={{
                      background: t.fraud_score > 0.7 ? "#fde8e8" : "#fff3e0",
                      color: t.fraud_score > 0.7 ? "#e74c3c" : "#e67e22",
                      padding: "3px 8px", borderRadius: 20, fontWeight: 600, fontSize: 12
                    }}>
                      {(t.fraud_score * 100).toFixed(1)}%
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}