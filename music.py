import time


# NOTE FREQUENCIES
# ================

DELAY = 0
# Octave 2
A2  = 110.00
AS2 = 116.54
B2  = 123.47
# Octave 3
C3  = 130.81
CS3 = 138.59
D3  = 146.83
DS3 = 155.56
E3  = 164.81
F3  = 174.61
FS3 = 185.00
G3  = 196.00
GS3 = 207.65
A3  = 220.00
AS3 = 233.08
B3  = 246.94
# Octave 4
C4  = 261.63
CS4 = 277.18
D4  = 293.66
dS4 = 311.13
E4  = 329.63
F4  = 349.23
FS4 = 369.99
G4  = 392.00
GS4 = 415.30
A4  = 440.00
AS4 = 466.16
B4  = 493.88
# Octave 5
C5  = 523.25
CS5 = 554.37
D5  = 587.33
DS5 = 622.25
E5  = 659.25
F5  = 698.46
FS5 = 739.99
G5  = 783.99
GS5 = 830.61
A5  = 880.00
AS5 = 932.33
B5  = 987.77
# Octave 6
C6  = 1046.50
CS6 = 1108.73
D6  = 1174.66
DS6 = 1244.51
E6  = 1318.51
F6  = 1396.91


# SONGS
# =====

class starwars:
    bpm = 83
    notes = [
        (G3, 1/3),
        (G3, 1/3),
        (G3, 1/3),
        (C4, 1),
        (G4, 1),
        (F4, 1/3),
        (E4, 1/3),
        (D4, 1/3),
        (C5, 1),
        (G4, 1),
        (F4, 1/3),
        (E4, 1/3),
        (D4, 1/3),
        (C5, 1),
        (G4, 1),
        (F4, 1/3),
        (E4, 1/3),
        (F4, 1/3),
        (D4, 1),
    ]

class close_encounters:
    bpm = 120
    notes= [
        (G4, 1),
        (A4, 1),
        (F4, 1),
        (F3, 1),
        (C4, 2),
    ]

class startrek:
    bpm = 120
    notes = [
    (A5, 4),
    (E5, 4),
    (G5, 4),
    (B4, 4),
    #(A4, full*4),

    (A2, 5/4),
    (DELAY, 1/4),
    (D3, 1/2),
    (G3, 2),
    (DELAY, 1/2),
    (FS3, 1),
    (D3, 1/4),
    (DELAY, 1/4),
    (B2, 1/2),
    (E3, 1/2),
    (A3, 9/4),
    (DELAY, 1/2),
    (A3, 1/4),
    (CS4, 4),
    ]

class indiana:
    bpm = 135
    notes = [
        (E3, 3/8),
        (DELAY, 3/8),
        (F3, 1/8),
        (DELAY, 1/8),
        (G3, 1/4),
        (DELAY, 1/4),
        (C4, 9/4),
        (DELAY, 1/4),
        (D3, 1/4),
        (DELAY, 1/2),
        (E3, 1/8),
        (DELAY, 1/8),
        (F3, 11/4),
        (DELAY, 1/4),
        (G3, 3/8),
        (DELAY, 3/8),
        (A3, 1/8),
        (DELAY, 1/8),
        (B3, 1/4),
        (DELAY, 1/4),
        (F4, 9/4),
        (DELAY, 1/4),
        (A3, 1/4),
        (DELAY, 1/2),
        (B3, 1/8),
        (DELAY, 1/8),
        (C4, 7/8),
        (DELAY, 1/8),
        (D4, 7/8),
        (DELAY, 1/8),
        (E4, 3/4),
    ]

class bttf:
    bpm = 75
    notes = [
        (CS3, 1/4),
        (DELAY, 3/4),
        (GS3, 1),
        (DELAY, 1/2),
        (CS4, 1/4),
        (DELAY, 1/4),
        (B3, 3/2),
        (DELAY, 1/4),
        (AS3, 1/8),
        (GS3, 1/8),
        (AS3, 1/4),
        (DELAY, 1/2),
        (GS3, 1/4),
        (DELAY, 1/4),
        (FS3, 1/4),
        (DELAY, 1/2),
        (GS3, 5+(3/4))
    ]

class swbattle:
    bpm = 120
    notes = [
        (A3, 1/8),
        (DELAY, 1/4),
        (A3, 7/8),
        (FS3, 1/2),
        (DELAY, 1/4),
        (A3, 1/8),
        (DELAY, 1/4),
        (A3, 3/4),
        (DELAY, 1/8),
        (FS3, 1/2),
        (DELAY, 1/4),
        (C4, 1/4),
        (DELAY, 1/8),
        (C4, 7/8),
        (B3, 3/8),
        (DELAY, 1/4),
        (C4, 1/8),
        (B3, 1/4),
        (A3, 1/8),
        (DELAY, 3/8),
        (FS3, 2),
    ]

