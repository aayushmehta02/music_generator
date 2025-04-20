import os

import music21  # type: ignore
import numpy as np
import tensorflow as tf  # type: ignore
from fastapi import FastAPI, HTTPException  # type: ignore
from fastapi.middleware.cors import CORSMiddleware  # type: ignore
from fastapi.staticfiles import StaticFiles  # type: ignore
from pydantic import BaseModel

app = FastAPI()

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static files
app.mount("/static", StaticFiles(directory="."), name="static")

# Load model
model = tf.keras.models.load_model("music_gen_model.keras")

class MoodRequest(BaseModel):
    mood: str  # "happy", "sad", "angry", "calm"
    length: int = 100

@app.post("/generate")
def generate_music(request: MoodRequest):
    mood_map = {"happy": 0, "sad": 2, "angry": 1, "calm": 3}
    
    # Generation logic (adapt from Colab code)
    seed_pitch = np.random.randint(0, 128, 32).tolist()
    seed_dur = np.random.rand(32).tolist()
    generated = []
    
    for _ in range(request.length):
        pitch_pred, dur_pred = model.predict([
            np.array([seed_pitch]),
            np.array([seed_dur]),
            np.array([[mood_map[request.mood]]*32])
        ], verbose=0)
        
        next_pitch = int(np.clip(np.argmax(pitch_pred[0]), 0, 127))
        
        valid_durations = [0.25, 0.5, 1.0, 2.0]  # sixteenth, eighth, quarter, half notes
        next_dur_raw = float(dur_pred[0][0])
        next_dur = min(valid_durations, key=lambda x: abs(x - next_dur_raw))

        generated.append({"pitch": next_pitch, "duration": next_dur})
        
        seed_pitch = seed_pitch[1:] + [next_pitch]
        seed_dur = seed_dur[1:] + [next_dur]

    # Convert to MIDI with offsets (VERY IMPORTANT)
    output_stream = music21.stream.Stream()
    current_offset = 0.0
    
    for note_data in generated:
        pitch = note_data["pitch"]
        dur = note_data["duration"]

        # Only add valid note durations and pitches
        if dur <= 0:
            dur = 0.25  # default to a sixteenth note if something weird

        if 0 <= pitch <= 127:
            n = music21.note.Note(pitch)
            n.duration = music21.duration.Duration(dur)
            n.offset = current_offset
            current_offset += dur
            output_stream.append(n)

    # Save the MIDI file properly
    midi_path = f"generated_{request.mood}_{np.random.randint(1000)}.mid"
    output_stream.write('midi', fp=midi_path)

    return {"midi_path": f"/static/{midi_path}"}
