import random
import tkinter as tk
from tkinter import ttk, filedialog
from mido import Message, MidiFile, MidiTrack, MetaMessage, bpm2tempo

# --------------------------
# NOTE SYSTEM
# --------------------------
NOTE_MAP = {"C":0,"C#":1,"D":2,"D#":3,"E":4,"F":5,"F#":6,"G":7,"G#":8,"A":9,"A#":10,"B":11}
NOTE_NAMES = list(NOTE_MAP.keys())

MODES = {
    "ionian": [0,2,4,5,7,9,11],
    "dorian": [0,2,3,5,7,9,10],
    "phrygian": [0,1,3,5,7,8,10],
    "lydian": [0,2,4,6,7,9,11],
    "mixolydian": [0,2,4,5,7,9,10],
    "aeolian": [0,2,3,5,7,8,10],
    "locrian": [0,1,3,5,6,8,10],
}

PROGRESSIONS = {
    "standard": [[0, 5, 6, 4], [0, 3, 4, 6]],
    "ambient": [[0, 2, 5, 3], [0, 4, 2, 6]],
    "weird": [[0, 1, 6, 3], [2, 6, 1, 5]],

    "dark": [
        [0, 6, 5, 4],
        [0, 3, 6, 2],
        [0, 5, 3, 2],
    ],

    "dystopian": [
        [0, 1, 6, 2],
        [0, 6, 1, 5],
        [2, 1, 6, 0],
    ],

    "jazz": [
        [0, 2, 5, 1],
        [0, 4, 1, 5],
        [2, 5, 1, 4],
    ],

    "emotional": [
        [0, 4, 5, 3],
        [0, 3, 5, 4],
        [0, 5, 4, 3],
    ],

    "uplifting": [
        [0, 4, 5, 6],
        [0, 3, 4, 5],
        [0, 5, 6, 4],
    ],

    "sad": [
        [0, 3, 4, 3],
        [0, 5, 3, 4],
        [0, 2, 3, 1],
    ],

    "introspective": [
        [0, 3, 2, 3],
        [0, 5, 2, 4],
        [0, 2, 4, 3],
    ],

    "spacey": [
        [0, 2, 1, 5],
        [0, 6, 2, 5],
        [0, 1, 2, 6],
    ],

    # RADIOHEAD-INSPIRED (Am / Fm modal mixture vibes)
    "am/fmhead": [
        [0, 5, 2, 6],   # i - VI - III - VII (Am F C G feel)
        [0, 3, 5, 4],   # i - iv - VI - V
        [0, 1, 5, 2],   # i - bII - VI - III (tense chromatic feel)
        [0, 3, 2, 6],   # i - iv - III - VII
    ],
}

# --------------------------
# CORE
# --------------------------
def build_scale(root, mode, octave):
    base = NOTE_MAP[root] + octave*12
    return [base+i for i in MODES[mode]]


def build_chord(scale, degree):
    s = scale + [n+12 for n in scale]
    return [s[degree], s[degree+2], s[degree+4], s[degree+6]]

# --------------------------
# RADIOHEAD CHORD HELPERS
# --------------------------

def minor7(root):
    return [root, root+3, root+7, root+10]


def major7(root):
    return [root, root+4, root+7, root+11]


