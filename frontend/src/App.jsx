import axios from 'axios'; // Importing axios for HTTP requests
import { useState } from 'react'; // Importing useState hook from React
import './App.css'; // Importing custom CSS styles

function App() {
  // State to track selected mood
  const [mood, setMood] = useState('happy');
  // State to store generated MIDI file URL
  const [midiUrl, setMidiUrl] = useState(null);
  // State to indicate loading status
  const [isGenerating, setIsGenerating] = useState(false);
  // State to handle error messages
  const [error, setError] = useState(null);

  // Function to generate music based on mood
  const generateMusic = async () => {
    try {
      setIsGenerating(true); // Start loading
      setError(null); // Reset error
      // Sending POST request to backend with selected mood
      const response = await axios.post('http://localhost:8000/generate', {
        mood: mood
      });
      
      // Construct full MIDI URL from response
      const fullUrl = `http://localhost:8000${response.data.midi_path}`;
      setMidiUrl(fullUrl); // Update state with MIDI file URL
    } catch (error) {
      console.error("Generation failed:", error); // Log error to console
      setError("Failed to generate music. Please try again."); // Set error message
    } finally {
      setIsGenerating(false); // Stop loading
    }
  };

  // Function to return corresponding emoji for selected mood
  const getMoodEmoji = (currentMood) => {
    const emojis = {
      happy: "😊",
      sad: "😢",
      angry: "😠",
      calm: "😌"
    };
    return emojis[currentMood] || "🎵"; // Default to music note if mood not found
  };

  return (
    <div className="app">
      {/* Animated music waves background */}
      <div className="music-waves">
        <div className="wave"></div>
        <div className="wave"></div>
        <div className="wave"></div>
      </div>

      <div className="content">
        {/* Title with mood emoji */}
        <h1 className="title">
          <span className="emoji-bounce">{getMoodEmoji(mood)}</span>
          Mood Music Generator
        </h1>

        {/* Mood selection dropdown */}
        <div className="mood-selector">
          <label htmlFor="mood-select">Choose your mood:</label>
          <select 
            id="mood-select"
            value={mood} 
            onChange={(e) => setMood(e.target.value)}
            className="mood-select"
          >
            <option value="happy">😊 Happy</option>
            <option value="sad">😢 Sad</option>
            <option value="angry">😠 Angry</option>
            <option value="calm">😌 Calm</option>
          </select>
        </div>
        
        {/* Button to trigger music generation */}
        <button 
          onClick={generateMusic}
          disabled={isGenerating}
          className={`generate-button ${isGenerating ? 'generating' : ''}`}
        >
          <span className="button-text">
            {isGenerating ? 'Generating...' : 'Generate Music'}
          </span>
          <span className="button-icon">🎵</span>
        </button>

        {/* Display error message if any */}
        {error && (
          <div className="error-message">
            {error}
          </div>
        )}
        
        {/* Display download link once MIDI is generated */}
        {midiUrl && (
          <div className="player fade-in">
            <div className="success-message">
              <span className="success-icon">✨</span>
              Music generated successfully!
            </div>
            <a 
              href={midiUrl} 
              download 
              className="download-button"
            >
              <span className="download-icon">⬇️</span>
              Download MIDI File
            </a>
          </div>
        )}
      </div>
    </div>
  );
}

export default App; // Exporting the App component