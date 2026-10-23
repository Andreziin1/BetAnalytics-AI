import { defineConfig } from 'vite';

// Mesma origem no navegador, inclusive se o Vite mudar de porta.
const proxy = {
  '/api': {
    target: 'http://127.0.0.1:8000',
    changeOrigin: true,
    rewrite: (path) => path.replace(/^\/api(?=\/|$)/, ''),
    timeout: 190000,
    proxyTimeout: 190000,
  },
};

export default defineConfig({
  server: { host: '127.0.0.1', port: 5173, proxy },
  preview: { host: '127.0.0.1', proxy },
});