def generate_progression():
    pattern = random.choice(PROGRESSIONS[prog_var.get()])
    chords = []

    base = NOTE_MAP[root_var.get()] + int(octave_var.get())*12

    for d in pattern:
        # Special Radiohead logic
        if prog_var.get() == "am/fmhead":

            # bII (chromatic tension)
            if d == 1:
                root = base + 1
                chord = major7(root)

            # iv minor (borrowed chord)
            elif d == 3:
                root = base + 5
                chord = minor7(root)

            else:
                scale = build_scale(root_var.get(), mode_var.get(), int(octave_var.get()))
                chord = build_chord(scale, d)

            # --------------------------
            # RADIOHEAD ENHANCEMENTS
            # --------------------------

            # occasional sus2 / sus4
            if random.random() > 0.6:
                chord = [
                    chord[0],
                    chord[0] + random.choice([2, 5]),  # sus2 or sus4
                    chord[2],
                    chord[3]
                ]

            # occasional cluster (tight dissonance)
            if random.random() > 0.7:
                chord.append(chord[0] + 1)  # add minor 2nd tension

            # slight voice leading (reduce jumps)
            if chords:
                prev = chords[-1]
                chord = [
                    note if abs(note - prev[i % len(prev)]) < 7 else note - 12
                    for i, note in enumerate(chord)
                ]

        else:
            scale = build_scale(root_var.get(), mode_var.get(), int(octave_var.get()))
            chord = build_chord(scale, d)

        chords.append(chord)

    return chords

# --------------------------
# VISUALIZER
# --------------------------
def draw_visual(prog):
    canvas.delete("all")

    length = float(length_var.get())
    bars = int(bars_var.get())
    overlap = overlap_var.get()
    velocity = velocity_var.get()

    ticks = 480
    base = int(ticks * length)

    time_cursor = 0

    for _ in range(bars):
        for chord in prog:
            durations = []

            for i, note in enumerate(chord):
                duration = base

                x = int(time_cursor / ticks * 40)
                width = int(duration / ticks * 40)
                y = 140 - (note*2 % 140)

                ratio = velocity/127
                r = int(255*ratio)
                b = int(255*(1-ratio))
                color = f"#{r:02x}00{b:02x}"

                canvas.create_rectangle(x, y, x+width, y+4, fill=color, outline="")
                durations.append(duration)

            release = int(max(durations)*(1-overlap))
            time_cursor += release

# --------------------------
# MIDI
# --------------------------
def export_midi(prog, path):
    mid = MidiFile()
    track = MidiTrack()
    mid.tracks.append(track)

    track.append(MetaMessage('set_tempo', tempo=bpm2tempo(int(tempo_var.get()))))

    ticks = 480
    length = float(length_var.get())
    base = int(ticks * length)

    for _ in range(int(bars_var.get())):
        for chord in prog:
            for note in chord:
                track.append(Message('note_on', note=note, velocity=velocity_var.get(), time=0))
            for i,note in enumerate(chord):
                track.append(Message('note_off', note=note, velocity=0, time=base if i==0 else 0))

    mid.save(path)

# --------------------------
# GUI
# --------------------------
def generate():
    prog = generate_progression()
    state["prog"] = prog
    draw_visual(prog)


def export():
    if "prog" not in state: return
    path = filedialog.asksaveasfilename(defaultextension=".mid")
    if path:
        export_midi(state["prog"], path)



def reset():
    state.clear()
    canvas.delete("all")

# --------------------------
# RANDOMIZE SETTINGS
# --------------------------
def randomize():
    # random selections
    root_var.set(random.choice(NOTE_NAMES))
    mode_var.set(random.choice(list(MODES.keys())))
    prog_var.set(random.choice(list(PROGRESSIONS.keys())))
    octave_var.set(str(random.randint(2, 5)))
    length_var.set(random.choice(["1", "2", "4", "8"]))
    bars_var.set(random.choice(["2", "4", "8"]))
    tempo_var.set(str(random.randint(70, 140)))
    overlap_var.set(round(random.uniform(0.0, 0.6), 2))
    velocity_var.set(random.randint(50, 110))

    # regenerate after randomizing
    prog = generate_progression()
    state["prog"] = prog
    draw_visual(prog)

# --------------------------
# APP
# --------------------------
app = tk.Tk()
app.geometry("520x600")
app.resizable(False, False)
app.columnconfigure(0, weight=1)
app.columnconfigure(1, weight=1)


state = {}

