from scipy.io import wavfile
import numpy as np
#import matplotlib.pyplot as plt
from math import log2, pow
from pychord import note_to_chord, Chord
import time
import csv
import glob

# globalne promenljive
chrom_scale_sharp = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B" ]
chrom_scale_flat = ["C", "Db", "D", "Eb", "E", "F", "Gb", "G", "Ab", "A", "Bb", "B" ]

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
n_matches_in_every_key = []
durations = []
roman_index_prog = []

k = 0
data_chunk = []
current_time = 0
start = 0
end = 0
duration = 0

once = True
found_ccp = False

def clear_global_vars():
  global chord_prog,n_matches_in_every_key,duration,roman_index_prog,k,data_chunk,current_time,start,end,duration,once,found_ccp

  chord_prog.clear()
  n_matches_in_every_key.clear()
  durations.clear()
  roman_index_prog.clear()

  k = 0
  data_chunk = []
  current_time = 0
  start = 0
  end = 0
  duration = 0

  once = True
  found_ccp = False


def check_results(results, results_real):
  def extend(chords,durations):
    chords_extended = []
    durations_extended = []

    for i in range(0, len(durations)):
      n = round(float(durations[i]) / 0.1)

      j = 0
      for j in range (0,n):
        chords_extended.append(chords[i])
        durations_extended.append("0.1")
  
    return (chords_extended, durations_extended)
  # storing chords and durations that program found in the analyzed file
  
  my_chords, my_durations = extend(results[0], results[1])
  i = 0

  # storing actual chords and durations of the analyzed file
  real_chords, real_durations = extend(results_real[0], results_real[1]) 
  j = 0

  # current time is left border of chunk being checked and current_time_r is right
  current_time = 0
  current_time_r = float(real_durations[j])

  # variables to store succesful percentage
  total_percentage = 0
  percentage = 0

  # running through chords that are found
  for m in range(0, len(my_chords)):
    if (current_time < current_time_r):
      if (my_chords[i] == real_chords[j]):
        print("{} Matching {}".format(my_chords[i], real_chords[j]))

        current_time = current_time + float( my_durations[i])

        # calculating percentage
        percentage = round(float( my_durations[i]) / duration * 100, 2)
        total_percentage = total_percentage + percentage
        print("Total percentage increased by ",percentage )

        i = i + 1
      else: # If my chord doesnt match actual chords check if some of its tone do

        print("{} Doesn't match {}".format(my_chords[i], real_chords[j]) )

        try: # if chord isnt none
          my_chord = Chord(my_chords[i])
          real_chord = Chord(real_chords[j])

          my_notes = reference_sort(my_chord.components())
          real_notes = reference_sort(real_chord.components())

          
          m = 0
          for note in my_notes:
            if (note == real_notes[m]):
              percentage = round(float( my_durations[i]) / duration * 100 / len(my_notes), 2)
              total_percentage = total_percentage + percentage
              print("Chord isnt right but some notes are, percentage increased by: ",percentage)
            m = m + 1
        except:
          pass

        current_time = current_time + float(my_durations[i])

        i = i + 1
    else:
      if(j < len(real_durations)-1):
        j = j + 1
      
        current_time_r = current_time_r + float(real_durations[j])

        if (my_chords[i] == real_chords[j]):
          print("{} Matching {}".format(my_chords[i], real_chords[j]))

          current_time = current_time + float( my_durations[i])

          # calculating percentage
          percentage = round(float( my_durations[i]) / duration * 100, 2)
          total_percentage = total_percentage + percentage
          print("Total percentage increased by ",percentage )
          
          i = i + 1
        else:
          print("{} Doesn't match {}".format(my_chords[i], real_chords[j]) )

          try:
            my_chord = Chord(my_chords[i])
            real_chord = Chord(real_chords[j])

            my_notes = reference_sort(my_chord.components())
            real_notes = reference_sort(real_chord.components())

            
            m = 0
            for note in my_notes:
              if (note == real_notes[m]):
                percentage = round(float( my_durations[i]) / duration * 100 / len(my_notes), 2)
                total_percentage = total_percentage + percentage
                print("Chord isnt right but some notes are, percentage increased by: ",percentage)
              m = m + 1
          except:
            pass

          current_time = current_time + float(my_durations[i])

          i = i + 1
      
    #print(current_time , ' ' , current_time_r)
  print()
  return total_percentage

