import random
import tkinter as tk
from tkinter import ttk, filedialog
from mido import Message, MidiFile, MidiTrack

NOTE_MAP = {
    "C": 0,
    "C#": 1,
    "D": 2,
    "D#": 3,
    "E": 4,
    "F": 5,
    "F#": 6,
    "G": 7,
    "G#": 8,
    "A": 9,
    "A#": 10,
    "B": 11,
}

NOTE_NAMES = list(NOTE_MAP.keys())

MODES = {
    "ionian": [0, 2, 4, 5, 7, 9, 11],
    "dorian": [0, 2, 3, 5, 7, 9, 10],
    "phrygian": [0, 1, 3, 5, 7, 8, 10],
    "lydian": [0, 2, 4, 6, 7, 9, 11],
    "mixolydian": [0, 2, 4, 5, 7, 9, 10],
    "aeolian": [0, 2, 3, 5, 7, 8, 10],
    "locrian": [0, 1, 3, 5, 6, 8, 10],
}

PROGRESSIONS = {
    "standard": [[0, 5, 6, 4], [0, 3, 4, 6]],
    "ambient": [[0, 2, 5, 3], [0, 4, 2, 6]],
    "weird": [[0, 1, 6, 3], [2, 6, 1, 5]],
    # NEW DARK PROGRESSIONS (minor-heavy, moody)
    "dark": [
        [0, 6, 5, 4],  # i - VII - VI - V
        [0, 3, 6, 2],  # i - iv - VII - iii
        [0, 5, 3, 2],  # i - VI - iv - iii
    ],
    # NEW DYSTOPIAN (tense / unstable)
    "dystopian": [
        [0, 1, 6, 2],  # i - bII - VII - iii (phrygian feel)
        [0, 6, 1, 5],  # i - VII - bII - VI
        [2, 1, 6, 0],  # iii - bII - VII - i (unresolved feel)
    ],
    # NEW JAZZ (extended harmony feel)
    "jazz": [
        [0, 2, 5, 1],  # i - iii - VI - ii
        [0, 4, 1, 5],  # i - V - ii - VI
        [2, 5, 1, 4],  # iii - VI - ii - V (classic jazz movement)
    ],
    # NEW EMOTIONAL (melodic / cinematic)
    "emotional": [
        [0, 4, 5, 3],  # i - V - VI - iv
        [0, 3, 5, 4],  # i - iv - VI - V
        [0, 5, 4, 3],  # i - VI - V - iv
    ],
    # NEW UPLIFTING (bright / hopeful)
    "uplifting": [
        [0, 4, 5, 6],  # i - V - VI - VII
        [0, 3, 4, 5],  # i - iv - V - VI
        [0, 5, 6, 4],  # i - VI - VII - V
    ],
    # NEW SAD (melancholic / minimal)
    "sad": [
        [0, 3, 4, 3],  # i - iv - V - iv
        [0, 5, 3, 4],  # i - VI - iv - V
        [0, 2, 3, 1],  # i - iii - iv - ii
    ],
    # NEW INTROSPECTIVE (slow movement / reflective)
    "introspective": [
        [0, 3, 2, 3],  # i - iv - iii - iv
        [0, 5, 2, 4],  # i - VI - iii - V
        [0, 2, 4, 3],  # i - iii - V - iv
    ],
    # NEW SPACEY (floating / non-grounded)
    "spacey": [
        [0, 2, 1, 5],  # i - iii - ii - VI
        [0, 6, 2, 5],  # i - VII - iii - VI
        [0, 1, 2, 6],  # i - ii - iii - VII
    ],
}


def build_scale(root, mode, octave):
    base = NOTE_MAP[root] + octave * 12
    return [base + i for i in MODES[mode]]


def get_note_name(midi_note):
    return NOTE_NAMES[midi_note % 12]


def build_chord(scale, degree, voicing):
    s = scale + [n + 12 for n in scale]

    root = s[degree]
    third = s[degree + 2]
    fifth = s[degree + 4]
    seventh = s[degree + 6]

    if voicing == "close":
        chord = [root, third, fifth, seventh]
    elif voicing == "wide":
        chord = [root, fifth + 12, third + 12, seventh + 12]
    else:  # super wide
        chord = [root, fifth + 12, third + 24, seventh + 24]

    if random.random() > 0.5:
        chord.append(s[(degree + 1) % 7] + 24)

    return chord


def detect_quality(chord):
    intervals = sorted([(n - chord[0]) % 12 for n in chord])
    if 4 in intervals and 7 in intervals:
        return "maj"
    if 3 in intervals and 7 in intervals:
        return "m"
    if 3 in intervals and 6 in intervals:
        return "dim"
    if 4 in intervals and 8 in intervals:
        return "aug"
    return ""


