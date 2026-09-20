import React, { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import client from '../api/client'
import Loading from '../components/Loading'
import { useAuth } from '../context/AuthContext'

// Simple force-free radial layout — no extra graph library dependency needed.
function layoutNodes(nodes) {
  const R = 180
  const cx = 260, cy = 220
  return nodes.map((n, i) => {
    const angle = (2 * Math.PI * i) / Math.max(nodes.length, 1)
    return { ...n, x: cx + R * Math.cos(angle), y: cy + R * Math.sin(angle) }
  })
}

export default function KnowledgeGraph() {
  const { courseId } = useParams()
  const { user } = useAuth()
  const [graph, setGraph] = useState(null)
  const [form, setForm] = useState({ name: '', description: '' })
  const [edgeForm, setEdgeForm] = useState({ source_id: '', target_id: '', edge_type: 'prerequisite' })

  async function load() {
    const { data } = await client.get(`/api/graph/course/${courseId}`)
    setGraph(data)
  }
  useEffect(() => { load() }, [courseId])

  async function addConcept(e) {
    e.preventDefault()
    await client.post('/api/graph/concepts', { course_id: Number(courseId), ...form })
    setForm({ name: '', description: '' })
    load()
  }

  async function addEdge(e) {
    e.preventDefault()
    await client.post('/api/graph/edges', {
      source_id: Number(edgeForm.source_id), target_id: Number(edgeForm.target_id), edge_type: edgeForm.edge_type,
    })
    load()
  }

  if (!graph) return <Loading />
  const positioned = layoutNodes(graph.nodes)
  const byId = Object.fromEntries(positioned.map(n => [n.id, n]))
  const canManage = user.role === 'faculty' || user.role === 'admin'

  return (
    <div>
      <p className="eyebrow mb-1">Module 5 · Knowledge Graph Navigation</p>
      <h1 className="text-3xl font-semibold mb-6">Concept map</h1>

      <div className="card mb-6 overflow-x-auto">
        {graph.nodes.length === 0 ? (
          <p className="text-ink/50 text-sm py-10 text-center">No concepts added yet.</p>
        ) : (
          <svg width="520" height="440" className="mx-auto">
            {graph.edges.map((e, i) => {
              const s = byId[e.source], t = byId[e.target]
              if (!s || !t) return null
              const color = e.type === 'prerequisite' ? '#C98A3E' : e.type === 'leads_to_outcome' ? '#3F6C51' : '#12172B33'
              return <line key={i} x1={s.x} y1={s.y} x2={t.x} y2={t.y} stroke={color} strokeWidth="2" markerEnd="url(#arrow)" />
            })}
            <defs>
              <marker id="arrow" markerWidth="8" markerHeight="8" refX="7" refY="3" orient="auto">
                <path d="M0,0 L0,6 L7,3 z" fill="#12172B55" />
              </marker>
            </defs>
            {positioned.map(n => (
              <g key={n.id}>
                <circle cx={n.x} cy={n.y} r="34" fill="#F6F3EC" stroke="#12172B" strokeWidth="1.5" />
                <text x={n.x} y={n.y} textAnchor="middle" dominantBaseline="middle" fontSize="9" fontWeight="600" fill="#12172B">
                  {n.name.length > 14 ? n.name.slice(0, 12) + '…' : n.name}
                </text>
              </g>
            ))}
          </svg>
        )}
        <div className="flex gap-4 justify-center text-xs mt-2 text-ink/60">
          <span><span className="inline-block w-3 h-0.5 bg-amber align-middle mr-1"></span>Prerequisite</span>
          <span><span className="inline-block w-3 h-0.5 bg-moss align-middle mr-1"></span>Leads to outcome</span>
          <span><span className="inline-block w-3 h-0.5 bg-ink/30 align-middle mr-1"></span>Related</span>
        </div>
      </div>

      {canManage && (
        <div className="grid sm:grid-cols-2 gap-4">
          <form onSubmit={addConcept} className="card space-y-3">
            <h3 className="font-semibold">Add concept</h3>
            <input className="input" placeholder="Concept name" required value={form.name}
              onChange={e => setForm(f => ({ ...f, name: e.target.value }))} />
            <input className="input" placeholder="Description" value={form.description}
              onChange={e => setForm(f => ({ ...f, description: e.target.value }))} />
            <button className="btn-accent">Add concept</button>
          </form>

          <form onSubmit={addEdge} className="card space-y-3">
            <h3 className="font-semibold">Link concepts</h3>
            <select className="input" required value={edgeForm.source_id}
              onChange={e => setEdgeForm(f => ({ ...f, source_id: e.target.value }))}>
              <option value="">From concept…</option>
              {graph.nodes.map(n => <option key={n.id} value={n.id}>{n.name}</option>)}
            </select>
            <select className="input" required value={edgeForm.target_id}
              onChange={e => setEdgeForm(f => ({ ...f, target_id: e.target.value }))}>
              <option value="">To concept…</option>
              {graph.nodes.map(n => <option key={n.id} value={n.id}>{n.name}</option>)}
            </select>
            <select className="input" value={edgeForm.edge_type}
              onChange={e => setEdgeForm(f => ({ ...f, edge_type: e.target.value }))}>
              <option value="prerequisite">Prerequisite</option>
              <option value="related">Related</option>
              <option value="leads_to_outcome">Leads to outcome</option>
            </select>
            <button className="btn-accent">Link</button>
          </form>
        </div>
      )}
    </div>
  )
}
