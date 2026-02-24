// frontend/env.d.ts
/// <reference types="vite/client" />

declare module '*.vue' {
  import type { DefineComponent } from 'vue'
  const component: DefineComponent<{}, {}, any>
  export default component
}

// Pour les imports de fichiers SVG
declare module '*.svg' {
  const content: string
  export default content
}