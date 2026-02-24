// frontend/src/types/conges.ts

// ============================================
// Types de base (correspondance avec Django)
// ============================================

export interface TypeCongeConfig {
  id: number
  type_conge: 'matin' | 'midi' | 'journee'
  heure_debut: string
  heure_fin: string
  deduction_jours: number
  vendredi_deduction?: number | null
  jeudi_deduction?: number | null
}

export interface JourFerie {
  id: number
  nom: string
  mois: number
  jour: number
  est_actif: boolean
}

export interface JourExceptionnel {
  id: number
  type_jour: 'exceptionnel' | 'non_exceptionnel'
  date: string
  annee: number
  description?: string
}

export interface CongeAnnuel {
  id: number
  nom: string
  date_debut: string
  date_fin: string
  annee: number
  est_actif: boolean
}

// ============================================
// NOUVEAU : Types pour les droits (congés exceptionnels)
// ============================================

export interface Droit {
  id: number
  nom: string
  description?: string | null
  est_actif: boolean
  ordre: number
}

// ============================================
// Types pour les congés (avec toutes les options)
// ============================================

export interface Conge {
  id: number
  utilisateur: number
  utilisateur_details?: {
    id: number
    display_name: string
    username: string
    email?: string
    pseudo?: string
  }
  type_conge: 'matin' | 'midi' | 'journee'
  type_conge_display?: string
  date_debut: string
  date_fin: string
  motif?: string | null
  statut: 'en_attente' | 'approuve' | 'refuse' | 'annule' | 'remplace'
  statut_display?: string
  jours_deduits: number
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
  
  // Refus
  refuse_par?: number
  refuse_par_details?: {
    id: number
    display_name: string
    username: string
  }
  date_refus?: string
  commentaire_refus?: string
  
  // Validation partielle
  jours_valides?: string[]
  
  // Fractionnement
  conge_original?: number
  conges_fractionnes?: Conge[]
  
  // ============================================
  // NOUVEAU : Champs pour les droits
  // ============================================
  est_droit?: boolean
  droit?: number | null
  droit_details?: Droit | null
}

// ============================================
// Types pour le calendrier
// ============================================

// Depuis l'API (dates en string)
export interface CalendarEventFromAPI {
  id: string | number 
  title: string
  start: string
  end?: string
  allDay?: boolean
  color?: string
  type?: 'conge' | 'ferie' | 'exceptionnel' | 'conge_annuel' | 'weekend'
  isBlocked?: boolean
  statut?: 'en_attente' | 'approuve' | 'refuse' | 'annule' | 'remplace'
  user_id?: number
  // NOUVEAU : Indicateur de droit dans le calendrier
  isDroit?: boolean
  droit_nom?: string
}

// Pour le composant Calendar (dates en Date)
export interface CalendarEvent {
  id: string | number 
  title: string
  start: Date
  end?: Date
  allDay?: boolean
  color?: string
  type?: 'conge' | 'ferie' | 'exceptionnel' | 'conge_annuel' | 'weekend'
  isBlocked?: boolean
  statut?: 'en_attente' | 'approuve' | 'refuse' | 'annule' | 'remplace'
  user_id?: number
  // NOUVEAU
  isDroit?: boolean
  droit_nom?: string
}

// ============================================
// Types pour la création de congés
// ============================================

export interface CreateCongeData {
  type_conge: 'matin' | 'midi' | 'journee'
  date_debut: string
  date_fin: string
  motif?: string | null
  // NOUVEAU : Champs pour les droits
  est_droit?: boolean
  droit?: number | null
}

// ============================================
// Types pour les utilisateurs gérables (managers)
// ============================================

export interface GerableUser {
  id: number
  display_name: string
  username: string
  equipe_nom: string | null
  solde_conge_actuelle: string  // Décimal en string de l'API
}

// ============================================
// Types pour le solde de congés
// ============================================

export interface UserSoldeConge {
  solde_conge_recue_par_mois: number
  solde_conge_actuelle: number
  solde_conge_consomme: number
  motif_conge?: string | null
  // NOUVEAU : Statistiques des droits utilisés
  droits_utilises?: number
  droits_disponibles?: number
}

// ============================================
// Types pour les filtres du calendrier
// ============================================

export interface CalendrierParams {
  annee?: number
  pole?: number
  equipe?: number
}

// ============================================
// Types pour les réponses API (actions spéciales)
// ============================================

export interface ValidationPartielleResponse {
  success: boolean
  message: string
  nouveaux_conges: number[]
  ancien_conge_annule: number
}

export interface AnnulationPartielleResponse {
  success: boolean
  message: string
  remboursement: string
  nouveaux_conges: number[]
  ancien_conge_annule: number
}

export interface ValidationResponse {
  success: boolean
  message: string
  valide_par: string
  date_validation: string
}

export interface RefusResponse {
  success: boolean
  message: string
  refuse_par: string
  date_refus: string
  commentaire_refus: string
}