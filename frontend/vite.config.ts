import { defineConfig } from 'vite';

export default defineConfig(async () => {
  // Dynamically import ESM-only plugin to avoid `require` loading errors on some environments
  const reactPlugin = (await import('@vitejs/plugin-react')).default;

  return {
    plugins: [reactPlugin()],
    build: {
      outDir: 'build',
      sourcemap: false,
    },
    server: {
      port: 3000,
      host: true,
    },
  };
});
