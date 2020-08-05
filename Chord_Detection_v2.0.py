from scipy.io import wavfile
import numpy as np
import matplotlib.pyplot as plt
from math import log2, pow
from pychord import note_to_chord, Chord
import time

# globalne promenljive
chrom_scale = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B" ]
chords_in_every_key = [["C", "Dm", "Em", "F", "G", "Am", "Bdim"],
                       ["C#", "D#m", "Fm", "F#", "G#m", "A#dim"],
                       ["D", "Em", "F#m", "G", "A", "Bm", "C#dim"],
                       ["D#", "Fm", "Gm", "G#", "A#", "Cm", "Ddim"],
                       ["E", "F#m", "G#m", "A", "B", "C#m", "D#dim"],
                       ["F", "Gm", "Am", "A#", "C", "Dm", "Edim"],
                       ["F#", "G#m", "A#m", "B", "C#", "D#m", "Fdim"],
                       ["G", "Am", "Bm", "C", "D", "Em", "F#dim"],
                       ["G#", "A#m", "Cm", "C#", "D#", "Fm", "Gdim"],
                       ["A", "Bm", "C#m", "D", "E", "F#m", "G#dim"],
                       ["A#", "Cm", "Dm", "D#", "F", "Gm", "Adim"],
                       ["B", "C#m", "D#m", "E", "F#", "G#m", "A#dim"]]
common_chord_progressions = [["I", "IV", "V"],
                             ["I", "V", "vi", "IV"],
                             ["ii", "V", "I"],
                             ["I", "vi", "IV", "V"],
                             ["I", "IV", "V", "IV"],
                             ["vi", "IV", "I", "V"],
                             ["I", "IV", "ii", "V"],
                             ["I", "IV", "I", "V"],
                             ["I", "ii", "iii", "IV", "V"],
                             ["vi", "I", "V"]]
                                
# prazne promenljive za rezultate
chord_prog = []
chord_prog_simple = [] 
n_matches_in_every_key = []
durations = []
durations_simple = []
roman_index_prog = []

k = 0
data_chunk = []
current_time = 0
start = 0
end = 0

once = True

def simplify ():
    global chord_prog, chord_prog_simple, durations, durations_simple
    i = 0
    j = 0
    once = True

    for i in range(0, len(chord_prog)):
        if (i == 0):
            prev = chord_prog[i]
            
            #print("i = 0, prev is now {0} added to dur_simp {1}".format(prev, round(durations[i], 1)))
            chord_prog_simple.append(prev)
            durations_simple.append(round(durations[i], 1))
        
        if (i != 0): # and i != len(durations)):
            if (chord_prog[i] == prev):
                #print("Chord at {0} is the same, adding {1}".format(i, round(durations[i], 1)))
                durations_simple[j] = durations_simple[j] + round(durations[i], 1)
                
            else:
                #print("New chord found, appending new duration ", round(durations[i], 1))
                chord_prog_simple.append(chord_prog[i])  
                durations_simple.append(round(durations[i], 1))
                j = j + 1

                prev = chord_prog[i]

def output_results (key_id = "None"):
    i = 0
    j = 0
    for chord in chord_prog_simple:
        if (key_id != "None"):
            try:
                i = chords_in_every_key[key_id].index(chord)
                in_key = True
            except:
                in_key = False
            
            try:
                m = roman_index_prog.index(roman_index(i))
            except:
                roman_index_prog.append(roman_index(i))
        
            if (in_key):
                print (chord + " " + roman_index(i) + " " + str(round(durations_simple[j], 1)) + "s")
                j = j + 1
            else:
                print (chord + " out of key " + str(round(durations_simple[j], 1)) + "s")
                j = j + 1
        else:
            print (chord + " " + str(round(durations_simple[j], 1)) + "s")
            j = j + 1

        if (chord_prog_simple.index(chord) == len(chord_prog_simple) - 1):
            print()



# funkcija koja pretvara rimski broj u akord
def cpp_to_chord (cpp, key_id):
    r_indexes = ["I", "ii", "iii", "IV", "V", "vi", "VII"] # matrica sa rimskim indexima
    
    print("Chords: ", end = " ")

    for index in cpp:
        id = r_indexes.index(index)  
        print(chords_in_every_key[key_id][id], end = " ")

    print()

