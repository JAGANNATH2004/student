import React from 'react'

export default function Loading({ label = 'Loading…' }) {
  return (
    <div className="flex items-center gap-3 text-ink/60 py-10 justify-center">
      <span className="h-4 w-4 rounded-full border-2 border-ink/20 border-t-amber animate-spin" />
      <span className="text-sm">{label}</span>
    </div>
  )
}
