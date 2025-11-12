export type AskResponse = {
  response: string
  sources?: string[]
}

const API_BASE = process.env.NEXT_PUBLIC_API_BASE?.replace(/\/$/, "") || "http://localhost:8000"

async function handleJson<T>(res: Response): Promise<T> {
  const text = await res.text()
  let data: any
  try {
    data = text ? JSON.parse(text) : {}
  } catch {
    throw new Error(`Invalid JSON from API: ${text?.slice(0, 200)}`)
  }
  if (!res.ok) {
    const message = (data && (data.error || data.detail)) || res.statusText
    throw new Error(typeof message === "string" ? message : JSON.stringify(message))
  }
  return data as T
}

export async function askQuestion(question: string): Promise<AskResponse> {
  const fd = new FormData()
  fd.append("question", question)
  const res = await fetch(`${API_BASE}/ask/`, { method: "POST", body: fd })
  return handleJson<AskResponse>(res)
}

export async function streamGroq(
  question: string,
  onToken: (chunk: string) => void,
  threadId?: string,
): Promise<void> {
  const fd = new FormData()
  fd.append("question", question)
  if (threadId) {
    fd.append("thread_id", threadId)
  }
  const res = await fetch(`${API_BASE}/groq_stream/`, { method: "POST", body: fd })
  if (!res.ok) {
    const text = await res.text()
    throw new Error(text || res.statusText)
  }
  const reader = res.body?.getReader()
  if (!reader) return
  const decoder = new TextDecoder()
  while (true) {
    const { done, value } = await reader.read()
    if (done) break
    const chunk = decoder.decode(value)
    if (chunk) onToken(chunk)
  }
}