class valkyries:
    bpm = 160
    notes = [
        (B4, 1/4),
        (DELAY, 1/2),
        (FS4, 1/4),
        (B4, 1/2),
        (DELAY, 1/4),
        (D5, 3/2),
        (B4, 3/2),
        (D5, 1/4),
        (DELAY, 1/2),
        (B4, 1/4),
        (D5, 1/4),
        (DELAY, 1/4),
        (FS5, 3/2),
        (D5, 3/2),
        (FS5, 1/4),
        (DELAY, 1/2),
        (D5, 1/4),
        (FS5, 1/4),
        (DELAY, 1/4),
        (A5, 3/2),
        (A4, 5/4),
        (DELAY, 1/4),
        (D5, 1/4),
        (DELAY, 1/2),
        (B4, 1/4),
        (D5, 1/4),
        (DELAY, 1/4),
        (FS5, 7),
    ]

class portal:
    bpm = 48
    notes = [
        (G4, 1/4),
        (FS4, 1/4),
        (E4, 1/4),
        (E4, 1/4),
        (FS4, 1/4),
        (DELAY, 10/4),
        (A3, 1/4),
        (G4, 1/4),
        (FS4, 1/4),
        (E4, 1/4),
        (E4, 1/4),
        (DELAY, 1/4),
        (FS4, 1/4),
        (DELAY, 1/2),
        (D4, 1/4),
        (DELAY, 1/4),
        (E4, 1/4),
        (A3, 1/4),
        (DELAY, 7/4),
        (A3, 1/4),
        (E4, 1/4),
        (DELAY, 1/4),
        (FS4, 1/4),
        (G4, 1/4),
        (DELAY, 1/2),
        (E4, 1/4),
        (CS4, 1/4),
        (DELAY, 1/4),
        (D4, 1/4),
        (DELAY, 1/2),
        (E4, 1/4),
        (DELAY, 1/4),
        (A3, 1/4),
        (A3, 1/4),
        (DELAY, 1/4),
        (FS4, 1/4),
    ]


class tank1:
    bpm = 280
    notes = [
        (D5, 1/2),
        (D5, 1),
        (D5, 1/2),
        (D5, 1),
        (D5, 1/2),
        (D5, 1/2),
        (DELAY, 1/2),
        (D5, 1/2),
        (D5, 1),
        (F5, 1),
        (FS5, 1),
        (DELAY, 8),
    ]

class tank2:
    bpm = 280
    notes = [
        (C3, 3/2),
        (G3, 3/2),
        (FS3, 1),
        (F3, 3/2),
        (DS3, 1),
        (AS2, 1/2),
        (AS2, 1),
    ]
class tank3:
    bpm = 280
    notes = [
        (C5, 1/2),
        (G5, 1),
        (C5, 1/2),
        (FS5, 1),
        (C5, 1/2),
        (DS5, 1/2),
        (DELAY, 1/2),
        (C5, 1/2),
        (AS4, 2),
        (C5, 7),
        (DELAY, 2),
    ]
class tank4:
    bpm = 280
    notes = [
        (F5, 1/2),
        (C6, 1),
        (F5, 1/2),
        (B5, 1),
        (F5, 1/2),
        (GS5, 1/2),
        (DELAY, 1/2),
        (F5, 1/2),
        (DS5, 2),
        (F5, 7),
        (DELAY, 2),
    ]
class tank5:
    bpm = 280
    notes = [
        (AS5, 1/2),
        (B5, 1/2),
        (DELAY, 2),
        (AS5, 1/2),
        (B5, 1/2),
        (DELAY, 2),
        (D6, 1/2),
        (CS6, 1/2),
        (DELAY, 1),
        (C6, 1/2),
        (CS6, 1/2),
        (DELAY, 2),
        (C6, 1/2),
        (CS6, 1/2),
        (DELAY, 2),
        (F6, 1/2),
        (E6, 1/2),
        (DELAY, 1),
    ]


# MUSIC FUNCTIONS
# ===============

def play_music(magtag, song):
    beat = 60 / song.bpm
    for note, duration in song.notes:
        if note == DELAY:
            time.sleep(beat*duration)
        else:
            magtag.peripherals.play_tone(note, beat*duration)

def play_tank(magtag):
    play_music(magtag, tank1)
    for x in range(0,4):
        play_music(magtag, tank2)
    play_music(magtag, tank3)
    play_music(magtag, tank3)
    play_music(magtag, tank4)
    play_music(magtag, tank3)
    play_music(magtag, tank5)
    play_music(magtag, tank3)

