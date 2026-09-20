import React from 'react'

export default function ConfidenceBadge({ score }) {
  const pct = Math.round((score ?? 0) * 100)
  const tone = pct >= 70 ? 'bg-moss/15 text-moss' : pct >= 40 ? 'bg-amber/20 text-amber' : 'bg-red-100 text-red-700'
  return (
    <span className={`inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-[11px] font-medium ${tone}`}>
      Confidence {pct}%
    </span>
  )
}
