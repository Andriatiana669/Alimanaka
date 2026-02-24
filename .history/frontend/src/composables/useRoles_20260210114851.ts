// frontend/src/composables/useRoles.ts
import { computed } from 'vue'
import type { User } from '@/types/user'

export type UserRole = 'super-admin' | 'admin' | 'user'

export function useRoles() {
  /**
   * Détermine le rôle d'un utilisateur
   */
  const getUserRole = (user: User | null): UserRole => {
    if (!user) return 'user'
    if (user.is_superuser) return 'super-admin'
    if (user.is_staff) return 'admin'
    return 'user'
  }

  /**
   * Retourne le label affichable du rôle
   */
  const getRoleLabel = (user: User | null): string => {
    const role = getUserRole(user)
    const labels: Record<UserRole, string> = {
      'super-admin': 'Super Admin',
      'admin': 'Admin',
      'user': 'Utilisateur'
    }
    return labels[role]
  }

  /**
   * Retourne la classe CSS pour le badge de rôle
   */
  const getRoleClass = (user: User | null): string => {
    const role = getUserRole(user)
    const classes: Record<UserRole, string> = {
      'super-admin': 'role-super-admin',
      'admin': 'role-admin',
      'user': 'role-user'
    }
    return classes[role]
  }

  /**
   * Vérifie si l'utilisateur est Super Admin
   */
  const isSuperAdmin = (user: User | null): boolean => {
    return getUserRole(user) === 'super-admin'
  }

  /**
   * Vérifie si l'utilisateur est Admin (ou Super Admin)
   */
  const isAdmin = (user: User | null): boolean => {
    const role = getUserRole(user)
    return role === 'admin' || role === 'super-admin'
  }

  /**
   * Vérifie si l'utilisateur peut administrer les équipes
   * (même logique que dans Users.vue)
   */
  const canManageEquipes = (user: User | null): boolean => {
    return isAdmin(user)
  }

  /**
   * Vérifie si l'utilisateur peut modifier les infos d'une équipe (nom, pôle, etc.)
   * (réservé au Super Admin)
   */
  const canEditEquipeDetails = (user: User | null): boolean => {
    return isSuperAdmin(user)
  }

  /**
   * Vérifie si l'utilisateur peut gérer les membres d'une équipe
   * (Admin et Super Admin)
   */
  const canManageEquipeMembers = (user: User | null): boolean => {
    return isAdmin(user)
  }

  return {
    getUserRole,
    getRoleLabel,
    getRoleClass,
    isSuperAdmin,
    isAdmin,
    canManageEquipes,
    canEditEquipeDetails,
    canManageEquipeMembers,
    
  }
}