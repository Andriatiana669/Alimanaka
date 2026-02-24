// frontend/src/types/reposmedicale.ts

import type { CalendarEvent } from '@/components/common/Calendar.vue'
import type { TypeCongeConfig } from './conges'

// ============================================
// Types pour les repos médicaux
// ============================================

export interface ReposMedical {
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
  heure_fin: string
  duree_heures: number
  
  motif: string
  avertissement: string
  
  // Statut
  statut: 'en_attente' | 'approuve' | 'transforme' | 'annule'
  statut_display?: string
  
  // Lien vers le congé généré
  conge_genere?: number | null
  conge_genere_details?: {
    id: number
    type_conge: string
    statut: string
  } | null
  
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
export interface ReposMedicalCalendarEventFromAPI {
  id: string | number
  title: string
  start: string
  end?: string
  allDay?: boolean
  color?: string
  type: 'repos_medical'
  user_id?: number
  statut?: string
  duree_heures?: number
  conge_genere_id?: number | null
}

// Version pour le composant Calendar (dates en Date)
export interface ReposMedicalCalendarEvent extends Omit<CalendarEvent, 'type'> {
  type: 'repos_medical'
  duree_heures?: number
  conge_genere_id?: number | null
}

// ============================================
// Types pour la création
// ============================================

export interface CreateReposMedicalData {
  date: string
  heure_debut: string
  heure_fin: string
  motif?: string
  avertissement?: string
}

// ============================================
// Types pour les utilisateurs gérables
// ============================================

export interface GerableUserReposMedical {
  id: number
  display_name: string
  username: string
  equipe_nom: string | null
}

// ============================================
// Types pour les filtres
// ============================================

export interface ReposMedicalParams {
  annee?: number
  statut?: string
}

export interface CalendrierReposMedicalParams {
  annee?: number
  statut?: string
}

// ============================================
// Types pour les réponses API
// ============================================

export interface ValidationResponse {
  success: boolean
  message: string
  statut: string
}

export interface TransformationResponse {
  success: boolean
  message: string
  conge_id: number
  statut: string
}

export interface AnnulationReposMedicalResponse {
  success: boolean
  message: string
  annule_par: string
  date_annulation: string
}