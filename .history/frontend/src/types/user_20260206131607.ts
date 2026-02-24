// frontend/src/types/users.ts - AJOUTE À LA FIN DU FICHIER EXISTANT

export interface Pole {
  id: number
  code: string
  nom: string
  description?: string
  est_actif: boolean
  equipes_count?: number
  utilisateurs_count?: number
  date_creation?: string
}

export interface Equipe {
  id: number
  nom: string
  description?: string
  pole: number | null
  pole_details?: Pole
  manager: number | null
  manager_details?: {
    id: number
    display_name: string
    username: string
  }
  equipe_parente: number | null
  membres_count?: number
  sous_equipes_count?: number
  niveau_hierarchique?: number
  est_actif: boolean
  date_creation?: string
  // Pour l'arborescence
  sous_equipes?: Equipe[]
}

export interface EquipeMembre {
  id: number
  display_name: string
  pseudo: string | null
  pole_nom?: string
  is_staff: boolean
  date_joined: string
}

export interface UpdatePoleEquipeData {
  user_id: number
  pole_id: number | 0  // 0 = retirer
  equipe_id: number | 0  // 0 = retirer
}

// Étendre l'interface User existante
export interface User {
  id: number
  username: string
  first_name: string
  last_name: string
  pseudo: string | null
  pseudo_format?: string
  email: string
  display_name: string
  full_name: string
  is_staff: boolean
  is_superuser: boolean
  date_joined: string
  last_login: string | null
  keycloak_id?: string
  is_active?: boolean
  // NOUVEAUX CHAMPS
  pole: number | null
  pole_details?: Pole
  equipe: number | null
  equipe_details?: Equipe
  est_chef_equipe?: boolean
  equipes_managerisees?: {
    id: number
    nom: string
    membres_count: number
  }[]
}

export type UpdatePseudoData = 
  | { pseudo: string; pseudo_format?: never }
  | { pseudo?: never; pseudo_format: string }
  | { pseudo: string; pseudo_format: string }