// frontend/src/composables/useDisplayName.ts
export function useDisplayName() {
  const generatePseudo = (lastName: string, pseudo?: string | null): string => {
    // Priorité au pseudo personnalisé
    if (pseudo) return pseudo;

    // Vérifiez que lastName est bien défini et non vide
    const words = lastName?.trim().split(/\s+/) || [];

    // Si words n'est pas vide, retournez le deuxième mot ou le premier mot
    if (words.length >= 2 && words[1] !== undefined) return words[1];
    if (words.length >= 1 && words[0] !== undefined) return words[0];

    // Retour par défaut
    return '-';
  };

  return { generatePseudo };
}
