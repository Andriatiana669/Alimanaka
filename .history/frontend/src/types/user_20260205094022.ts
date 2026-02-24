// frontend/src/types/user.ts
export interface User {
  id: number
  username: string
  first_name: string
  last_name: string
  pseudo: string | null
  email: string
  display_name: string
  full_name: string
  is_staff: boolean
  is_superuser: boolean
  date_joined: string
  last_login: string | null
  keycloak_id?: string
}

export interface UpdatePseudoData {
  pseudo: string
}