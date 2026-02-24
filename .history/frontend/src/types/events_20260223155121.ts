// frontend/src/types/events.ts

import type { CalendarEvent } from '@/components/common/Calendar.vue'

// ============================================
// Types pour les événements
// ============================================

export interface Event {
  id: number
  title: string
  description?: string
  event_type: 'conge' | 'retard' | 'permission' | 'repos_medical' | 'ostie' | 'ferie' | 'exceptionnel' | 'weekend' | 'system'
  
  // Dates
  start_date: string
  end_date?: string | null
  start_time?: string | null
  end_time?: string | null
  all_day: boolean
  
  // Apparence
  color?: string
  icon?: string
  
  // Comportement
  is_blocked: boolean
  is_system: boolean
  
  // Utilisateur concerné
  user?: number
  user_details?: {
    id: number
    display_name: string
    username: string
  }
  statut?: string
  
  // Métadonnées
  created_at?: string
  updated_at?: string
}

// ============================================
// Types pour le calendrier
// ============================================

export interface EventCalendarEventFromAPI {
  id: string
  title: string
  start: string
  end?: string
  allDay?: boolean
  color?: string
  type: string
  user_id?: number
  user_display_name?: string
  statut?: string
  isBlocked?: boolean
  isSystem?: boolean
  description?: string
  start_time?: string
  end_time?: string
}

export interface EventCalendarEvent extends Omit<CalendarEvent, 'type'> {
  type: string
  user_id?: number
  user_display_name?: string
  statut?: string
  isBlocked?: boolean
  isSystem?: boolean
  originalEvent?: EventCalendarEventFromAPI
}

// ============================================
// Types pour les filtres
// ============================================

export interface EventParams {
  annee?: number
  mois?: number
  type?: string
  statut?: string
  skip_cache?: boolean
}

export interface EventType {
  value: string
  label: string
  color: string
}

export interface EventUser {
  id: number
  display_name: string
  username: string
  equipe_nom: string | null
}

// ============================================
// Types pour les statistiques
// ============================================

export interface EventStats {
  total: number
  byType: Record<string, number>
  byStatus: Record<string, number>
  upcoming: number
}