def read_results(file_name, key_id = "None"):
  chords = []
  durations = []
  roman_indices = []

  print(f"\nOpening {file_name}\n")
  with open(file_name, newline='') as csvfile:
    # print("Current file ", file_name)
    reader = csv.reader(csvfile, delimiter=' ')

    if (key_id == "None"):
      for row in reader:
        #print("Current row: ",row)
        if (len(row) > 0):
          chords.append(row[0])
          durations.append(row[1])
        
      return [chords,durations]
    else:
      for row in reader:
        #print("Current row: ",row)
        if (len(row) > 0):
          chords.append(row[0])
          roman_indices.append(row[1])
        durations.append(row[2])
      return [chords, roman_indices, durations]
    

def save_results(name, results_address, key_id = "None"):
    file_name = "{0}{1}.csv".format(results_address, name)
    #file_name = "{0}.csv".format(name)
    with open(file_name, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=' ')
        j = 0
        for chord in chord_prog:           
            writer.writerow([chord, str(round(durations[j], 1))])
            j = j + 1

   
def simplify ():
    global chord_prog, durations, durations_simple
    i = 0
    j = 0
    chord_prog_simple = []
    durations_simple = []

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
    chord_prog = chord_prog_simple
    durations = durations_simple

def output_results (key_id = "None"):
    i = 0
    j = 0
    for chord in chord_prog:
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
                print (chord + " " + roman_index(i) + " " + str(round(durations[j], 1)) + "s")
                j = j + 1
            else:
                print (chord + " out of key " + str(round(durations[j], 1)) + "s")
                j = j + 1
        else:
            print (chord + " " + str(round(durations[j], 1)) + "s")
            j = j + 1

        if (chord_prog.index(chord) == len(chord_prog) - 1):
            print()

# funkcija koja pretvara rimski broj u akord
def ccp_to_chord (ccp, key_id):
    r_indexes = ["I", "ii", "iii", "IV", "V", "vi", "VII"] # matrica sa rimskim indexima
    
    print("Chords: ", end = " ")

    cp = []
    for index in ccp:
        id = r_indexes.index(index)  
        print(chords_in_every_key[key_id][id], end = " ")
        cp.append(chords_in_every_key[key_id][id])
        
    print("\n")
    return cp

# funkcija koja proverava da li se pojavljuje common chord proggresion
def find_ccp (key_id):
    global found_ccp

    not_found = True
    
    i = 0
    cp = "None"

    print("Roman index proggresion: {}".format(roman_index_prog))

    while (not_found):
        if (roman_index_prog == common_chord_progressions[i]):
            not_found = False
            found_ccp = True
            print ("\nPossible common chord progression found: ", common_chord_progressions[i], "\n")
            cp = ccp_to_chord (common_chord_progressions[i], key_id)

        if (i == len(common_chord_progressions) - 1):
            break

        i = i + 1

    return (common_chord_progressions[i],cp)
    
# funkcija koja prebacuje random akorde koji se pojavljuju jako kratko (iste duzine kao i zadat interval)
# u prethodni poznat akord  (sto je vrlo verovatno i tacno)
def correction(interval):
    i = 0
    for duration in durations:
        if (duration == interval and i != 0): 
            if (chord_prog[i] != chord_prog[i - 1]):
              print("Changed ", chord_prog[i], " to ", chord_prog[i - 1])
              chord_prog[i] = chord_prog[i - 1]
            # roman_index_prog[i] = roman_index_prog[i - 1]
        i = i + 1
        if (i == len (durations) - 1):
            if (chord_prog[i] == "None"):
                print("Changed ", chord_prog[i], " to ", chord_prog[i - 1])
                chord_prog[i] = chord_prog[i - 1]

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

    for note in chrom_scale_sharp:
        check_chord_matching(chord_prog, chords_in_every_key[i])
        i = i + 1

    id = np.argmax(n_matches_in_every_key)

    print("We are in the key of ", chrom_scale_sharp[id], "\n")

    return id

