import { defineConfig, loadEnv } from 'vite'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'

export default defineConfig(({ mode }) => {
  // Charge les variables d'environnement selon le mode (dev/prod)
  const env = loadEnv(mode, process.cwd(), '')
  
  // Déterminer l'URL du backend en fonction de l'environnement
  const backendUrl = env.VITE_API_BASE_URL || 'http://localhost:4000'
  // Extraire le protocole et l'hôte:port (enlever /api si présent)
  const backendHost = backendUrl.replace('/api', '')
  
  console.log(`🚀 Mode: ${mode}, Backend: ${backendHost}`)
  
  return {
    plugins: [vue()],
    resolve: {
      alias: {
        '@': resolve(__dirname, './src'),
      },
    },
    server: {
      port: env.VITE_PORT ? parseInt(env.VITE_PORT) : 5173,
      host: true, // Équivalent à --host 0.0.0.0
      proxy: {
        '/api': {
          target: backendHost,  // ← Utilise l'URL du backend depuis .env
          changeOrigin: true,
          secure: false,
          configure: (proxy, _options) => {
            proxy.on('error', (err, _req, _res) => {
              console.log('❌ Proxy error:', err);
            });
            proxy.on('proxyReq', (proxyReq, req, _res) => {
              console.log('🔄 Proxy:', req.method, req.url, '→', backendHost);
            });
          },
        },
        '/auth': {
          target: backendHost,  // ← Utilise l'URL du backend depuis .env
          changeOrigin: true,
        },
        '/static': {
          target: backendHost,
          changeOrigin: true,
        },
        '/media': {
          target: backendHost,
          changeOrigin: true,
        },
      },
    },
    build: {
      outDir: '../backend/alimanaka/static',
      emptyOutDir: true,
      assetsDir: 'assets',
      rollupOptions: {
        input: {
          main: resolve(__dirname, 'index.html'),
        },
      },
    },
    // Expose les variables d'environnement au frontend
    define: {
      __APP_ENV__: JSON.stringify(env.VITE_APP_ENV),
    },
  }
})