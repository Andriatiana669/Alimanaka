// frontend/src/types/conges.ts

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
  motif?: string
  statut: 'en_attente' | 'approuve' | 'refuse' | 'annule'
  statut_display?: string
  jours_deduits: number
  date_creation?: string
  date_modification?: string

  valide_par?: number
  valide_par_details?: {
    id: number
    display_name: string
    username: string
  }
  date_validation?: string
  
  refuse_par?: number
  refuse_par_details?: {
    id: number
    display_name: string
    username: string
  }
  date_refus?: string
  commentaire_refus?: string
}

// Pour le calendrier - dates en string depuis l'API
export interface CalendarEventFromAPI {
  id: string | number 
  title: string
  start: string
  end?: string
  allDay?: boolean
  color?: string
  type?: 'conge' | 'ferie' | 'exceptionnel' | 'conge_annuel' | 'weekend'
  isBlocked?: boolean
  statut?: 'en_attente' | 'approuve' | 'refuse' | 'annule'
  user_id?: number
}

// Pour le composant Calendar - dates en Date
export interface CalendarEvent {
  id: string | number 
  title: string
  start: Date
  end?: Date
  allDay?: boolean
  color?: string
  type?: 'conge' | 'ferie' | 'exceptionnel' | 'conge_annuel' | 'weekend'  // AJOUTÉ
  isBlocked?: boolean  // AJOUTÉ
}

export interface CreateCongeData {
  type_conge: 'matin' | 'midi' | 'journee'
  date_debut: string
  date_fin: string
  motif?: string
}

export interface UserSoldeConge {
  solde_conge_recue_par_mois: number
  solde_conge_actuelle: number
  solde_conge_consomme: number
  motif_conge?: string | null
}


// Pour les privilège (Ninho)

export interface GerableUser {
  id: number
  display_name: string
  username: string
  equipe_nom: string | null
  solde_conge_actuelle: string
}

export interface CalendrierParams {
  annee?: number
  pole?: number
  equipe?: number
}

