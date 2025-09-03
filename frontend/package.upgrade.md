# Modernizing Frontend

To avoid legacy dependency issues, upgrade to the latest React and Vite:

1. Backup your current `frontend` folder.
2. Create a new Vite React app:
   ```sh
   npm create vite@latest frontend -- --template react-ts
   ```
3. Copy your `src` code and assets into the new Vite project.
4. Update dependencies:
   ```sh
   cd frontend
   npm install
   ```
5. Remove legacy packages (`react-scripts`, old `ajv`, etc.).
6. Test and commit your new frontend.

This will give you a fast, modern, and production-ready React setup.
