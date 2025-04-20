import axios from 'axios';
import { useState } from 'react';
import './App.css';

function App() {
  const [mood, setMood] = useState('happy');
  const [midiUrl, setMidiUrl] = useState(null);
  const [isGenerating, setIsGenerating] = useState(false);
  const [error, setError] = useState(null);

  const generateMusic = async () => {
    try {
      setIsGenerating(true);
      setError(null);
      const response = await axios.post('http://localhost:8000/generate', {
        mood: mood
      });
      
      const fullUrl = `http://localhost:8000${response.data.midi_path}`;
      setMidiUrl(fullUrl);
    } catch (error) {
      console.error("Generation failed:", error);
      setError("Failed to generate music. Please try again.");
    } finally {
      setIsGenerating(false);
    }
  };

  const getMoodEmoji = (currentMood) => {
    const emojis = {
      happy: "😊",
      sad: "😢",
      angry: "😠",
      calm: "😌"
    };
    return emojis[currentMood] || "🎵";
  };

  return (
    <div className="app">
      <div className="music-waves">
        <div className="wave"></div>
        <div className="wave"></div>
        <div className="wave"></div>
      </div>

      <div className="content">
        <h1 className="title">
          <span className="emoji-bounce">{getMoodEmoji(mood)}</span>
          Mood Music Generator
        </h1>

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

        {error && (
          <div className="error-message">
            {error}
          </div>
        )}
        
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

export default App;