// frontend/src/types/retards.ts

import type { CalendarEvent } from '@/components/common/Calendar.vue'

// ============================================
// Types pour la configuration des retards
// ============================================

export interface TypeRetardConfig {
  id: number
  type_retard: 'leger' | 'moyen' | 'Autres'
  // NOUVEAU: heure de début prévue (configurable dans l'admin)
  heure_debut_prevue: string  // Format: "HH:MM"
  minutes_min: number
  minutes_max: number | null
  multiplicateur: number
  couleur: string
  est_actif: boolean
  ordre: number
  // Pour l'affichage dans le frontend
  type_retard_display?: string
  heure_debut_prevue_formatted?: string
}

// ============================================
// Types pour les retards
// ============================================

export interface Retard {
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
  type_retard_config?: number
  type_retard_config_details?: TypeRetardConfig
  heure_debut_prevue: string
  heure_arrivee_reelle: string
  minutes_retard: number
  heures_a_rattraper: number
  heures_restantes: number
  type_retard: 'Matin' | 'Midi' | 'Autres'
  type_retard_display?: string
  motif_retard?: string | null
  statut: 'en_attente' | 'en_cours' | 'approuve' | 'annule' | 'remplace'
  statut_display?: string
  
  date_creation?: string
  date_modification?: string
  
  approuve_par?: number
  approuve_par_details?: {
    id: number
    display_name: string
    username: string
  }
  date_approbation?: string
  
  annule_par?: number
  annule_par_details?: {
    id: number
    display_name: string
    username: string
  }
  date_annulation?: string
  commentaire_annulation?: string
  
  rattrapages?: Rattrapage[]
  retard_original?: number
}

// ============================================
// Types pour les rattrapages
// ============================================

export interface Rattrapage {
  id: number
  retard: number
  date_rattrapage: string
  heure_debut: string
  heure_fin: string
  heures_rattrapees: number
  valide_par?: number
  valide_par_details?: {
    id: number
    display_name: string
    username: string
  }
  date_validation?: string
  commentaire?: string | null
}

// ============================================
// Types pour le calendrier (COMPATIBLE AVEC Calendar.vue)
// ============================================

// Version étendue de CalendarEvent qui accepte 'retard'
export interface RetardCalendarEvent extends Omit<CalendarEvent, 'type'> {
  type: 'retard'  // On étend avec notre propre type
  minutes_retard?: number
  heures_restantes?: number
}

// Version API
export interface RetardCalendarEventFromAPI {
  id: string | number
  title: string
  start: string
  end?: string
  allDay?: boolean
  color?: string
  type: 'retard'
  user_id?: number
  statut?: string
  minutes_retard?: number
  heures_restantes?: number
}

// ============================================
// Types pour la création
// ============================================

export interface CreateRetardData {
  date: string
  heure_arrivee_reelle: string
  motif_retard?: string | null
  type_retard_config_id: number  // ← Important: ajouté
}

export interface CreateRattrapageData {
  date_rattrapage: string
  heure_debut: string
  heure_fin: string
  commentaire?: string | null
}

// ============================================
// Types pour les utilisateurs gérables
// ============================================

export interface GerableUserRetard {
  id: number
  display_name: string
  username: string
  equipe_nom: string | null
}

// ============================================
// Types pour les filtres
// ============================================

export interface RetardsParams {
  annee?: number
  statut?: string
}

export interface CalendrierRetardsParams {
  annee?: number
  statut?: string
}

// ============================================
// Types pour les réponses API
// ============================================

export interface RattrapageResponse {
  success: boolean
  message: string
  rattrapage: Rattrapage
  heures_restantes: string
}

export interface AnnulationRetardResponse {
  success: boolean
  message: string
  annule_par: string
  date_annulation: string
}