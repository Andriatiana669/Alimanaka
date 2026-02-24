// frontend/src/composables/useDisplayName.ts
export function useDisplayName() {
  const generatePseudo = (lastName?: string, pseudo?: string | null): string => {
    // Priorité au pseudo personnalisé
    if (pseudo) return pseudo
    
    // Valeur par défaut si lastName est undefined
    const words = (lastName || '').trim().split(/\s+/)
    
    if (words.length >= 2 && words[1]) return words[1]
    if (words.length >= 1 && words[0]) return words[0]
    
    return '-'
  }
  
  return { generatePseudo }
}