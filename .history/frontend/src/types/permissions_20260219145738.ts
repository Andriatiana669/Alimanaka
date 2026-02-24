// frontend/src/types/permissions.ts

import type { CalendarEvent } from '@/components/common/Calendar.vue'
import type { TypeCongeConfig } from './conges'

// ============================================
// Types pour les permissions
// ============================================

export interface Permission {
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
  heure_depart: string
  heure_arrivee_max: string
  heure_arrivee_reelle?: string | null
  motif: string
  
  // Calculs
  minutes_depassement: number
  heures_a_rattraper: number
  heures_restantes: number
  
  // Statut
  statut: 'en_attente' | 'retourne' | 'rattrapage' | 'approuve' | 'transforme' | 'annule'
  statut_display?: string
  
  // Rattrapages (stockés en JSON)
  rattrapages?: RattrapageJSON[]
  
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
// Types pour les rattrapages (JSON)
// ============================================

export interface RattrapageJSON {
  id: number
  date: string
  heure_debut: string
  heure_fin: string
  heures: number
  commentaire?: string
  valide_par?: number
  date_validation?: string
}

// ============================================
// Types pour le calendrier
// ============================================

// Version API
export interface PermissionCalendarEventFromAPI {
  id: string | number
  title: string
  start: string
  end?: string
  allDay?: boolean
  color?: string
  type: 'permission'
  user_id?: number
  statut?: string
  heures_restantes?: number
  peut_retourner?: boolean
  conge_genere_id?: number | null
}

// Version pour le composant Calendar (dates en Date)
export interface PermissionCalendarEvent extends Omit<CalendarEvent, 'type'> {
  type: 'permission'
  heures_restantes?: number
  peut_retourner?: boolean
  conge_genere_id?: number | null
}

// ============================================
// Types pour la création
// ============================================

export interface CreatePermissionData {
  date: string
  heure_depart: string
  motif: string
}

// ============================================
// Types pour les utilisateurs gérables
// ============================================

export interface GerableUserPermission {
  id: number
  display_name: string
  username: string
  equipe_nom: string | null
}

// ============================================
// Types pour les filtres
// ============================================

export interface PermissionsParams {
  annee?: number
  statut?: string
}

export interface CalendrierPermissionsParams {
  annee?: number
  statut?: string
}

// ============================================
// Types pour les réponses API
// ============================================

export interface RetourResponse {
  success: boolean
  message: string
  statut: string
  heures_a_rattraper: number
  minutes_depassement: number
}

export interface RattrapageResponse {
  success: boolean
  message: string
  heures_rattrapees: number
  heures_restantes: number
  statut: string
  rattrapages: RattrapageJSON[]
}

export interface TransformationResponse {
  success: boolean
  message: string
  conge_id: number
  statut: string
}

export interface AnnulationPermissionResponse {
  success: boolean
  message: string
  annule_par: string
  date_annulation: string
}