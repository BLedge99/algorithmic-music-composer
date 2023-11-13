from Data_Translation import MidiToData


class Note:

    def __init__(self, on_time=0, pitch=0, duration=0, channel=0, loudness=0, tied_note=0):
        self.on_time = on_time
        self.pitch = pitch
        self.duration = duration
        self.channel = channel
        self.loudness = loudness
        self.tied_note = tied_note


class Beat:

    def __init__(self, note_list=[], destination_notes=[], is_signature=False, phrase_cadence_offset=0, character=0,
                 SPEAC=[]):
        self.note_list = note_list
        self.notes = []
        self.setNoteList()
        self.destination_notes = destination_notes
        self.is_signature = is_signature
        self.phrase_cadence_offset = phrase_cadence_offset
        self.character = character
        self.SPEAC = SPEAC

    def setNoteList(self):
        for note in self.note_list:
            self.notes.append(note)

    def addNote(self, note):
        self.note_list.append(note)

    def setSPEAC(self, SPEAC):
        self.SPEAC = SPEAC

    def orderNotes(self):
        for note in self.note_list:
            # order notes
            pass

    def setDestinations(self, destinations):
        self.destination_notes = destinations


class Phrase:

    def __init__(self):
        pass


class Disassembler:

    def __init__(self, midi_file):
        self.beats = {}
        self.beat_objs = []
        self.mido = MidiToData(midi_file)
        self.mid = self.mido.mid
        self.ticks = self.mid.ticks_per_beat
        self.notes = self.mido.tuple_list
        self.beat_interval = 0
        self.tempo_marking = 0
        self.beat_disassemble()
        self.to_beats()
        self.next_beats()

    def midi_tempo_to_bpm(self, tempo):
        bpm = tempo / 1000000
        bpm = 60 / bpm
        return bpm

    def find_tempo_changes(self):
        tempo_changes = []
        for channel in self.mid.tracks:
            time = 0
            for message in channel:
                time += message.time
                if message.type == "set_tempo":
                    tempo_changes.append((message.tempo, self.midi_tempo_to_bpm(message.tempo), time))
        return tempo_changes

    def normalised_on_time(self, note):
        on_time = note[0]
        rem = on_time % self.ticks
        if rem > (self.ticks / 4) * 3:
            #norm_time = on_time // self.ticks
            #norm_time += 1
            #norm_time *= self.ticks
            norm_time = on_time
        elif rem < self.ticks / 4:
            norm_time = on_time // self.ticks
            norm_time *= self.ticks
        else:
            norm_time = on_time #// self.ticks
            #norm_time *= self.ticks
            #norm_time += self.ticks / 2
        return norm_time, note[1], note[2], note[3], note[4]

    def beat_disassemble(self):
        for note in self.notes:  # check that note occurs at a reasonable time
            if note[2] != 0: #remove seemingly unintentional notes of duration 0 that often are duplicate entries of a note of the same pitch at the same time (with a duration > 0)
                norm_note = self.normalised_on_time(note)
                if self.beats.get(norm_note[3], "Not") == "Not":
                    self.beats[norm_note[3]] = {}
                if self.beats.get(norm_note[3]).get(norm_note[0]):
                    self.beats[norm_note[3]][norm_note[0]].append(norm_note)
                else:
                    beat = [norm_note]
                    self.beats[norm_note[3]][norm_note[0]] = beat

    def to_beats(self):
        for channel in self.beats:
            for beat in self.beats[channel]:
                notes = self.beats[channel][beat]
                self.beat_objs.append(Beat(notes))

    def next_beats(self):
        for x in range(len(self.beat_objs) - 1):
            self.beat_objs[x].setDestinations(self.beat_objs[x + 1].notes)
        self.beat_objs[-1].setDestinations([0])

        # add note to beat object, add beat object to beat list

