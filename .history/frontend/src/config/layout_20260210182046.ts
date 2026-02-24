// src/config/layout.ts
export interface LayoutConfig {
  minWidth: number
  minHeight: number
  sidebarWidth: number
  sidebarWidthCollapsed: number
  mobileBreakpoint: number
  tabletBreakpoint: number
}

export const layoutConfig: LayoutConfig = {
  minWidth: 1023,
  minHeight: 890,
  sidebarWidth: 250,
  sidebarWidthCollapsed: 80,
  mobileBreakpoint: 768,
  tabletBreakpoint: 992
}

// Fonction pour obtenir les valeurs calculées
export function getCalculatedValues(config: LayoutConfig) {
  return {
    minWidthMain: config.minWidth - config.sidebarWidth,
    minWidthMainCollapsed: config.minWidth - config.sidebarWidthCollapsed
  }
}

// Fonction pour mettre à jour la configuration
export function updateLayoutConfig(updates: Partial<LayoutConfig>) {
  Object.assign(layoutConfig, updates)
}