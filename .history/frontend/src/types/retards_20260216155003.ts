// Types pour les retards (similaire à conges.ts)

export interface TypeRetardConfig {
  id: number;
  type_retard: 'leger' | 'moyen' | 'important';
  minutes_min: number;
  minutes_max: number | null;
  multiplicateur: string; // Decimal as string
}

export interface Rattrapage {
  id: number;
  retard: number;
  date_rattrapage: string; // YYYY-MM-DD
  heure_debut: string; // HH:MM
  heure_fin: string; // HH:MM
  heures_rattrapees: string; // Decimal as string
  valide_par: number | null;
  valide_par_details?: {
    id: number;
    username: string;
    pseudo?: string;
    first_name: string;
    last_name: string;
  };
  date_validation: string;
  commentaire: string | null;
}

export interface Retard {
  id: number;
  utilisateur: number;
  utilisateur_details?: {
    id: number;
    username: string;
    pseudo?: string;
    first_name: string;
    last_name: string;
    get_display_name: string;
  };
  
  // Dates et heures
  date: string; // YYYY-MM-DD
  heure_debut_prevue: string; // HH:MM
  heure_arrivee_reelle: string; // HH:MM
  
  // Calculs automatiques
  minutes_retard: number;
  heures_a_rattraper: string; // Decimal as string
  heures_restantes: string; // Decimal as string
  
  // Justificatif
  motif_retard: string | null;
  
  // Type calculé
  type_retard: string;
  type_retard_display?: string;
  
  // Statut
  statut: 'en_attente' | 'approuve' | 'annule';
  statut_display?: string;
  
  // Timestamps
  date_creation: string;
  date_modification: string;
  
  // Approbation
  approuve_par: number | null;
  approuve_par_details?: {
    id: number;
    username: string;
    pseudo?: string;
    first_name: string;
    last_name: string;
    get_display_name: string;
  };
  date_approbation: string | null;
  
  // Annulation
  annule_par: number | null;
  annule_par_details?: {
    id: number;
    username: string;
    pseudo?: string;
    first_name: string;
    last_name: string;
    get_display_name: string;
  };
  date_annulation: string | null;
  commentaire_annulation: string | null;
  
  // Relations
  retard_original: number | null;
  rattrapages: Rattrapage[];
  total_rattrape?: string; // Decimal as string
}

export interface RetardCreateData {
  date: string;
  heure_arrivee_reelle: string;
  motif_retard?: string;
}

export interface RattrapageCreateData {
  date_rattrapage: string;
  heure_debut: string;
  heure_fin: string;
  commentaire?: string;
}

export interface RetardFilters {
  statut?: string;
  annee?: number;
}

// Pour le calendrier (même structure que les congés)
export interface RetardCalendarEvent {
  id: string;
  title: string;
  start: string;
  allDay: boolean;
  color: string;
  type: 'retard';
  user_id: number;
  equipe_id: number | null;
  statut: string;
  heures_restantes: string;
}