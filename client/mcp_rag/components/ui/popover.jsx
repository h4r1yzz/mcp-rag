"use client"

import { createContext, useContext, useEffect, useMemo, useRef, useState } from "react"
import { createPortal } from "react-dom"

const PopoverContext = createContext(null)

export function Popover({ open, onOpenChange, children }) {
  const [internalOpen, setInternalOpen] = useState(false)
  const triggerRef = useRef(null)

  const isControlled = typeof open === "boolean"
  const isOpen = isControlled ? open : internalOpen
  const setOpen = onOpenChange || setInternalOpen

  const value = useMemo(() => ({ isOpen, setOpen, triggerRef }), [isOpen])

  return <PopoverContext.Provider value={value}>{children}</PopoverContext.Provider>
}

export function PopoverTrigger({ asChild = false, children }) {
  const ctx = usePopoverCtx()
  const child = asChild && children && typeof children === "object" ? children : null

  const onClick = () => ctx.setOpen(!ctx.isOpen)

  if (child) {
    return (
      <child.type
        {...child.props}
        ref={(node) => {
          if (typeof child.ref === "function") child.ref(node)
          else if (child.ref) child.ref.current = node
          ctx.triggerRef.current = node
        }}
        onClick={(e) => {
          child.props?.onClick?.(e)
          onClick()
        }}
      />
    )
  }

  return (
    <button ref={ctx.triggerRef} onClick={onClick} type="button">
      {children}
    </button>
  )
}

export function PopoverContent({ className = "", children, side = "bottom", align = "center" }) {
  const ctx = usePopoverCtx()
  const contentRef = useRef(null)
  const [mounted, setMounted] = useState(false)
  const [style, setStyle] = useState({ position: "absolute", top: 0, left: 0, minWidth: "auto", zIndex: 50 })

  useEffect(() => setMounted(true), [])

  useEffect(() => {
    if (!ctx.isOpen || !ctx.triggerRef.current) return
    const triggerRect = ctx.triggerRef.current.getBoundingClientRect()
    const spacing = 8
    const contentEl = contentRef.current
    const compute = () => {
      const width = contentEl?.offsetWidth || 0
      const height = contentEl?.offsetHeight || 0
      let top = 0
      let left = 0

      if (side === "top") top = triggerRect.top - height - spacing
      else if (side === "bottom") top = triggerRect.bottom + spacing
      else if (side === "left") top = triggerRect.top
      else if (side === "right") top = triggerRect.top

      if (align === "start") left = triggerRect.left
      else if (align === "end") left = triggerRect.right - width
      else left = triggerRect.left + triggerRect.width / 2 - width / 2

      // Fallback within viewport a bit
      top = Math.max(8, top)
      left = Math.max(8, Math.min(left, window.innerWidth - width - 8))

      setStyle((s) => ({ ...s, top: Math.round(top) + window.scrollY, left: Math.round(left) + window.scrollX }))
    }

    compute()
    const ro = new ResizeObserver(compute)
    ro.observe(document.body)
    window.addEventListener("scroll", compute, true)
    window.addEventListener("resize", compute)
    return () => {
      ro.disconnect()
      window.removeEventListener("scroll", compute, true)
      window.removeEventListener("resize", compute)
    }
  }, [ctx.isOpen, side, align])

  useEffect(() => {
    if (!ctx.isOpen) return
    const onKey = (e) => {
      if (e.key === "Escape") ctx.setOpen(false)
    }
    const onClick = (e) => {
      if (!contentRef.current || !ctx.triggerRef.current) return
      const target = e.target
      if (!contentRef.current.contains(target) && !ctx.triggerRef.current.contains(target)) {
        ctx.setOpen(false)
      }
    }
    document.addEventListener("keydown", onKey)
    document.addEventListener("mousedown", onClick)
    return () => {
      document.removeEventListener("keydown", onKey)
      document.removeEventListener("mousedown", onClick)
    }
  }, [ctx.isOpen])

  if (!mounted || !ctx.isOpen) return null

  const content = (
    <div
      ref={contentRef}
      className={`rounded-md border border-zinc-200 dark:border-zinc-800 bg-white dark:bg-zinc-900 shadow-md ${className}`}
      style={style}
      role="dialog"
    >
      {children}
    </div>
  )

  return createPortal(content, document.body)
}

function usePopoverCtx() {
  const ctx = useContext(PopoverContext)
  if (!ctx) throw new Error("Popover components must be used within <Popover>")
  return ctx
}


