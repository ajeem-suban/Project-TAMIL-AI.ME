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

function VerseCard({ r, isRandom = false }) {
  const [expanded, setExpanded] = useState(false)

  return (
    <div style={isRandom ? styles.randomCard : styles.card}>
      {/* Header */}
      <div style={styles.cardHeader}>
        <span style={styles.badge}>{r.source} #{r.number}</span>
        {r.period && <span style={styles.periodBadge}>{r.period}</span>}
        {r.poet && <span style={styles.poet}>— {r.poet}</span>}
      </div>

      {/* Tamil verse */}
      <p style={styles.tamil}>{r.tamil}</p>

      {/* Transliteration */}
      {r.transliteration && (
        <p style={styles.transliteration}>{r.transliteration}</p>
      )}

      {/* Topic */}
      {r.topic && (
        <p style={styles.topic}>📌 {r.topic}</p>
      )}

      {/* English translation */}
      {r.translation && (
        <p style={styles.translation}>🇬🇧 {r.translation}</p>
      )}

      {/* Couplet */}
      {r.couplet && (
        <p style={styles.couplet}>✒️ {r.couplet}</p>
      )}

      {/* Show More button */}
      {(r.translation_ta || r.explanation) && (
        <button
          style={styles.expandBtn}
          onClick={() => setExpanded(!expanded)}
        >
          {expanded ? "▲ Show Less" : "▼ Show More"}
        </button>
      )}

      {/* Expanded content */}
      {expanded && (
        <div style={styles.expandedSection}>
          {r.translation_ta && (
            <div style={styles.expandedBlock}>
              <span style={styles.expandedLabel}>தமிழ் விளக்கம்</span>
              <p style={styles.expandedText}>{r.translation_ta}</p>
            </div>
          )}
          {r.explanation && (
            <div style={styles.expandedBlock}>
              <span style={styles.expandedLabel}>Explanation</span>
              <p style={styles.expandedText}>{r.explanation}</p>
            </div>
          )}
        </div>
      )}
    </div>
  )
}

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
      setRandom(null)
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
      setResults([])
    } catch {
      alert("API not reachable. Is backend running?")
    }
    setLoading(false)
  }

  return (
    <div style={styles.container}>
      <h1 style={styles.title}>🏛️ Tamil AI</h1>
      <p style={styles.subtitle}>
        4,592 verses · Thirukkural · Sangam · Post-Sangam Classical Tamil
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
        <>
          <h3 style={styles.resultsTitle}>🎲 Random Verse</h3>
          <VerseCard r={random} isRandom={true} />
        </>
      )}

      {/* Search Results */}
      {results.length > 0 && (
        <>
          <h3 style={styles.resultsTitle}>Results for "{query}"</h3>
          {results.map((r, i) => (
            <VerseCard key={i} r={r} />
          ))}
        </>
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
  },
  cardHeader: {
    display: "flex",
    alignItems: "center",
    gap: "0.5rem",
    flexWrap: "wrap",
    marginBottom: "0.75rem"
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
  periodBadge: {
    backgroundColor: "#2a2a2a",
    color: "#888",
    padding: "2px 8px",
    borderRadius: "20px",
    fontSize: "0.7rem",
    border: "1px solid #444"
  },
  tamil: {
    fontSize: "1.15rem",
    lineHeight: "1.8",
    margin: "0.5rem 0",
    color: "#f0e6d3"
  },
  transliteration: {
    color: "#888",
    fontSize: "0.85rem",
    fontStyle: "italic",
    margin: "0.25rem 0"
  },
  topic: {
    color: "#b8860b",
    fontSize: "0.85rem",
    margin: "0.25rem 0"
  },
  translation: {
    color: "#aaa",
    fontSize: "0.95rem",
    margin: "0.5rem 0"
  },
  couplet: {
    color: "#c8a96e",
    fontStyle: "italic",
    fontSize: "0.9rem",
    margin: "0.5rem 0",
    borderLeft: "2px solid #d4af37",
    paddingLeft: "0.75rem"
  },
  poet: {
    color: "#d4af37",
    fontSize: "0.85rem"
  },
  expandBtn: {
    background: "transparent",
    border: "1px solid #444",
    color: "#888",
    padding: "4px 12px",
    borderRadius: "20px",
    fontSize: "0.8rem",
    cursor: "pointer",
    marginTop: "0.5rem"
  },
  expandedSection: {
    marginTop: "0.75rem",
    borderTop: "1px solid #333",
    paddingTop: "0.75rem"
  },
  expandedBlock: {
    marginBottom: "0.75rem"
  },
  expandedLabel: {
    color: "#d4af37",
    fontSize: "0.75rem",
    fontWeight: "bold",
    textTransform: "uppercase",
    letterSpacing: "0.05em"
  },
  expandedText: {
    color: "#c8b89a",
    fontSize: "0.95rem",
    lineHeight: "1.7",
    margin: "0.25rem 0 0 0"
  },
  resultsTitle: {
    color: "#d4af37",
    marginBottom: "1rem"
  }
}