def chord_name(chord):
    root_note = get_note_name(chord[0])
    quality = detect_quality(chord)

    if any((n - chord[0]) % 12 == 10 for n in chord):
        quality += "7"
    if any((n - chord[0]) % 12 == 11 for n in chord):
        quality += "maj7"
    if any((n - chord[0]) % 12 == 2 for n in chord):
        quality += "9"

    return f"{root_note}{quality}"


def generate_progression(root, base_mode, mode_type, voicing, octave, multi_mode):
    pattern = random.choice(PROGRESSIONS[mode_type])
    chords = []
    names = []

    for d in pattern:
        if multi_mode:
            mode = random.choice(list(MODES.keys()))
        else:
            mode = base_mode

        scale = build_scale(root, mode, octave)
        chord = build_chord(scale, d, voicing)

        chords.append(chord)
        names.append(chord_name(chord))

    return chords, names


def export_midi(prog, filename, length, humanize):
    mid = MidiFile()
    track = MidiTrack()
    mid.tracks.append(track)

    duration = int(480 * length)

    for chord in prog:
        for note in chord:
            t = random.randint(0, 10) if humanize else 0
            track.append(Message("note_on", note=note, velocity=70, time=t))

        for note in chord:
            track.append(Message("note_off", note=note, velocity=70, time=duration))

    mid.save(filename)


def generate():
    root = root_var.get()
    mode = mode_var.get()
    prog_mode = prog_var.get()
    voicing = voicing_var.get()
    octave = int(octave_var.get())

    chords, names = generate_progression(
        root, mode, prog_mode, voicing, octave, multi_mode_var.get()
    )

    output.delete("1.0", tk.END)
    for n in names:
        output.insert(tk.END, n + "\n")

    state["prog"] = chords
    output.insert(tk.END, "\nReady for next generation...\n")


def export():
    if "prog" not in state:
        return

    path = filedialog.asksaveasfilename(defaultextension=".mid")
    if path:
        export_midi(state["prog"], path, float(length_var.get()), humanize_var.get())
        # Keep app active and reset output after export
        output.insert(tk.END, "\nExport complete. You can generate again.\n")


app = tk.Tk()
# Prevent app from closing accidentally after operations
app.protocol("WM_DELETE_WINDOW", lambda: None)
app.title("Advanced MIDI Generator")

state = {}

root_var = tk.StringVar(value="C")
mode_var = tk.StringVar(value="aeolian")
prog_var = tk.StringVar(value="ambient")
voicing_var = tk.StringVar(value="wide")
octave_var = tk.StringVar(value="4")
length_var = tk.StringVar(value="2")
humanize_var = tk.BooleanVar(value=True)
multi_mode_var = tk.BooleanVar(value=False)

ttk.Label(app, text="Root").grid(row=0, column=0)
ttk.Combobox(app, textvariable=root_var, values=NOTE_NAMES).grid(row=0, column=1)

ttk.Label(app, text="Mode").grid(row=1, column=0)
ttk.Combobox(app, textvariable=mode_var, values=list(MODES.keys())).grid(
    row=1, column=1
)

ttk.Label(app, text="Progression").grid(row=2, column=0)
ttk.Combobox(app, textvariable=prog_var, values=list(PROGRESSIONS.keys())).grid(
    row=2, column=1
)

ttk.Label(app, text="Voicing").grid(row=3, column=0)
ttk.Combobox(app, textvariable=voicing_var, values=["close", "wide", "super"]).grid(
    row=3, column=1
)

ttk.Label(app, text="Octave").grid(row=4, column=0)
ttk.Combobox(app, textvariable=octave_var, values=[str(i) for i in range(0, 8)]).grid(
    row=4, column=1
)

ttk.Label(app, text="Chord Length").grid(row=5, column=0)
ttk.Combobox(app, textvariable=length_var, values=["1", "2", "4"]).grid(row=5, column=1)

ttk.Checkbutton(app, text="Humanize", variable=humanize_var).grid(
    row=6, column=0, columnspan=2
)
ttk.Checkbutton(app, text="Multi-Mode Progression", variable=multi_mode_var).grid(
    row=7, column=0, columnspan=2
)

ttk.Button(app, text="Generate", command=generate).grid(row=8, column=0, columnspan=2)
ttk.Button(app, text="Export MIDI", command=export).grid(row=9, column=0, columnspan=2)

output = tk.Text(app, height=10, width=40)
output.grid(row=10, column=0, columnspan=2)

app.mainloop()
