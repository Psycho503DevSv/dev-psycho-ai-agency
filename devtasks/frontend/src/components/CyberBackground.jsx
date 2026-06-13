import { useEffect, useRef } from 'react'

export default function CyberBackground() {
  const canvasRef = useRef(null)
  const mouseRef = useRef({ x: 0, y: 0, targetX: 0, targetY: 0 })

  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return
    const ctx = canvas.getContext('2d')
    let animationFrameId
    
    const resizeCanvas = () => {
      canvas.width = window.innerWidth
      canvas.height = window.innerHeight
    }
    resizeCanvas()
    window.addEventListener('resize', resizeCanvas)

    const handleMouseMove = (e) => {
      mouseRef.current.targetX = e.clientX
      mouseRef.current.targetY = e.clientY
    }
    window.addEventListener('mousemove', handleMouseMove)

    // Setup neural network nodes
    const particleCount = Math.min(60, Math.floor((window.innerWidth * window.innerHeight) / 20000))
    const particles = []
    for (let i = 0; i < particleCount; i++) {
      particles.push({
        x: Math.random() * canvas.width,
        y: Math.random() * canvas.height,
        vx: (Math.random() - 0.5) * 0.6,
        vy: (Math.random() - 0.5) * 0.6,
        radius: Math.random() * 2 + 1,
        color: Math.random() > 0.5 ? 'rgba(0, 243, 255, 0.4)' : 'rgba(112, 0, 255, 0.3)'
      })
    }

    // Grid properties
    let gridOffset = 0
    let laserY = 0
    let laserSpeed = 1.5

    const draw = () => {
      // Clear with dark graphene fade
      ctx.fillStyle = 'rgba(5, 5, 8, 0.15)'
      ctx.fillRect(0, 0, canvas.width, canvas.height)

      // Smooth mouse interpolation
      const mouse = mouseRef.current
      mouse.x += (mouse.targetX - mouse.x) * 0.08
      mouse.y += (mouse.targetY - mouse.y) * 0.08

      // Draw Volumetric Aurora Radial Glow around mouse & center
      const radialGlow = ctx.createRadialGradient(
        mouse.x, mouse.y, 10,
        mouse.x, mouse.y, Math.max(canvas.width, canvas.height) * 0.35
      )
      radialGlow.addColorStop(0, 'rgba(0, 243, 255, 0.06)')
      radialGlow.addColorStop(0.5, 'rgba(112, 0, 255, 0.03)')
      radialGlow.addColorStop(1, 'rgba(0,0,0,0)')
      ctx.fillStyle = radialGlow
      ctx.fillRect(0, 0, canvas.width, canvas.height)

      // Draw Cyberpunk Grid lines with 3D-ish perspective distortion
      ctx.strokeStyle = 'rgba(0, 243, 255, 0.03)'
      ctx.lineWidth = 1
      const gridSize = 60
      gridOffset = (gridOffset + 0.2) % gridSize

      // Vertical lines
      for (let x = -gridSize; x < canvas.width + gridSize; x += gridSize) {
        ctx.beginPath()
        ctx.moveTo(x + (mouse.x - canvas.width / 2) * 0.02, 0)
        ctx.lineTo(x + (mouse.x - canvas.width / 2) * 0.05, canvas.height)
        ctx.stroke()
      }

      // Horizontal lines
      for (let y = -gridSize; y < canvas.height + gridSize; y += gridSize) {
        ctx.beginPath()
        ctx.moveTo(0, y + (mouse.y - canvas.height / 2) * 0.02 + gridOffset)
        ctx.lineTo(canvas.width, y + (mouse.y - canvas.height / 2) * 0.02 + gridOffset)
        ctx.stroke()
      }

      // Draw Tactical Neural Connections (Lines and Nodes)
      particles.forEach((p, idx) => {
        // Move particle
        p.x += p.vx
        p.y += p.vy

        // Repel slightly from mouse
        const dx = p.x - mouse.x
        const dy = p.y - mouse.y
        const dist = Math.hypot(dx, dy)
        if (dist < 150) {
          const force = (150 - dist) / 150
          p.x += (dx / dist) * force * 1.5
          p.y += (dy / dist) * force * 1.5
        }

        // Boundary wrap
        if (p.x < 0) p.x = canvas.width
        if (p.x > canvas.width) p.x = 0
        if (p.y < 0) p.y = canvas.height
        if (p.y > canvas.height) p.y = 0

        // Draw connections
        for (let j = idx + 1; j < particles.length; j++) {
          const p2 = particles[j]
          const p2dist = Math.hypot(p.x - p2.x, p.y - p2.y)
          if (p2dist < 120) {
            const alpha = (120 - p2dist) / 120 * 0.15
            ctx.strokeStyle = `rgba(0, 243, 255, ${alpha})`
            ctx.beginPath()
            ctx.moveTo(p.x, p.y)
            ctx.lineTo(p2.x, p2.y)
            ctx.stroke()
          }
        }

        // Draw particle
        ctx.fillStyle = p.color
        ctx.beginPath()
        ctx.arc(p.x, p.y, p.radius, 0, Math.PI * 2)
        ctx.fill()
      })

      // Horizontal tactical laser scanner sweep
      laserY += laserSpeed
      if (laserY > canvas.height || laserY < 0) {
        laserSpeed = -laserSpeed
      }
      const laserGlow = ctx.createLinearGradient(0, laserY - 4, 0, laserY + 4)
      laserGlow.addColorStop(0, 'rgba(0, 243, 255, 0)')
      laserGlow.addColorStop(0.5, 'rgba(0, 243, 255, 0.12)')
      laserGlow.addColorStop(1, 'rgba(0, 243, 255, 0)')
      ctx.fillStyle = laserGlow
      ctx.fillRect(0, laserY - 4, canvas.width, 8)

      // Tactical tech lines / brackets overlay (Blade Runner style diagnostics)
      ctx.strokeStyle = 'rgba(0, 243, 255, 0.08)'
      ctx.lineWidth = 2
      // Top-Left corner bracket
      ctx.beginPath(); ctx.moveTo(20, 40); ctx.lineTo(20, 20); ctx.lineTo(40, 20); ctx.stroke()
      // Top-Right corner bracket
      ctx.beginPath(); ctx.moveTo(canvas.width - 20, 40); ctx.lineTo(canvas.width - 20, 20); ctx.lineTo(canvas.width - 40, 20); ctx.stroke()
      // Bottom-Left
      ctx.beginPath(); ctx.moveTo(20, canvas.height - 40); ctx.lineTo(20, canvas.height - 20); ctx.lineTo(40, canvas.height - 20); ctx.stroke()
      // Bottom-Right
      ctx.beginPath(); ctx.moveTo(canvas.width - 20, canvas.height - 40); ctx.lineTo(canvas.width - 20, canvas.height - 20); ctx.lineTo(canvas.width - 40, canvas.height - 20); ctx.stroke()

      // Diagnostic text simulation
      ctx.fillStyle = 'rgba(0, 243, 255, 0.2)'
      ctx.font = '9px "Share Tech Mono", monospace'
      ctx.fillText(`SYS.LOC: 2085.CLASSIFIED // CORE_PULSE: ACTIVE`, 30, 32)
      ctx.fillText(`MEM_LOAD: ${(Math.sin(Date.now() / 1000) * 5 + 82).toFixed(2)}% // SEC_LVL: 5`, canvas.width - 260, 32)

      animationFrameId = requestAnimationFrame(draw)
    }
    
    draw()

    return () => {
      cancelAnimationFrame(animationFrameId)
      window.removeEventListener('resize', resizeCanvas)
      window.removeEventListener('mousemove', handleMouseMove)
    }
  }, [])

  return (
    <canvas
      ref={canvasRef}
      style={{
        position: 'fixed',
        top: 0,
        left: 0,
        width: '100vw',
        height: '100vh',
        zIndex: -1,
        pointerEvents: 'none',
        display: 'block'
      }}
    />
  )
}
