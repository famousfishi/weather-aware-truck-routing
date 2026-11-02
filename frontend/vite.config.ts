import react from '@vitejs/plugin-react';
import { defineConfig } from 'vite';

// In development, calls to /api are forwarded to Django on port 8000,
// so the browser sees one origin and no CORS setup is needed.
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: { '/api': 'http://localhost:8000' },
  },
  // Libraries change rarely, so they get their own files that browsers can keep cached between deploys.
  build: {
    rolldownOptions: {
      output: {
        codeSplitting: {
          groups: [
            { name: 'mui', test: /node_modules[\\/](@mui|@emotion)[\\/]/ },
            { name: 'map', test: /node_modules[\\/](leaflet|react-leaflet|@react-leaflet)[\\/]/ },
          ],
        },
      },
    },
  },
});