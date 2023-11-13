import random

from mido import MidiFile, MidiTrack, Message

from Data_Translation import MidiToData
from Dissassembly import Disassembler
from patternmatching import differential_sig, summational_sig, serial_sig, parallel_sig, chord_sig, interval_test, \
    find_intervals, find_direction


def get_patterns(song_notes, pattern_length,
                 clocks_per_beat):  # pass a list of lists of tuples with each list of tuples being all the notes in a channel of a song
    bar_times = []
    pattern_list = []
    n = pattern_length / 4
    for x in range(0, song_notes[-1][0] + 4 * clocks_per_beat, 4 * clocks_per_beat):
        bar_times.append(x)
    #for channel in song_notes:
    #    x = 0
    #    patterns = []
    #    for note in channel:
    #        patterns[x] = []
    #        y = bar_times[x]
    #        while note[0] < n * bar_times[x + 1]:
    #            patterns[x].append(note)
    #        pattern_list.append(patterns)
    for n in range(len(bar_times)):
        pattern_list.append([])
    channels = song_notes[-1][3]
    for i in range(1,channels+1,1):
        x = 0
        for note in song_notes:
            if note[3] == i:
                if note[0] < bar_times[x + 1]:
                    pattern_list[x].append(note)
                else:
                    x += 1
                    pattern_list[x].append(note)
    return pattern_list


def get_data(midi_files, pattern_length):
    midi_patterns = []
    temp_patterns = []
    for x in range(len(midi_files)):
        notes = []
        data = Disassembler(midi_files[x])
        for beat in data.beat_objs:
            for note_list in beat.notes:
                notes.append(note_list)
        patterns = get_patterns(notes, pattern_length, data.ticks)
        temp_patterns.append(patterns)
    for pattern_list in temp_patterns:
        for pattern in pattern_list:
            midi_patterns.append(pattern)
    return midi_patterns
                    #pattern_list.append(note)
    #return pattern_list
    #return data


def get_all_notes(data):
    pattern_list = []
    for song in data:
        for beat in song.beat_objs:
            for note_list in beat.notes:
                for note in note_list:
                    pattern_list.append(note)
    return pattern_list


def identify(pattern_list, threshold=20, benchmark=60):
    scores = []
    interval_sigs = []
    direction_sigs = []
    for x in range(len(pattern_list)):
        for y in range(len(pattern_list)):
            if x != y:
                if len(pattern_list[x]) == len(pattern_list[y]):
                    differential = differential_sig(pattern_list[x], pattern_list[y], benchmark)
                    summational = summational_sig(pattern_list[x], pattern_list[y], benchmark)
                    serial = serial_sig(pattern_list[x], pattern_list[y])
                    parallel = parallel_sig(pattern_list[x], pattern_list[y])
                    chord = chord_sig(pattern_list[x], pattern_list[y])
                    scores.append([pattern_list[x], pattern_list[y], differential, summational, serial, parallel, chord])
                    if summational > threshold:
                        interval_sigs.append(find_intervals(pattern_list[x]))
                        direction_sigs.append(find_direction(pattern_list[x]))
    return interval_sigs, direction_sigs


def recombine(key, sig_list, structure='ABABCBA'):
    time = 150
    structure = structure
    initial_pitch = 60
    mid = MidiFile()
    track = MidiTrack()
    mid.tracks.append(track)
    sig_dict = get_sig_dict(sig_list, structure)
    msgs = []
    for letter in structure:
        for x in range(len(sig_dict[letter][0])):
            pitch = initial_pitch + sig_dict[letter][0][x] * sig_dict[letter][1][x]
            print(pitch)
            msgs.append(Message('note_on', note=int(pitch), velocity=64, time=time))
            msgs.append(Message('note_off', note=int(pitch), velocity=64, time=time))
            print(msgs)
    for msg in msgs:
        track.append(msg)
    mid.save('music/' + "untiled" + '.mid')
    return mid


def get_sig_dict(sig_list, structure):
    sig_dict = {}
    structure_letters = ''.join(set(structure))
    rand_sigs = []
    for n in range(len(structure_letters)):
        index = random.randint(0, len(sig_list[0]))
        rand_sigs.append((sig_list[0][index], sig_list[1][index]))
    for x in range(len(structure_letters)):
        if sig_dict.get(structure_letters[x], "Hello") == "Hello":
            sig_dict[structure_letters[x]] = rand_sigs[x]
    return sig_dict


def save_midi(midi_file, file_path):
    midi_file.save(file_path)


def generate_sigs(midi_files, pattern_length=16, threshold=60, benchmark=20):
    patterns = get_data(midi_files, pattern_length)
    sigs = identify(patterns, threshold, benchmark)
    return sigs


def generate_song(signatures, key=60, structure='ABABCDA'):
    midi = recombine(key, signatures, structure)
    return midi

def save_song(midi_file, file_path):
    midi_file.save(file_path[0])