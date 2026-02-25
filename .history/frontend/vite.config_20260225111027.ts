import { defineConfig, loadEnv } from 'vite'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'

export default defineConfig(({ mode }) => {
  // Charge les variables d'environnement selon le mode
  const env = loadEnv(mode, process.cwd(), '')

  return {
    plugins: [vue()],

    resolve: {
      alias: {
        '@': resolve(__dirname, './src'),
      },
    },

    /**
     * =====================================================
     * DEV SERVER (UNIQUEMENT EN DEV)
     * =====================================================
     */
    server: {
      port: 4002, // ✅ FRONTEND UNIQUE
      strictPort: true,
      proxy: {
        '/api': {
          target: env.VITE_API_BASE_URL, // http://localhost:4000
          changeOrigin: true,
        },
        '/auth': {
          target: env.VITE_API_BASE_URL,
          changeOrigin: true,
        },
        '/static': {
          target: env.VITE_API_BASE_URL,
          changeOrigin: true,
        },
        '/media': {
          target: env.VITE_API_BASE_URL,
          changeOrigin: true,
        },
      },
    },

    /**
     * =====================================================
     * BUILD (POUR DJANGO)
     * =====================================================
     */
    build: {
      outDir: '../backend/frontend/dist', // cohérent avec settings.py
      emptyOutDir: true,
      assetsDir: 'assets',
      rollupOptions: {
        input: {
          main: resolve(__dirname, 'index.html'),
        },
      },
    },

    /**
     * =====================================================
     * ENV EXPOSÉES AU FRONT
     * =====================================================
     */
    define: {
      __APP_ENV__: JSON.stringify(env.VITE_APP_ENV),
    },
  }
})