// frontend/env.d.ts
/// <reference types="vite/client" />

// Les types pour Vue sont suffisants, vite gère déjà les SVG
declare module '*.vue' {
  import type { DefineComponent } from 'vue'
  const component: DefineComponent<{}, {}, any>
  export default component
}