def analyze_chunk(interval, fs, data_parts, duration, T1): # rekurzivna funkcija

    global current_time, k, data_chunk # current time, current position in data_parts array , data chunk to be analyzed 
    global start, end # starting and ending position of chunk to be analyzed
    global once  # switch
    global chord_prog, durations # list to store chords that are found and list to store durations

    #T2 = time.time()
    #if ((T2 - T1) > 60):
      #return "Failed"

    if (current_time >= duration or k == len(data_parts)): # basic if
        return "Done"
    
    if (once): # running once, to make starting interval
        end = start + interval
        once = False

    chunk = end - start # deo u sekundi

    n_intervals = round(chunk / interval)

    if (n_intervals > 1):
        for i in range (0, n_intervals):
            if (k != len(data_parts)):
                data_chunk = np.append(data_chunk, data_parts[k])
                k = k + 1
            else:
                print("Nothing found beetwen {0} and {1}".format(round(start, 1), round(end, 1)))
                chord_prog.append("None")
                durations.append(round(chunk, 1) - interval)
                return "Done"
    else:
        data_chunk = data_parts[k]
        k = k + 1
        

    fft_and_freq = do_fft(fs, data_chunk) # kreiranje matrice sa fft vrednostima i odgovarajucim frekvencijama

    notes = find_all_notes(fft_and_freq[0], fft_and_freq[1]) # trazenje svih nota, sortiranih od one koja se cuje najvise

    triad_notes = []
    l = 0
    for note in notes:
        if (note != "None" and l < 3):
            triad_notes.append(note)
            l = l + 1

    triad = reference_sort(triad_notes) # pravljenje trikorda od 3 najjaca tona, sortirana po hromatskoj skali

    chord_list = note_to_chord(triad) # odredjivanje koji to akord, s tim da note_to_chord funkcija vraca listu (len(a) = 0 akko nije nasao akord)

    if (len(chord_list) != 0): # ako nadje akord
        chord = chord_list[0].chord

        print("Chord {0} found between {1} - {2}".format(chord, round( start, 1), round(end, 1) ) )
        #print("Notes found are ", triad)

        if("/" in chord): # sklanjanje "/"
            slash_id = chord.find("/")
            chord = chord[0:slash_id]
        else:
            pass

        current_time = current_time + chunk
        
        chord_prog.append(chord)
        durations.append(round(chunk, 1))

        data_chunk = [] # emptying data chunk to analyzed

        start = end            # moving start point to end    
        end = end + interval   # moving end point by 1 interval

           # increasing analyzed_time by analyzed time

        analyze_chunk(interval, fs, data_parts, duration, T1)

    else:
        data_chunk = [] # emptying data chunk to analyzed

        end = end + interval # moving end point by 1 interval

        #print("Nothing found, increasing interval to {0}".format(round(end - start, 1)))

        k = k - n_intervals

        analyze_chunk(interval, fs, data_parts, duration, T1) 

# glavna funkcija
def find_chord_progression(starting_interval, fs, data, T1):
    global duration
    duration = round(len(data) / fs, 1)   # duzina uzorka (s)
    print("Duration is: {0}s".format(duration))

    n_parts = duration / starting_interval
   
    if (n_parts % 2 == 0.5): # specijalni slucaj (npr 22.5 treba da ide na 23 a ne na 22)
        n_parts = round(n_parts + 0.5)
    else:
        n_parts = round(n_parts) # broj delova
    
    data_parts = np.array_split(data, n_parts) # seckanje

    a = analyze_chunk(starting_interval, fs, data_parts, duration, T1)

