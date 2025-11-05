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

export async function uploadPdfs(files: File[] | FileList): Promise<{ messages: string }> {
  const fd = new FormData()
  const arr = Array.from(files as any)
  if (arr.length === 0) throw new Error("No files selected")
  for (const f of arr) fd.append("files", f)
  const res = await fetch(`${API_BASE}/upload_pdfs/`, { method: "POST", body: fd })
  return handleJson<{ messages: string }>(res)
}


