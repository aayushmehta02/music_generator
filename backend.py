import os
import music21  # Music21 library for MIDI file creation and manipulation
import numpy as np
import tensorflow as tf  # TensorFlow for model loading and prediction
from fastapi import FastAPI, HTTPException  # FastAPI for building the web API
from fastapi.middleware.cors import CORSMiddleware  # To allow cross-origin requests
from fastapi.staticfiles import StaticFiles  # To serve static files like MIDI downloads
from pydantic import BaseModel  # For request body validation

# Initialize FastAPI app
app = FastAPI()

# Enable CORS (Cross-Origin Resource Sharing) to allow frontend to interact with backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (can be restricted to specific domains)
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount the current directory to serve static files (used for serving generated MIDI files)
app.mount("/static", StaticFiles(directory="."), name="static")

# Load the pre-trained music generation model
model = tf.keras.models.load_model("music_gen_model.keras")

# Define the request body structure for /generate endpoint
class MoodRequest(BaseModel):
    mood: str  # Expected values: "happy", "sad", "angry", "calm"
    length: int = 100  # Number of notes to generate (default = 100)

# Define the endpoint for generating music based on the requested mood
@app.post("/generate")
def generate_music(request: MoodRequest):
    # Map moods to numerical categories (these must match the model's training labels)
    mood_map = {"happy": 0, "sad": 2, "angry": 1, "calm": 3}
    
    # Generate random initial seed (32 pitches and durations) for input to model
    seed_pitch = np.random.randint(0, 128, 32).tolist()  # MIDI pitch range
    seed_dur = np.random.rand(32).tolist()  # Random durations (to be cleaned later)
    generated = []  # List to store generated notes

    # Generate notes iteratively using the model
    for _ in range(request.length):
        # Predict next pitch and duration
        pitch_pred, dur_pred = model.predict([
            np.array([seed_pitch]),  # Shape: (1, 32)
            np.array([seed_dur]),    # Shape: (1, 32)
            np.array([[mood_map[request.mood]] * 32])  # Mood as input, shape: (1, 32)
        ], verbose=0)

        # Get the predicted pitch as the index with the highest probability
        next_pitch = int(np.clip(np.argmax(pitch_pred[0]), 0, 127))

        # Define valid musical durations and round prediction to the closest one
        valid_durations = [0.25, 0.5, 1.0, 2.0]  # Sixteenth, eighth, quarter, half notes
        next_dur_raw = float(dur_pred[0][0])
        next_dur = min(valid_durations, key=lambda x: abs(x - next_dur_raw))

        # Append the generated note to the list
        generated.append({"pitch": next_pitch, "duration": next_dur})

        # Slide the window forward by one
        seed_pitch = seed_pitch[1:] + [next_pitch]
        seed_dur = seed_dur[1:] + [next_dur]

    # Convert the generated notes to a music21 stream for MIDI creation
    output_stream = music21.stream.Stream()
    current_offset = 0.0  # Keeps track of the timing of each note

    for note_data in generated:
        pitch = note_data["pitch"]
        dur = note_data["duration"]

        # Validate and fix invalid durations if necessary
        if dur <= 0:
            dur = 0.25  # Default to sixteenth note

        # Add valid note to the stream
        if 0 <= pitch <= 127:
            n = music21.note.Note(pitch)
            n.duration = music21.duration.Duration(dur)
            n.offset = current_offset  # Schedule the note at the right time
            current_offset += dur  # Update the offset for the next note
            output_stream.append(n)

    # Generate a unique MIDI filename using mood and random number
    midi_path = f"generated_{request.mood}_{np.random.randint(1000)}.mid"

    # Save the generated music to a MIDI file
    output_stream.write('midi', fp=midi_path)

    # Return the path to the generated MIDI file (to be accessed from frontend)
    return {"midi_path": f"/static/{midi_path}"}