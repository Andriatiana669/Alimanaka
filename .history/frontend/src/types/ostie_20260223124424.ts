// frontend/src/types/ostie.ts

import type { CalendarEvent } from '@/components/common/Calendar.vue'
import type { ReposMedical } from './reposmedicale'

// ============================================
// Types pour les OSTIES
// ============================================

export interface Ostie {
  id: number
  utilisateur: number
  utilisateur_details?: {
    id: number
    display_name: string
    username: string
    email?: string
    pseudo?: string
  }
  date: string
  heure_debut: string
  heure_fin?: string | null
  
  motif: string
  
  // Statut
  statut: 'en_attente' | 'approuve' | 'transforme' | 'annule'
  statut_display?: string
  
  // Lien vers le repos médical généré
  repos_genere?: number | null
  repos_genere_details?: ReposMedical | null
  
  // Métadonnées
  date_creation?: string
  date_modification?: string
  
  // Validation
  valide_par?: number
  valide_par_details?: {
    id: number
    display_name: string
    username: string
  }
  date_validation?: string
  
  // Annulation
  annule_par?: number
  annule_par_details?: {
    id: number
    display_name: string
    username: string
  }
  date_annulation?: string
  commentaire_annulation?: string
}

// ============================================
// Types pour le calendrier
// ============================================

// Version API
export interface OstieCalendarEventFromAPI {
  id: string | number
  title: string
  start: string
  end?: string
  allDay?: boolean
  color?: string
  type: 'ostie'
  user_id?: number
  statut?: string
  heure_debut?: string
  heure_fin?: string | null
  repos_genere_id?: number | null
}

// Version pour le composant Calendar (dates en Date)
export interface OstieCalendarEvent extends Omit<CalendarEvent, 'type'> {
  type: 'ostie'
  heure_debut?: string
  heure_fin?: string | null
  repos_genere_id?: number | null
}

// ============================================
// Types pour la création
// ============================================

export interface CreateOstieData {
  date: string
  heure_debut: string
  motif?: string
}

// ============================================
// Types pour les utilisateurs gérables
// ============================================

export interface GerableUserOstie {
  id: number
  display_name: string
  username: string
  equipe_nom: string | null
}

// ============================================
// Types pour les filtres
// ============================================

export interface OstieParams {
  annee?: number
  statut?: string
}

export interface CalendrierOstieParams {
  annee?: number
  statut?: string
}

// ============================================
// Types pour les réponses API
// ============================================

export interface ValidationOstieResponse {
  success: boolean
  message: string
  statut: string
  heure_fin: string
}

export interface TransformationOstieResponse {
  success: boolean
  message: string
  statut: string
  repos_id: number
  repos_statut: string
}

export interface AnnulationOstieResponse {
  success: boolean
  message: string
  annule_par: string
  date_annulation: string
}

// ============================================
// Types pour les formulaires d'action
// ============================================

export interface ValidationOstieForm {
  heure_fin: string
}

export interface TransformationOstieForm {
  heure_fin_ostie: string
  heure_fin_repos: string
}