# funkcija koja proverava da li se pojavljuje common chord proggresion
def find_ccp (key_id):
    not_found = True
    i = 0

    while (not_found):
        if (roman_index_prog == common_chord_progressions[i]):
            not_found = False
            print ("\nPossible common chord progression found: ", common_chord_progressions[i], "\n")
            cpp_to_chord (common_chord_progressions[i], key_id)

        if (i == len(common_chord_progressions) - 1):
            break

        i = i + 1

    return "none"
    
# funkcija koja prebacuje random akorde koji se pojavljuju jako kratko (iste duzine kao i zadat interval)
# u prethodni poznat akord  (sto je vrlo verovatno i tacno)
def correction(interval):
    i = 0
    for duration in durations_simple:
        if (duration == interval):           
            print("Changed ", chord_prog_simple[i], " to ", chord_prog_simple[i - 1])
            chord_prog_simple[i] = chord_prog_simple[i - 1]
            # roman_index_prog[i] = roman_index_prog[i - 1]
        i = i + 1

# nesto poput enuma za rimske oznake
def roman_index(i):
    switcher = {0:"I",
                1:"ii",
                2:"iii",
                3:"IV",
                4:"V",
                5:"vi",
                6:"VII"
                }
    return switcher.get(i, "Invalid")

# funkcija koja proverava da li se akordi u datoj progresiji poklapaju sa odredjenim kljucem
def check_chord_matching(chord_prog, key):
    #print("Current key: ",key[0])
    n_matches = 0

    for chord in chord_prog:
        try:
            chord_id = key.index(chord)
            #print("Chord ", chord ," is in the key")
            n_matches = n_matches + 1
        except:
            #print("Chord ", chord ," is out of the key")
            pass

    n_matches_in_every_key.append(n_matches)
    
# funkcija koja odredjuje kljuc tako sto ide i uporedjuje sa svakim od mogucih kljuceva
def get_key():

    i = 0

    for note in chrom_scale:
        check_chord_matching(chord_prog_simple, chords_in_every_key[i])
        i = i + 1

    id = np.argmax(n_matches_in_every_key)

    print("We are in the key of ", chrom_scale[id], "\n")

    return id

def analyze_chunk(interval, fs, data_parts, duration, is_stereo = True): # rekurzivna funkcija

    global current_time, k, data_chunk # current time, current position in data_parts array , data chunk to be analyzed 
    global start, end # starting and ending position of chunk to be analyzed
    global once  # switch
    global chord_prog, durations # list to store chords that are found and list to store durations

    if (current_time >= duration or k == len(data_parts)): # basic if
        return "Done"
    
    if (once): # running once, to make starting interval
        end = start + interval
        once = False

    chunk = end - start # deo u sekundi

    n_intervals = round(chunk / interval)

    if (n_intervals > 1):
        for i in range (0, n_intervals):
            data_chunk = np.append(data_chunk, data_parts[k])
            k = k + 1
    else:
        data_chunk = data_parts[k]
        k = k + 1
        

    fft_and_freq = do_fft(fs, data_chunk, is_stereo) # kreiranje matrice sa fft vrednostima i odgovarajucim frekvencijama

    notes = find_all_notes(fft_and_freq[0], fft_and_freq[1]) # trazenje svih nota, sortiranih od one koja se cuje najvise

    triad = reference_sort([notes[0], notes[1], notes[2]], chrom_scale) # pravljenje trikorda od 3 najjaca tona, sortirana po hromatskoj skali

    chord_list = note_to_chord(triad) # odredjivanje koji to akord, s tim da note_to_chord funkcija vraca listu (len(a) = 0 akko nije nasao akord)

    if (len(chord_list) != 0): # ako nadje akord
        chord = chord_list[0].chord

        print("Chord {0} found between {1} - {2}".format(chord, round( start, 1), round(end, 1) ) )

        if("/" in chord): # sklanjanje "/"
            slash_id = chord.find("/")
            chord = chord[0:slash_id]
        else:
            pass

        chord_prog.append(chord)
        durations.append(round(chunk, 1))

        data_chunk = [] # emptying data chunk to analyzed

        start = end            # moving start point to end    
        end = end + interval   # moving end point by 1 interval

        current_time = current_time + chunk   # increasing analyzed_time by analyzed time

        analyze_chunk(interval, fs, data_parts, duration, is_stereo)

    else:
        data_chunk = [] # emptying data chunk to analyzed

        end = end + interval # moving end point by 1 interval

        #print("Nothing found, increasing interval to {0}".format(round(end - start, 1)))

        k = k - n_intervals

        analyze_chunk(interval, fs, data_parts, duration, is_stereo) 


