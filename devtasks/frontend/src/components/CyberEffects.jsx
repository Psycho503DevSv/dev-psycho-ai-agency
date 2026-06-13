import { useState, useEffect, useRef } from 'react'

// Text Scramble effect helper
export function TextScramble({ text, speed = 40, delay = 0 }) {
  const [displayText, setDisplayText] = useState('')
  const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789@#$%&*+='

  useEffect(() => {
    let timer
    let scrambleTimer
    let currentIndex = 0
    const textArray = text.split('')
    const output = Array(textArray.length).fill('')

    const startScramble = () => {
      scrambleTimer = setInterval(() => {
        for (let i = currentIndex; i < textArray.length; i++) {
          if (textArray[i] === ' ') {
            output[i] = ' '
          } else {
            output[i] = chars[Math.floor(Math.random() * chars.length)]
          }
        }
        setDisplayText(output.join(''))
      }, speed)

      timer = setInterval(() => {
        if (currentIndex < textArray.length) {
          output[currentIndex] = textArray[currentIndex]
          currentIndex++
        } else {
          clearInterval(timer)
          clearInterval(scrambleTimer)
          setDisplayText(text)
        }
      }, speed * 1.5)
    }

    const timeout = setTimeout(startScramble, delay)

    return () => {
      clearTimeout(timeout)
      clearInterval(timer)
      clearInterval(scrambleTimer)
    }
  }, [text, speed, delay])

  return <span>{displayText}</span>
}

// 3D Tilt Card wrapper
export function TiltCard({ children, className = '', style = {}, ...props }) {
  const cardRef = useRef(null)
  const [coords, setCoords] = useState({ x: 0, y: 0 })
  const [isHovered, setIsHovered] = useState(false)

  const handleMouseMove = (e) => {
    const card = cardRef.current
    if (!card) return
    const rect = card.getBoundingClientRect()
    const x = e.clientX - rect.left - rect.width / 2
    const y = e.clientY - rect.top - rect.height / 2
    // Limit max tilt to 12 degrees
    const tiltX = -(y / (rect.height / 2)) * 10
    const tiltY = (x / (rect.width / 2)) * 10
    setCoords({ x: tiltX, y: tiltY })
  }

  const handleMouseLeave = () => {
    setIsHovered(false)
    setCoords({ x: 0, y: 0 })
  }

  const tiltStyle = {
    ...style,
    transform: isHovered 
      ? `perspective(1000px) rotateX(${coords.x}deg) rotateY(${coords.y}deg) scale3d(1.02, 1.02, 1.02)` 
      : 'perspective(1000px) rotateX(0deg) rotateY(0deg) scale3d(1, 1, 1)',
    transition: isHovered ? 'none' : 'transform 0.5s cubic-bezier(0.16, 1, 0.3, 1)',
    transformStyle: 'preserve-3d'
  }

  return (
    <div
      ref={cardRef}
      className={className}
      style={tiltStyle}
      onMouseMove={handleMouseMove}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={handleMouseLeave}
      {...props}
    >
      {children}
    </div>
  )
}
