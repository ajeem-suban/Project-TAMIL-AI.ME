import { useState } from "react"
import axios from "axios"

const API = "http://localhost:8000"

const SOURCES = [
  { value: "all",               label: "All Texts" },
  { value: "thirukkural",       label: "Thirukkural" },
  { value: "purananuru",        label: "Purananuru" },
  { value: "akananuru",         label: "Akananuru" },
  { value: "kurunthogai",       label: "Kurunthogai" },
  { value: "narrinai",          label: "Narrinai" },
  { value: "kalithogai",        label: "Kalithogai" },
  { value: "paripadal",         label: "Paripadal" },
  { value: "pathirruppattu",    label: "Pathirruppattu" },
  { value: "madurai_kanji",     label: "Madurai Kanji" },
  { value: "malaipadukadam",    label: "Malaipadukadam" },
  { value: "nedunalvaadai",     label: "Nedunalvaadai" },
  { value: "kurinjippattu",     label: "Kurinjippattu" },
  { value: "pattinapalai",      label: "Pattinapalai" },
  { value: "mullaipattu",       label: "Mullaipattu" },
  { value: "perumpanatrupadai", label: "Perumpanatrupadai" },
  { value: "naaladiyar",        label: "Naaladiyar" },
  { value: "acharakovai",       label: "Acharakovai" },
  { value: "mudhumozhikanchi",  label: "Mudhumozhikanchi" },
  { value: "naanmanikadikai",   label: "Naanmanikadikai" },
  { value: "iniyavainarpadhu",  label: "Iniyavainarpadhu" },
  { value: "innanarpadhu",      label: "Innanarpadhu" },
  { value: "thirikadugam",      label: "Thirikadugam" },
]

export default function App() {
  const [query, setQuery] = useState("")
  const [results, setResults] = useState([])
  const [random, setRandom] = useState(null)
  const [loading, setLoading] = useState(false)
  const [source, setSource] = useState("all")

  const search = async () => {
    if (!query.trim()) return
    setLoading(true)
    try {
      const res = await axios.get(`${API}/search`, {
        params: { query, source, n: 5 }
      })
      setResults(res.data.results)
    } catch {
      alert("API not reachable. Is backend running?")
    }
    setLoading(false)
  }

  const getRandom = async () => {
    setLoading(true)
    try {
      const res = await axios.get(`${API}/random`)
      setRandom(res.data)
    } catch {
      alert("API not reachable. Is backend running?")
    }
    setLoading(false)
  }

  return (
    <div style={styles.container}>
      <h1 style={styles.title}>🏛️ Tamil AI — Classical Corpus Search</h1>
      <p style={styles.subtitle}>
        Search across 4,592 verses · Thirukkural · Sangam · Post-Sangam
      </p>

      {/* Search Bar */}
      <div style={styles.searchBox}>
        <input
          style={styles.input}
          value={query}
          onChange={e => setQuery(e.target.value)}
          onKeyDown={e => e.key === "Enter" && search()}
          placeholder="Search in Tamil or English... (e.g. love, war, rain)"
        />
        <select
          style={styles.select}
          value={source}
          onChange={e => setSource(e.target.value)}
        >
          {SOURCES.map(s => (
            <option key={s.value} value={s.value}>{s.label}</option>
          ))}
        </select>
        <button style={styles.btn} onClick={search}>
          {loading ? "Searching..." : "Search"}
        </button>
        <button style={styles.btnSecondary} onClick={getRandom}>
          🎲 Random
        </button>
      </div>

      {/* Random Verse */}
      {random && (
        <div style={styles.randomCard}>
          <span style={styles.badge}>{random.source} #{random.number}</span>
          <p style={styles.tamil}>{random.tamil}</p>
          {random.translation && (
            <p style={styles.translation}>"{random.translation}"</p>
          )}
          {random.poet && <p style={styles.poet}>— {random.poet}</p>}
        </div>
      )}

      {/* Search Results */}
      {results.length > 0 && (
        <div>
          <h3 style={styles.resultsTitle}>Results for "{query}"</h3>
          {results.map((r, i) => (
            <div key={i} style={styles.card}>
              <span style={styles.badge}>{r.source} #{r.number}</span>
              <p style={styles.tamil}>{r.tamil}</p>
              {r.translation && (
                <p style={styles.translation}>"{r.translation}"</p>
              )}
              {r.poet && <p style={styles.poet}>— {r.poet}</p>}
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

const styles = {
  container: {
    maxWidth: "800px",
    margin: "0 auto",
    padding: "2rem",
    fontFamily: "Georgia, serif",
    backgroundColor: "#0f0f0f",
    minHeight: "100vh",
    color: "#f0e6d3"
  },
  title: {
    fontSize: "2rem",
    color: "#d4af37",
    textAlign: "center",
    marginBottom: "0.5rem"
  },
  subtitle: {
    textAlign: "center",
    color: "#888",
    marginBottom: "2rem",
    fontSize: "0.95rem"
  },
  searchBox: {
    display: "flex",
    gap: "0.5rem",
    marginBottom: "1.5rem",
    flexWrap: "wrap"
  },
  input: {
    flex: 1,
    padding: "0.75rem",
    fontSize: "1rem",
    borderRadius: "8px",
    border: "1px solid #d4af37",
    backgroundColor: "#1a1a1a",
    color: "#f0e6d3",
    minWidth: "200px"
  },
  select: {
    padding: "0.75rem",
    borderRadius: "8px",
    border: "1px solid #d4af37",
    backgroundColor: "#1a1a1a",
    color: "#f0e6d3",
    fontSize: "0.9rem"
  },
  btn: {
    padding: "0.75rem 1.5rem",
    backgroundColor: "#d4af37",
    color: "#0f0f0f",
    border: "none",
    borderRadius: "8px",
    fontSize: "1rem",
    cursor: "pointer",
    fontWeight: "bold"
  },
  btnSecondary: {
    padding: "0.75rem 1.5rem",
    backgroundColor: "transparent",
    color: "#d4af37",
    border: "1px solid #d4af37",
    borderRadius: "8px",
    fontSize: "1rem",
    cursor: "pointer"
  },
  card: {
    backgroundColor: "#1a1a1a",
    border: "1px solid #333",
    borderRadius: "12px",
    padding: "1.25rem",
    marginBottom: "1rem",
    borderLeft: "4px solid #d4af37"
  },
  randomCard: {
    backgroundColor: "#1a1a2e",
    border: "1px solid #d4af37",
    borderRadius: "12px",
    padding: "1.5rem",
    marginBottom: "1.5rem",
    textAlign: "center"
  },
  badge: {
    backgroundColor: "#d4af37",
    color: "#0f0f0f",
    padding: "2px 10px",
    borderRadius: "20px",
    fontSize: "0.75rem",
    fontWeight: "bold",
    textTransform: "uppercase"
  },
  tamil: {
    fontSize: "1.15rem",
    lineHeight: "1.8",
    margin: "0.75rem 0",
    color: "#f0e6d3"
  },
  translation: {
    color: "#aaa",
    fontStyle: "italic",
    fontSize: "0.95rem",
    margin: "0.5rem 0"
  },
  poet: {
    color: "#d4af37",
    fontSize: "0.85rem",
    margin: "0.25rem 0"
  },
  resultsTitle: {
    color: "#d4af37",
    marginBottom: "1rem"
  }
}
