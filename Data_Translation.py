from mido import MidiFile


class MidiToData:

        def __init__(self, m_path):
            self.m_path = m_path
            self.mid = MidiFile(m_path, clip=True)
            #self.data = {}
            self.track_list = self.get_track_list()
            self.tuple_list = []
            self.generate_tuple_list()

        def get_track_list(self):
            track_list = []
            for channel in self.mid.tracks:
                track_list.append(MidiTrack(channel))
            return track_list

        def generate_tuple_list(self):
            channel_number = 0
            for channel in self.track_list:
                if channel.track_type == 1:
                    channel_number += 1
                    self.generate_tuple_list_for_representation1(channel, channel_number)
                elif channel.track_type == 2:
                    channel_number += 1
                    self.generate_tuple_list_for_representation2(channel, channel_number)

        def generate_tuple_list_for_representation1(self, channel, channel_number):
            current_time = 0
            current_note = 0
            event_dict = {}
            for event in channel.track:
                if event.type == 'note_on' or event.type == 'note_off':
                    current_note = event.note
                    current_time += event.time
                note_counter = {}
                if event.type == 'note_on':
                    if event_dict.get(current_note,
                                      "nothing there bud") != "nothing there bud":  # if there is more than one note_on for a single pitch in a row, count how many there are in a row
                        if note_counter.get(current_note, "Hello") == "Hello":
                            note_counter[current_note] = 1
                        else:
                            note_counter[current_note] += 1
                    else:
                        event_dict[current_note] = [current_time, current_note, 0, channel_number, event.velocity]
                elif event.type == 'note_off':
                    if event_dict.get(current_note,
                                      "nothing there bud") == "nothing there bud":  # if there is a note off that appears while there is nothing in the event dictionary send error msg
                        #print("Error, incorrectly formatted midi file for channel", channel.track.name, "for note", current_note, "at time ", current_time, note_counter)
                        print(" ")
                    elif note_counter.get(current_note,
                                        "Hello") != "Hello":  # code for counting down the note_counter upon seeing the first note_off
                        if note_counter[current_note] == 1:
                            note_counter.pop(current_note)
                        else:
                            note_counter[current_note] -= 1
                    else:
                        event_dict[current_note][2] = event.time
                        note_tuple = event_dict[current_note]
                        event_dict.pop(current_note)
                        note_tuple = tuple(note_tuple)
                        self.tuple_list.append(note_tuple)

        def generate_tuple_list_for_representation2(self, channel, channel_number):
            current_time = 0
            event_dict = {}
            for event in channel.track:
                if event.type == 'note_on':
                    current_note = event.note
                    if event_dict.get(current_note, "nothing there bud") != "nothing there bud":
                        if event.velocity > 0:
                            print("MIDI format incorrectly handled, please contact the program provider for assistance")
                        else:
                            event_dict[current_note][2] = event.time
                            note_tuple = event_dict[current_note]
                            event_dict.pop(current_note)
                            note_tuple = tuple(note_tuple)
                            self.tuple_list.append(note_tuple)
                    else:
                        event_dict[current_note] = [current_time, current_note, 0, channel_number, event.velocity]
                current_time += event.time

        def test_track(self, channel_num):
            channel = self.track_list[channel_num]
            for event in channel.track:
                print(event)


class MidiTrack:

        def __init__(self, channel):
            self.track = channel
            self.track_type = 100
            self.get_track_type()

        def get_track_type(self):
            # Find type of track (meta data, song info, notes with representation 1, notes with representation 2 etc etc)
            counter1 = 0
            counter2 = 0
            for event in self.track:
                if event.type == 'note_on':
                    counter1 += 1
                    counter2 += 1
                if event.type == 'note_off':
                    counter1 += 1
                    counter2 -= 1
            if counter1 == 0:
                self.track_type = 0
            else:
                if counter2 == 0:
                    self.track_type = 1
                else:
                    self.track_type = 2