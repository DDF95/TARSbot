import random
import subprocess
import tempfile
from copy import deepcopy

import music21
from pyrogram import Client, filters


@Client.on_message(filters.command("music", "!"))
async def music(client, message):
    pitch_names = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]

    intro = []
    for i in range(8):
        p = random.choice(pitch_names) + str(random.randint(1, 3))
        intro.append(music21.note.Note(p))
    
    verse = []
    for i in range(16):
        p = random.choice(pitch_names) + str(random.randint(2, 4))
        verse.append(music21.note.Note(p))
    
    chorus = []
    for i in range(10):
        p = random.choice(pitch_names) + str(random.randint(3, 5))
        chorus.append(music21.note.Note(p))
    
    bridge = []
    for i in range(16):
        p = random.choice(pitch_names) + str(random.randint(2, 3))
        bridge.append(music21.note.Note(p))
    
    outro = []
    for i in range(8):
        p = random.choice(pitch_names) + str(random.randint(1, 5))
        outro.append(music21.note.Note(p))
    
    stream = music21.stream.Stream()
    stream.append(music21.instrument.ElectricGuitar())
    stream.append(intro + verse + chorus + deepcopy(verse) + bridge + deepcopy(chorus) + outro)
    
    with tempfile.NamedTemporaryFile(mode='wb', suffix='.mid', delete=False) as file:
        stream.write('midi', fp=file.name)
        midi_file_name = file.name
    
    ogg_file_name = midi_file_name.replace('.mid', '.ogg')
    subprocess.call(['fluidsynth', '-F', ogg_file_name, '-ni', midi_file_name])
    
    intro_note_names = []
    verse_note_names = []
    chorus_note_names = []
    bridge_note_names = []
    outro_note_names = []
    for i, note in enumerate(stream.flat.notes):
        if i < 8:
            intro_note_names.append(note.nameWithOctave)
        elif i < 24:
            verse_note_names.append(note.nameWithOctave)
        elif i < 34:
            chorus_note_names.append(note.nameWithOctave)
        elif i < 50:
            pass
        elif i < 66:
            bridge_note_names.append(note.nameWithOctave)
        elif i < 76:
            pass
        elif i < 84:
            outro_note_names.append(note.nameWithOctave)
    
    note_string = f"Intro: {', '.join(intro_note_names)}\n\nVerse: {', '.join(verse_note_names)}\n\nChorus: {', '.join(chorus_note_names)}\n\nBridge: {', '.join(bridge_note_names)}\n\nOutro: {', '.join(outro_note_names)}"
    
    await message.reply_voice(ogg_file_name, caption=note_string)


@Client.on_message(filters.command("sing", "!"))
async def sing(client, message):
    note_mapping = {
        "A": "C2",
        "B": "C#2",
        "C": "D2",
        "D": "D#2",
        "E": "E2",
        "F": "F2",
        "G": "F#2",
        "H": "G2",
        "I": "G#2",
        "J": "A2",
        "K": "A#2",
        "L": "B2",
        "M": "C3",
        "N": "C#3",
        "O": "D3",
        "P": "D#3",
        "Q": "E3",
        "R": "F3",
        "S": "F#3",
        "T": "G3",
        "U": "G#3",
        "V": "A3",
        "W": "A#3",
        "X": "B3",
        "Y": "C4",
        "Z": "C#4"
    }

    if message.reply_to_message:
        song = message.reply_to_message.text.upper()
    else:
        if message.text[6:] == "--help":
            await message.reply_text("Pitch map:\n\nA = C2\nB = C#2\nC = D2\nD = D#2\nE = E2\nF = F2\nG = F#2\nH = G2\nI = G#2\nJ = A2\nK = A#2\nL = B2\nM = C3\nN = C#3\nO = D3\nP = D#3\nQ = E3\nR = F3\nS = F#3\nT = G3\nU = G#3\nV = A3\nW = A#3\nX = B3\nY = C4\nZ = C#4")
            return
        else:
            song = message.text[6:].upper().split("\n")[0].strip()

    notes = []
    for char in song:
        if char == " ":
            notes.append(music21.note.Rest())
        elif char in note_mapping:
            notes.append(music21.note.Note(note_mapping[char]))

    stream = music21.stream.Stream()

    bpm = 300  # default value
    instrument = "Bagpipes"  # default value

    if message.text:
        lines = message.text.split("\n")
        for line in lines:
            if line.startswith("--instrument"):
                instrument = line.split(" ")[1].strip()
            if line.startswith("--bpm"):
                bpm = int(line.split(" ")[1].strip())

    stream.append(getattr(music21.instrument, instrument)())
    stream.insert(0, music21.tempo.MetronomeMark(number=bpm))
    stream.append(notes)

    with tempfile.NamedTemporaryFile(mode='wb', suffix='.mid', delete=False) as file:
        stream.write('midi', fp=file.name)
        midi_file_name = file.name
    
    ogg_file_name = midi_file_name.replace('.mid', '.ogg')
    subprocess.call(['fluidsynth', '-F', ogg_file_name, '-ni', midi_file_name])

    caption = f"Instrument: {stream[0].instrumentName}\nBPM: {bpm}"

    if message.reply_to_message:
        await message.reply_to_message.reply_voice(ogg_file_name, caption=caption)
    else:
        await message.reply_voice(ogg_file_name, caption=caption)


@Client.on_message(filters.command("instruments", "!"))
async def instruments(client, message):
    instruments = [i for i in dir(music21.instrument) if isinstance(getattr(music21.instrument, i), type) and issubclass(getattr(music21.instrument, i), music21.instrument.Instrument)]
    await message.reply_text("Available instruments:\n\n" + "\n".join(instruments))