# funkcija koja sorta po zadatom nizu (u mom slucaju po hromatskoj skali)
def reference_sort(arr):
    for i in range (0, len(arr) - 1):

        for j in range(i+1, len(arr)):
          if ('#' in arr[i]):
            index_i = chrom_scale_sharp.index(arr[i])
            
          else:
            index_i = chrom_scale_flat.index(arr[i])

          if ('#' in arr[j]):
            index_j = chrom_scale_sharp.index(arr[j])
          else:
            index_j = chrom_scale_flat.index(arr[j])

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
        #octave = h // 12
        n = h % 12
        return chrom_scale_sharp[n] #+ str(octave)
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
    
def do_fft(fs, data):
    # stereo u mono
    shape = np.shape(data)
    if (len(shape) > 1):
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

    wav_files = glob.glob("Wavfiles/*.wav")
    #real_results = glob.glob("Real/*.csv")

    for wav in wav_files:
      print("Current file: ",wav)
      
      """
      try:
        fs, data = wavfile.read(wav)
        starting_interval = 0.1 # sekundi

        T1 = time.time()
        find_chord_progression(starting_interval, fs, data,  T1)

        print("\nSimplifying...")
        simplify()

        print("\nChord progression ( with durations ) before correction is: ")
        output_results()
        save_results(wav[9:(len(wav) - 4)], "Raw/")

        print("\nMaking corrections...")
        correction(starting_interval)

        print("\nGetting key... ")
        key_id = get_key()

        print("\nSimplifying...")
        simplify()

        print("\nChord progression ( with durations ) after correction is as following:")
        output_results(key_id)
        save_results("{0}_corrected".format(wav[9:(len(wav) - 4)]), "Corrected/", key_id)

        print("\nChecking for common chord progression...")
        my_ccp = find_ccp(key_id)
        
        
        my_results = read_results("Raw/{0}.csv".format(wav[9:(len(wav) - 4)]))
        my_corrected_results = read_results("Corrected/{0}_corrected.csv".format(wav[9:(len(wav) - 4)]))
        real_results = read_results("Real/{0}_real.csv".format(wav[9:(len(wav) - 4)]))
        
        print("Calculating percentage...")
        percentage = check_results(my_results, real_results)
        print("Before correcttion, successful percentage is {0}%\n".format(round(percentage,2)))

        corrected_percentage = check_results(my_corrected_results, real_results)
        print("After correction, successful percentage is {0}%\n".format(round(corrected_percentage,2)))

        with open("Results/{0}.txt".format(wav[9:(len(wav) - 4)]), 'w') as txt:
            txt.write("Successful percentage is {}% \n".format(corrected_percentage))
            if(found_ccp):
              txt.write("Found common chord progression: {}\n".format(str(my_ccp[0])))
              txt.write("Possible chords: {}".format(str(my_ccp[1])))
        

        clear_global_vars()      
      
      except ValueError:
        print("\nCant read file!\n")
        clear_global_vars()

      except TimeoutError:
        print("\nToo much time passed!\n")

      except:
        print("\nSomething went wrong!\n")

      finally:
        print("\nDone!\n")
      """

      fs, data = wavfile.read(wav)
      starting_interval = 0.1 # sekundi

      T1 = time.time()
      find_chord_progression(starting_interval, fs, data,  T1)

      print("\nSimplifying...")
      simplify()

      print("\nChord progression ( with durations ) before correction is: ")
      output_results()
      save_results(wav[9:(len(wav) - 4)], "Raw/")

      print("\nMaking corrections...")
      correction(starting_interval)

      print("\nGetting key... ")
      key_id = get_key()

      print("\nSimplifying...")
      simplify()

      print("\nChord progression ( with durations ) after correction is as following:")
      output_results(key_id)
      save_results("{0}_corrected".format(wav[9:(len(wav) - 4)]), "Corrected/", key_id)

      print("\nChecking for common chord progression...")
      my_ccp = find_ccp(key_id)
      
             
    t2 = time.time()
    t = t2 - t1
    print("\nTime elapsed: ", round(t, 2), "s")
    

if __name__ == '__main__':
    main()