import { useMemo, useState } from 'react'

type FlowStep = {
  action: string
  description: string
  url?: string | null
  selector?: string | null
  query?: string | null
  urls?: string[] | null
  from_step?: number | null
  fields?: Record<string, string> | null
  wait_ms?: number | null
}
type FlowPlan = { goal: string; summary: string; steps: FlowStep[] }
type FlowEvent = {
  kind: 'plan_created' | 'step_started' | 'step_finished' | 'step_failed' | 'run_finished'
  step_index: number | null
  message: string
  data?: Record<string, unknown> | null
}

const EVENT_ICON: Record<FlowEvent['kind'], string> = {
  plan_created: '📋',
  step_started: '▶️',
  step_finished: '✅',
  step_failed: '❌',
  run_finished: '🏁',
}

function toCsv(rows: Record<string, unknown>[], columns: string[]): string {
  const cols = columns.length ? columns : [...new Set(rows.flatMap((r) => Object.keys(r)))]
  const esc = (v: unknown) => {
    const s = v === null || v === undefined ? '' : String(v)
    return /[",\n]/.test(s) ? `"${s.replace(/"/g, '""')}"` : s
  }
  return [cols.join(','), ...rows.map((r) => cols.map((c) => esc(r[c])).join(','))].join('\n')
}

function downloadCsv(rows: Record<string, unknown>[], columns: string[]) {
  const blob = new Blob([toCsv(rows, columns)], { type: 'text/csv;charset=utf-8' })
  const a = document.createElement('a')
  a.href = URL.createObjectURL(blob)
  a.download = 'flowpilot-results.csv'
  a.click()
  URL.revokeObjectURL(a.href)
}

export default function App() {
  const [goal, setGoal] = useState('')
  const [plan, setPlan] = useState<FlowPlan | null>(null)
  const [events, setEvents] = useState<FlowEvent[]>([])
  const [rows, setRows] = useState<Record<string, unknown>[]>([])
  const [columns, setColumns] = useState<string[]>([])
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')

  const finishedAt = useMemo(() => {
    const failed = new Set(events.filter((e) => e.kind === 'step_failed').map((e) => e.step_index))
    const done = new Set(events.filter((e) => e.kind === 'step_finished').map((e) => e.step_index))
    return { failed, done }
  }, [events])

  async function makePlan() {
    setBusy(true)
    setError('')
    setEvents([])
    setRows([])
    setColumns([])
    setPlan(null)
    try {
      const res = await fetch('/api/plan', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ goal }),
      })
      if (!res.ok) throw new Error((await res.json()).detail ?? `plan failed (${res.status})`)
      setPlan(await res.json())
    } catch (e) {
      setError(String(e instanceof Error ? e.message : e))
    } finally {
      setBusy(false)
    }
  }

  async function runPlan() {
    if (!plan) return
    setBusy(true)
    setError('')
    setEvents([])
    setRows([])
    setColumns([])
    try {
      const res = await fetch('/api/run', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(plan),
      })
      if (!res.ok || !res.body) throw new Error(`run failed (${res.status})`)
      const reader = res.body.getReader()
      const decoder = new TextDecoder()
      let buffer = ''
      for (;;) {
        const { done, value } = await reader.read()
        if (done) break
        buffer += decoder.decode(value, { stream: true })
        const chunks = buffer.split('\n\n')
        buffer = chunks.pop() ?? ''
        for (const chunk of chunks) {
          const payload = chunk.replace(/^data: /, '').trim()
          if (!payload) continue
          const event = JSON.parse(payload) as FlowEvent
          setEvents((prev) => [...prev, event])
          const dataRows = event.data?.rows
          if (Array.isArray(dataRows) && dataRows.length && typeof dataRows[0] === 'object') {
            setRows(dataRows as Record<string, unknown>[])
            if (Array.isArray(event.data?.columns)) setColumns(event.data.columns as string[])
          }
        }
      }
    } catch (e) {
      setError(String(e instanceof Error ? e.message : e))
    } finally {
      setBusy(false)
    }
  }

  return (
    <main className="app">
      <h1>FlowPilot</h1>
      <p className="tagline">
        Plain-English web process automation — <strong>Nemotron</strong> plans, <strong>Tavily</strong> reads the web,
        <strong> Playwright</strong> executes.
      </p>

      <section className="card">
        <textarea
          value={goal}
          onChange={(e) => setGoal(e.target.value)}
          placeholder={'Describe a repetitive web task, e.g.\n"Collect the support emails from the pricing pages of these 20 companies"\n"Search example.com for robots and put the first 10 results with links into a table"'}
          rows={3}
        />
        <div className="row">
          <button onClick={makePlan} disabled={busy || !goal.trim()}>
            {busy ? 'Working…' : '1 · Plan'}
          </button>
          {plan && (
            <button className="primary" onClick={runPlan} disabled={busy}>
              2 · Run
            </button>
          )}
        </div>
      </section>

      {error && <section className="card error">{error}</section>}

      {plan && (
        <section className="card">
          <h2>Plan {plan.summary ? <span className="summary">— {plan.summary}</span> : null}</h2>
          <ol className="steps">
            {plan.steps.map((s, i) => (
              <li key={i} className={finishedAt.failed.has(i) ? 'failed' : finishedAt.done.has(i) ? 'done' : ''}>
                <code>{s.action}</code> {s.description}
                {s.url ? <span className="meta"> → {s.url}</span> : null}
                {s.query ? <span className="meta"> → “{s.query}”</span> : null}
              </li>
            ))}
          </ol>
        </section>
      )}

      {events.length > 0 && (
        <section className="card">
          <h2>Execution</h2>
          <ul className="events">
            {events.map((e, i) => (
              <li key={i} className={e.kind}>
                <span className="icon">{EVENT_ICON[e.kind]}</span> {e.message}
              </li>
            ))}
          </ul>
        </section>
      )}

      {rows.length > 0 && (
        <section className="card">
          <h2>
            Results ({rows.length} rows)
            <button className="small" onClick={() => downloadCsv(rows, columns)}>
              Export CSV
            </button>
          </h2>
          <div className="tablewrap">
            <table>
              <thead>
                <tr>
                  {(columns.length ? columns : [...new Set(rows.flatMap((r) => Object.keys(r)))]).map((c) => (
                    <th key={c}>{c}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {rows.map((r, i) => (
                  <tr key={i}>
                    {(columns.length ? columns : Object.keys(r)).map((c) => (
                      <td key={c}>
                        {typeof r[c] === 'string' && /^https?:\/\//.test(r[c] as string) ? (
                          <a href={r[c] as string} target="_blank" rel="noreferrer">
                            {(r[c] as string).length > 48 ? `${(r[c] as string).slice(0, 48)}…` : r[c]}
                          </a>
                        ) : (
                          String(r[c] ?? '—')
                        )}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>
      )}
    </main>
  )
}
