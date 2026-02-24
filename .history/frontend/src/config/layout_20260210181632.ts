// config/layout.ts
export const layoutConfig = {
  minWidth: 802,
  minHeight: 873,
  sidebarWidth: 250,
  sidebarWidthCollapsed: 80,
  mobileBreakpoint: 768,
  tabletBreakpoint: 992,
  
  // Valeurs calculées
  get minWidthMain() {
    return this.minWidth - this.sidebarWidth
  },
  get minWidthMainCollapsed() {
    return this.minWidth - this.sidebarWidthCollapsed
  }
}