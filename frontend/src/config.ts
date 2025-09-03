// config.ts
// Central config for frontend environment variables
// Update BACKEND_URL for production or development

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8000';

export default {
  BACKEND_URL,
};
