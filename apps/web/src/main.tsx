import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.tsx'
import { AuthProvider } from './context/AuthContext.tsx'
import { readPublicConfig } from './lib/config.ts'

const configuration = readPublicConfig()
createRoot(document.getElementById('root')!).render(
  <StrictMode>
    {configuration.config
      ? <AuthProvider><App /></AuthProvider>
      : <main style={{maxWidth:640,margin:"80px auto",padding:24}} role="alert">
          <h1>Application configuration required</h1>
          <p>Property Intelligence cannot start safely because required public configuration is missing.</p>
          <ul>{configuration.errors.map(error=><li key={error}>{error}</li>)}</ul>
          <p>Configure the Vite public environment variables and restart the frontend.</p>
        </main>}
  </StrictMode>,
)
