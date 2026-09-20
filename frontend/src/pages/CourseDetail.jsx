import React, { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import client from '../api/client'
import { useAuth } from '../context/AuthContext'
import Loading from '../components/Loading'

export default function CourseDetail() {
  const { courseId } = useParams()
  const { user } = useAuth()
  const [course, setCourse] = useState(null)
  const [materials, setMaterials] = useState(null)
  const [uploadForm, setUploadForm] = useState({ title: '', material_type: 'pdf', file: null })
  const [videoForm, setVideoForm] = useState({ title: '', video_url: '' })
  const [busy, setBusy] = useState(false)
  const [msg, setMsg] = useState('')

  async function load() {
    const [c, m] = await Promise.all([
      client.get(`/api/courses/${courseId}`),
      client.get(`/api/materials/course/${courseId}`),
    ])
    setCourse(c.data)
    setMaterials(m.data)
  }

  useEffect(() => { load() }, [courseId])

  async function handleUpload(e) {
    e.preventDefault()
    if (!uploadForm.file) return
    setBusy(true)
    setMsg('')
    try {
      const fd = new FormData()
      fd.append('course_id', courseId)
      fd.append('title', uploadForm.title)
      fd.append('material_type', uploadForm.material_type)
      fd.append('file', uploadForm.file)
      await client.post('/api/materials/upload', fd, { headers: { 'Content-Type': 'multipart/form-data' } })
      setMsg('Uploaded — processing and indexing in the background.')
      setUploadForm({ title: '', material_type: 'pdf', file: null })
      load()
    } catch (err) {
      setMsg(err?.response?.data?.detail || 'Upload failed')
    } finally {
      setBusy(false)
    }
  }

  async function handleAddVideo(e) {
    e.preventDefault()
    setBusy(true)
    try {
      await client.post('/api/materials/video', { course_id: Number(courseId), ...videoForm })
      setVideoForm({ title: '', video_url: '' })
      load()
    } finally {
      setBusy(false)
    }
  }

  async function logView(materialId) {
    if (user.role === 'student') {
      try { await client.post(`/api/materials/${materialId}/log-view`) } catch {}
    }
  }

  if (!course || !materials) return <Loading />

  const canManage = user.role === 'faculty' || user.role === 'admin'

  return (
    <div>
      <p className="eyebrow mb-1">{course.code}</p>
      <h1 className="text-3xl font-semibold mb-2">{course.title}</h1>
      <p className="text-ink/60 max-w-2xl mb-6">{course.description}</p>

      <div className="flex flex-wrap gap-2 mb-8">
        <Link to={`/courses/${courseId}/graph`} className="btn-ghost text-sm">Knowledge graph</Link>
        <Link to={`/courses/${courseId}/assignments`} className="btn-ghost text-sm">Assignments</Link>
        {user.role === 'student' && <Link to="/assistant" className="btn-ghost text-sm">Ask AI assistant</Link>}
      </div>

      {canManage && (
        <div className="grid sm:grid-cols-2 gap-4 mb-8">
          <form onSubmit={handleUpload} className="card space-y-3">
            <h3 className="font-semibold">Upload material (PDF / PPT)</h3>
            <input className="input" placeholder="Title" required
              value={uploadForm.title} onChange={e => setUploadForm(f => ({ ...f, title: e.target.value }))} />
            <select className="input" value={uploadForm.material_type}
              onChange={e => setUploadForm(f => ({ ...f, material_type: e.target.value }))}>
              <option value="pdf">PDF</option>
              <option value="ppt">PPT</option>
            </select>
            <input className="input" type="file" accept=".pdf,.ppt,.pptx" required
              onChange={e => setUploadForm(f => ({ ...f, file: e.target.files[0] }))} />
            <button className="btn-accent" disabled={busy}>{busy ? 'Uploading…' : 'Upload & index'}</button>
            {msg && <p className="text-sm text-ink/60">{msg}</p>}
          </form>

          <form onSubmit={handleAddVideo} className="card space-y-3">
            <h3 className="font-semibold">Add video resource</h3>
            <input className="input" placeholder="Title" required
              value={videoForm.title} onChange={e => setVideoForm(f => ({ ...f, title: e.target.value }))} />
            <input className="input" placeholder="Video URL" required
              value={videoForm.video_url} onChange={e => setVideoForm(f => ({ ...f, video_url: e.target.value }))} />
            <button className="btn-accent" disabled={busy}>Add video</button>
          </form>
        </div>
      )}

      <h2 className="text-xl font-semibold mb-3">Learning materials</h2>
      {materials.length === 0 ? (
        <p className="text-ink/50">No materials uploaded yet.</p>
      ) : (
        <div className="space-y-2">
          {materials.map(m => (
            <div key={m.id} className="card flex items-center justify-between !py-3">
              <div>
                <p className="font-medium">{m.title}</p>
                <p className="text-xs text-ink/50 uppercase tracking-wide">
                  {m.material_type} · {m.is_indexed ? 'Indexed' : 'Processing…'}
                </p>
              </div>
              {m.material_type !== 'video' && (
                <Link
                  to={`/materials/${m.id}/study`}
                  onClick={() => logView(m.id)}
                  className="btn-ghost text-sm !py-1.5"
                >
                  Study tools
                </Link>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
