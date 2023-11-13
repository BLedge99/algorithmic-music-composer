from math import gcd


def interval_test(pattern1, pattern2):
    if len(pattern1) != len(pattern2):
        print("Invalid patterns provided, patterns must be of the same length")
    else:
        count = 0
        p_length = len(pattern1)
        intervals1 = find_intervals(pattern1)
        intervals2 = find_intervals(pattern2)
        return percentage_similarity(intervals1, intervals2)


def direction_test(pattern1, pattern2):
    if len(pattern1) != len(pattern2):
        print("Invalid patterns provided, patterns must be of the same length")
    else:
        directions1 = find_direction(pattern1)
        directions2 = find_direction(pattern2)
        return percentage_similarity(directions1, directions2)


def rhythm_test(pattern1, pattern2):
    # don't test for len as may be differing number of beats with similar but not identical rhythm that passes some
    # threshold
    relative_rhythm1 = find_rhythm(pattern1)
    relative_rhythm2 = find_rhythm(pattern2)
    return percentage_similarity(relative_rhythm1, relative_rhythm2)


def percentage_similarity(list1, list2):
    if len(list1) == len(list2):
        count = 0
        for x in range(len(list1)):
            if list1[x] is list2[x]:
                count += 1
        return count / len(list1) * 100
    else:
        print("Invalid lists provided, lists must be of the same length")
        return 0


# tracks whether the next note in the pattern is of greater or lesser pitch
def find_direction_old(pattern):
    directions = []
    last_pitch = -5000
    for note in pattern:
        if last_pitch != -5000:
            if note.pitch > last_pitch:
                directions.append(1)
            elif note.pitch < last_pitch:
                directions.append(-1)
            else:
                directions.append(0)
        last_pitch = note.pitch
    return directions

def find_direction(pattern):
    directions = []
    last_pitch = -5000
    for note in pattern:
        if last_pitch != -5000:
            if note[1] > last_pitch:
                directions.append(1)
            elif note[1] < last_pitch:
                directions.append(-1)
            else:
                directions.append(0)
        last_pitch = note[1]
    return directions



def find_intervals_old(pattern):
    pattern_intervals = []
    interval = 0
    for note in pattern:
        note_pitch = note.pitch
        if interval == 0:
            interval = note_pitch
        else:
            interval = abs(interval - note_pitch)
            pattern_intervals.append(interval)
    return pattern_intervals

def find_intervals(pattern):
    pattern_intervals = []
    last_pitch = 0
    for note in pattern:
        note_pitch = note[1]
        if last_pitch == 0:
            last_pitch = note_pitch
        else:
            interval = abs(last_pitch - note_pitch)
            pattern_intervals.append(interval)
    return pattern_intervals


def find_rhythm(pattern):
    durations = []
    for note in pattern:
        durations.append(note.duration)
    durations = lowest_common_multiple(durations)
    return durations


def lowest_common_multiple(factors):
    facs = []
    hcf = find_hcf(factors)
    for num in factors:
        facs.append(num/hcf)
    return facs


def find_hcf(a):
    #x = reduce(gcd, a)
    x = 0
    return x


def summational_sig(pattern1, pattern2, benchmark):
    interval_score = interval_test(pattern1, pattern2)
    directional_score = direction_test(pattern1, pattern2)
    score = (interval_score - benchmark) + (directional_score - benchmark)
    return score


def serial_sig(pattern1, pattern2):
    interval_score = interval_test(pattern1, pattern2)
    directional_score = direction_test(pattern1, pattern2)
    return interval_score + directional_score == 200


def parallel_sig(pattern1, pattern2):
    interval_score = interval_test(pattern1, pattern2)
    directional_score = direction_test(pattern1, pattern2)
    return interval_score == 100 or directional_score == 100


def differential_sig(pattern1, pattern2, benchmark):
    interval_score = interval_test(pattern1, pattern2)
    directional_score = direction_test(pattern1, pattern2)
    int_bench = 0
    dir_bench = 0
    if interval_score < benchmark:
        int_bench = abs(benchmark - interval_score)
    if directional_score < benchmark:
        dir_bench = abs(benchmark - directional_score)
    return int_bench + dir_bench


