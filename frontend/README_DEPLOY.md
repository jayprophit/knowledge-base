# Knowledge Base Assistant Web Deployment

This project is a cross-platform AI assistant web app built with React. It supports chat, code generation, and multimodal features.

## Deploying to Netlify

1. Ensure dependencies are installed:
   ```sh
   npm install
   ```
2. Build the app:
   ```sh
   npm run build
   ```
3. Deploy to Netlify (or Vercel):
   - Use the `build` folder as the publish directory.
   - Use the default build command: `npm run build`
   - The `netlify.toml` sets up backend API proxying for local dev.

## Local Development

- Start backend (FastAPI):
  ```sh
  uvicorn backend.src.main:app --reload
  ```
- Start frontend:
  ```sh
  npm start
  ```

## Features
- AI chat with knowledge base search
- Code generation via LLM
- Multimodal analysis (image/audio)
- Responsive, modern UI

---
For mobile and desktop packaging, see the project root and docs for React Native/Electron/Tauri instructions.
