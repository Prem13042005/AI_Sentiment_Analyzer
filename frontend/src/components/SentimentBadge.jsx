import React from 'react'

const SentimentBadge = ({ sentiment }) => {
  const normalized = sentiment ? sentiment.toLowerCase().trim() : 'neutral'

  let styles = {
    bg: 'bg-gray-100',
    text: 'text-gray-700',
    label: 'Neutral',
  }

  if (normalized === 'positive' || normalized === 'complete') {
    styles = {
      bg: 'bg-[#dcfce7]',
      text: 'text-[#15803d]',
      label: normalized === 'complete' ? 'Complete' : 'Positive',
    }
  } else if (normalized === 'negative') {
    styles = {
      bg: 'bg-[#fee2e2]',
      text: 'text-[#b91c1c]',
      label: 'Negative',
    }
  } else if (normalized === 'neutral') {
    styles = {
      bg: 'bg-[#f1f5f9]',
      text: 'text-[#475569]',
      label: 'Neutral',
    }
  } else if (normalized === 'processing') {
    styles = {
      bg: 'bg-[#fef3c7]',
      text: 'text-[#92400e]',
      label: 'Processing',
    }
  }

  return (
    <span
      className={`inline-flex items-center rounded-full px-2.5 py-1 text-xs font-semibold uppercase tracking-wider ${styles.bg} ${styles.text}`}
    >
      {styles.label}
    </span>
  )
}

export default SentimentBadge