def chord_sig(pattern1,pattern2):
    pattern_1_notes = PitchAnalyser(pattern1).note_list
    pattern_2_notes = PitchAnalyser(pattern2).note_list
    return percentage_similarity(pattern_1_notes,pattern_2_notes)


class PitchAnalyser:

    def __init__(self, input_notes):
        self.input_notes = input_notes
        self.notes = {}
        self.lookup = {}
        self.maj_chords = {}
        self.min_chords = {}
        self.note_list = []
        self.set_notes()
        self.set_lookup()
        self.set_chords()
        self.assign_notes()

    def set_notes(self):
        c = [x for x in range(0, 132, 12)]
        self.notes['C'] = c
        db = [x for x in range(1,132,12)]
        self.notes['Db C#'] = db
        d = [x for x in range(2,132,12)]
        self.notes['D'] = d
        eb = [x for x in range(3,132,12)]
        self.notes['Eb D#'] = eb
        e = [x for x in range(4,132,12)]
        self.notes['E'] = e
        f = [x for x in range(5,132,12)]
        self.notes['F'] = f
        gb = [x for x in range(6,132,12)]
        self.notes['Gb F#'] = gb
        g = [x for x in range(7,132,12)]
        self.notes['G'] = g
        ab = [x for x in range(8,132,12)]
        self.notes['Ab G#'] = ab
        a = [x for x in range(9,132,12)]
        self.notes['A'] = a
        bb = [x for x in range(10,132,12)]
        self.notes['Bb A#'] = bb
        b = [x for x in range(11,132,12)]
        self.notes['B'] = b


    def set_lookup(self):
        for x in range(132):
            for key,value in self.notes.items():
                if x in value:
                    self.lookup[x] = key


    def set_chords(self):
        for key, pitch in self.notes.items():
            self.maj_chords[key] = [[],[],[]]
            self.min_chords[key] = [[],[],[]]
            major_thirds = [x + 4 for x in pitch]
            major_fiths = [x + 7 for x in pitch]
            minor_thirds = [x + 3 for x in pitch]
            minor_fiths = [x + 7 for x in pitch]
            self.maj_chords[key][0] = pitch
            self.maj_chords[key][1] = major_thirds
            self.maj_chords[key][2] = major_fiths
            self.min_chords[key][0] = pitch
            self.min_chords[key][1] = minor_thirds
            self.min_chords[key][2] = minor_fiths


    def assign_notes(self):
        for note in self.input_notes:
            pitch = note[1]
            self.note_list.append(self.lookup[pitch])

    def find_chord(self, key_sig):
        chords = {}
        if key_sig == 'Major':
            chords = self.get_chord_list(self.maj_chords)
        if key_sig == 'Minor':
            chords = self.get_chord_list(self.min_chords)
        return chords

    def get_chord_list(self, chord_dict):
        chords = {}
        for key, pitches in chord_dict.items():
            if chords.get(key, "Hello") == 'Hello':
                chords[key] = 0
            for note_pitch in self.input_notes:
                current_pitch = note_pitch[1]
                print(current_pitch)
                for pitch in pitches[0]:
                    if current_pitch == pitch:
                        print(pitch)
                        print(key)
                        chords[key] += 2
                for pitch in pitches[1]:
                    if current_pitch == pitch:
                        print(pitch)
                        print(key)
                        chords[key] += 1
                for pitch in pitches[2]:
                    if current_pitch == pitch:
                        print(pitch)
                        print(key)
                        chords[key] += 1
        return chords


pitches = PitchAnalyser([(14400, 63, 0, 1, 63), (14400, 63, 137, 1, 63), (14400, 65, 137, 1, 63)])
pitches2 = PitchAnalyser([(15360, 66, 137, 1, 63), (15360, 65, 720, 1, 63)])
#print(chord_sig([(14400, 63, 0, 1, 63), (14400, 65, 137, 1, 63)],[(15360, 66, 137, 1, 63), (15360, 65, 720, 1, 63)]))
#print(pitches.maj_chords)
#print(pitches.find_chord('Major'))
print(serial_sig([(14400, 63, 0, 1, 63), (14400, 65, 137, 1, 63)],[(15360, 66, 137, 1, 63), (15360, 65, 720, 1, 63)]))