# glavna funkcija
def find_chord_progression(starting_interval, fs, data, is_stereo = True):

    duration = round(len(data) / fs)   # duzina uzorka (s)
    print("Duration is: ", duration)

    n_parts = duration / starting_interval
   
    if (n_parts % 2 == 0.5): # specijalni slucaj (npr 22.5 treba da ide na 23 a ne na 22)
        n_parts = round(n_parts + 0.5)
    else:
        n_parts = round(n_parts) # broj delova
    
    data_parts = np.array_split(data, n_parts) # seckanje

    a = analyze_chunk(starting_interval, fs, data_parts, duration, is_stereo)

# funkcija koja sorta po zadatom nizu (u mom slucaju po hromatskoj skali)
def reference_sort(arr, ref_arr):
    for i in range (0, len(arr) - 1):
        for j in range(i+1, len(arr)):
            index_i = ref_arr.index(arr[i])
            index_j = ref_arr.index(arr[j])

            if (index_i > index_j):
                temp = arr[i]
                arr[i] = arr[j]
                arr[j] = temp
    return arr

# funkcija koja pretvara frekvenciju [Hz] u notu
def get_note(freq):
    A4 = 440
    C0 = A4*pow(2, -4.75)

    try:
        h = round(12*log2(freq/C0))
        octave = h // 12
        n = h % 12
        return chrom_scale[n] #+ str(octave)
    except:
        return "None"

# trazenje nota u jednom isecku
def find_all_notes(w_half_abs, freq_half_hz):
    notes = []
    w_sorted = np.sort(w_half_abs)[::-1]

    for i in range(0, len(w_sorted)):
        # uzimamo vrednost iz sorted array-a
        value = w_sorted[i]

        # trazimo index tog elementa u nesortanom arrayu
        id = np.where(w_half_abs == value)

        # trazimo frekvenciju u array frekvencija
        freq = freq_half_hz[id]

        # konvertujem frekvenciju u notu
        note = get_note(freq)

        # trazi se nota, ako se nadje vec je tu,super, ako ne dodamo je na listu
        try:
            id = notes.index(note)
        except:
            notes.append(note)

    return notes;
    
def do_fft(fs, data, is_stereo):
    # stereo u mono
    if (is_stereo):
        data = np.mean(data, axis=1)

    w = np.fft.fft(data)
    freqs = np.fft.fftfreq(len(w))

    # zbog simetricnosti deli se na 2 i uzima pozitivan deo
    w_half = np.array_split(w , 2)
    freqs_half = np.array_split(freqs, 2)

    w_half_abs = abs(w_half[0])
    freq_half_hz = abs(freqs_half[0] * fs)

    return [w_half_abs, freq_half_hz]

def main():
    t1 = time.time()

    address = "F:\\Skola\\Projekat\\AmCGG.wav" # adresa fajla (.wav format)
    fs, data = wavfile.read(address)
    starting_interval = 0.1 # sekundi
    is_stereo = False

    find_chord_progression(starting_interval, fs, data, is_stereo)

    print("Raw: ",chord_prog, "\n there is ", len(chord_prog))
    print("Durations: ",durations, "\n there is ", len(durations))

    print()
    simplify()

    print("SImplified chords: ",chord_prog_simple)
    print("Simplified durations:", durations_simple)

    print("\nChord progression ( with durations ) before correction is: ")
    output_results()

    print("\nMaking corrections...")
    correction(starting_interval)

    print("\nGetting key... ")
    key_id = get_key()

    print("Chord progression ( with durations ) after correction is as following:")
    output_results(key_id)

    find_ccp(key_id)
    
    t2 = time.time()
    t = t2 - t1
    print("\nTime elapsed: ", round(t, 2), "s")
    

if __name__ == '__main__':
    main()