root_var = tk.StringVar(value="C")
mode_var = tk.StringVar(value="aeolian")
prog_var = tk.StringVar(value="ambient")
octave_var = tk.StringVar(value="4")
length_var = tk.StringVar(value="2")
bars_var = tk.StringVar(value="4")
tempo_var = tk.StringVar(value="120")
overlap_var = tk.DoubleVar(value=0.3)
velocity_var = tk.IntVar(value=80)

# UI
ttk.Label(app, text="Root").grid(row=0, column=0, padx=8, pady=4, sticky="ew")
ttk.Combobox(app, textvariable=root_var, values=NOTE_NAMES).grid(row=0, column=1, padx=8, pady=4, sticky="ew")

ttk.Label(app, text="Mode").grid(row=1, column=0, padx=8, pady=4, sticky="ew")
ttk.Combobox(app, textvariable=mode_var, values=list(MODES.keys())).grid(row=1, column=1, padx=8, pady=4, sticky="ew")

ttk.Label(app, text="Progression").grid(row=2, column=0, padx=8, pady=4, sticky="ew")
ttk.Combobox(app, textvariable=prog_var, values=list(PROGRESSIONS.keys())).grid(row=2, column=1, padx=8, pady=4, sticky="ew")

ttk.Label(app, text="Length").grid(row=3, column=0, padx=8, pady=4, sticky="ew")
ttk.Combobox(app, textvariable=length_var, values=["1", "2", "4", "8"]).grid(row=3, column=1, padx=8, pady=4, sticky="ew")

ttk.Label(app, text="Bars").grid(row=4, column=0, padx=8, pady=4, sticky="ew")
ttk.Combobox(app, textvariable=bars_var, values=["1", "2", "4", "8"]).grid(row=4, column=1, padx=8, pady=4, sticky="ew")

ttk.Label(app, text="Tempo").grid(row=5, column=0, padx=8, pady=4, sticky="ew")
ttk.Entry(app, textvariable=tempo_var).grid(row=5, column=1, padx=8, pady=4, sticky="ew")

ttk.Label(app, text="Overlap").grid(row=6, column=0, padx=8, pady=4, sticky="ew")
ttk.Scale(app, from_=0, to=0.9, orient="horizontal", variable=overlap_var, command=lambda v: draw_visual(state.get("prog", []))).grid(row=6, column=1, padx=8, pady=4, sticky="ew")

ttk.Label(app, text="Velocity").grid(row=7, column=0, padx=8, pady=4, sticky="ew")

velocity_frame = ttk.Frame(app)
velocity_frame.grid(row=7, column=1, padx=8, pady=4, sticky="ew")

velocity_scale = ttk.Scale(
    velocity_frame,
    from_=40,
    to=127,
    orient="horizontal",
    variable=velocity_var,
    command=lambda v: update_velocity_display(v)
)
velocity_scale.pack(side="left", fill="x", expand=True)

velocity_label = ttk.Label(velocity_frame, text=str(velocity_var.get()), width=4)
velocity_label.pack(side="right")

# update function
def update_velocity_display(v):
    velocity_label.config(text=str(int(float(v))))
    draw_visual(state.get("prog", []))

canvas = tk.Canvas(app, width=360, height=120, bg="black")
canvas.grid(row=8, column=0, columnspan=2, padx=8, pady=6, sticky="ew")

ttk.Button(app, text="Generate", command=generate).grid(row=9, column=0, columnspan=2, padx=8, pady=4, sticky="ew")
ttk.Button(app, text="Export", command=export).grid(row=10, column=0, columnspan=2, padx=8, pady=4, sticky="ew")
ttk.Button(app, text="Reset", command=reset).grid(row=11, column=0, columnspan=2, padx=8, pady=4, sticky="ew")
ttk.Button(app, text="Randomize", command=randomize).grid(row=12, column=0, columnspan=2, padx=8, pady=4, sticky="ew")



app.mainloop()
