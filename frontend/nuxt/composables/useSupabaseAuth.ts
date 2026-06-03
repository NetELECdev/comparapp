/**
 * composables/useSupabaseAuth.ts
 * Autenticación OAuth con Supabase directamente desde el frontend.
 * Requiere: npm install @supabase/supabase-js (en frontend/nuxt/)
 */

const SUPABASE_URL = 'https://fbsugjqjbltvvyywfsal.supabase.co'
const SUPABASE_ANON_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImZic3VnanFqYmx0dnZ5eXdmc2FsIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDQ3NTc5MDAsImV4cCI6MjA2MDMzMzkwMH0.WGPCnfur8MVDzW22WGF3n2K0Ai1xnVh0t0sK0MbYwoc'

let _client: any = null

async function getClient() {
  if (!_client && import.meta.client) {
    const { createClient } = await import('@supabase/supabase-js')
    _client = createClient(SUPABASE_URL, SUPABASE_ANON_KEY)
  }
  return _client
}

export function useSupabaseAuth() {
  const REDIRECT_URL = import.meta.client
    ? `${window.location.origin}/auth/callback`
    : 'http://localhost:3000/auth/callback'

  async function loginWithGoogle() {
    const supabase = await getClient()
    if (!supabase) throw new Error('Solo disponible en el navegador')
    const { data, error } = await supabase.auth.signInWithOAuth({
      provider: 'google',
      options: { redirectTo: REDIRECT_URL }
    })
    if (error) throw error
    return data
  }

  async function getSession() {
    const supabase = await getClient()
    if (!supabase) return null
    const { data } = await supabase.auth.getSession()
    return data.session
  }

  async function getUser() {
    const supabase = await getClient()
    if (!supabase) return null
    const { data } = await supabase.auth.getUser()
    return data.user
  }

  return { loginWithGoogle, getSession, getUser }
}
