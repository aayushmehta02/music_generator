import { StrictMode } from 'react' // Importing StrictMode for highlighting potential problems in an application
import { createRoot } from 'react-dom/client' // Importing createRoot from React DOM for concurrent rendering
import './index.css' // Importing global CSS styles
import App from './App.jsx' // Importing the main App component

// Creating the root of the React application and rendering the App inside StrictMode
createRoot(document.getElementById('root')).render(
  <StrictMode>
    <App /> {/* Rendering the App component inside StrictMode for development checks */}
  </StrictMode>,
)