// frontend/src/types/auth.ts
import type { User } from '@/types/user'

export interface AuthState {
  user: User | null
  token: string | null
  isAuthenticated: boolean
  loading: boolean
}

export interface LoginCredentials {
  username: string
  password: string
}