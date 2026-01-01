import { useEffect, useRef, useState } from 'react'

export default function KnowledgeGraph({ data }) {
  const canvasRef = useRef(null)
  const [nodes, setNodes] = useState([])

  useEffect(() => {
    if (!data?.nodes?.length) return

    // Initialize node positions
    const initialized = data.nodes.map((node, i) => ({
      ...node,
      x: 200 + Math.cos(i * 2 * Math.PI / data.nodes.length) * 150,
      y: 200 + Math.sin(i * 2 * Math.PI / data.nodes.length) * 150,
      vx: 0,
      vy: 0
    }))
    setNodes(initialized)
  }, [data])

  useEffect(() => {
    if (!nodes.length || !canvasRef.current) return

    const canvas = canvasRef.current
    const ctx = canvas.getContext('2d')

    const draw = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height)

      // Draw links
      ctx.strokeStyle = '#999'
      ctx.lineWidth = 1
      data.links?.forEach(link => {
        const source = nodes.find(n => n.id === link.source)
        const target = nodes.find(n => n.id === link.target)
        if (source && target) {
          ctx.beginPath()
          ctx.moveTo(source.x, source.y)
          ctx.lineTo(target.x, target.y)
          ctx.stroke()
        }
      })

      // Draw nodes
      nodes.forEach(node => {
        ctx.beginPath()
        ctx.arc(node.x, node.y, 12, 0, 2 * Math.PI)
        ctx.fillStyle = node.type === 'skill' ? '#4a90d9' : '#ef4444'
        ctx.fill()
        ctx.strokeStyle = '#fff'
        ctx.lineWidth = 2
        ctx.stroke()

        // Label
        ctx.fillStyle = '#333'
        ctx.font = '12px sans-serif'
        ctx.textAlign = 'center'
        ctx.fillText(node.label || node.id, node.x, node.y + 25)
      })
    }

    draw()
  }, [nodes, data])

  if (!data?.nodes?.length) {
    return <div style={{ padding: '20px', textAlign: 'center', color: '#666' }}>No graph data available</div>
  }

  return (
    <div className="knowledge-graph" style={{ border: '1px solid #ddd', borderRadius: '8px', overflow: 'hidden' }}>
      <canvas ref={canvasRef} width={400} height={400} style={{ display: 'block' }} />
    </div>
  )
}
