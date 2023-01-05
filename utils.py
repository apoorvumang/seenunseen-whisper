import os
import pyvtt

def list_mp3_files(folder):
    # get all files in the folder
    files = os.listdir(folder)
    # filter out all files that are not MP3 files
    mp3_files = [f for f in files if f.endswith('.mp3')]
    return mp3_files

def readLines(fname):
    f = open(fname, 'r')
    lines = []
    for line in f:
        lines.append(line.rstrip())
    f.close()
    return lines

def read_rttm(fname):
    lines = readLines(fname)
    out = []
    for line in lines:
        line = line.split(' ')
        start_time = float(line[3])
        duration = float(line[4])
        speaker = line[7]
        out.append([start_time, duration, speaker])
    return out

def getSpeakerDurations(rttm):
    speaker_dict = {}
    total_runtime = 0
    for line in rttm:
        speaker = line[2]
        duration = line[1]
        total_runtime += duration
        if speaker in speaker_dict:
            speaker_dict[speaker] += duration
        else:
            speaker_dict[speaker] = duration
    for k in speaker_dict.keys():
        speaker_dict[k] /= total_runtime
    return speaker_dict

def replaceRandomSpeakers(rttm):
    speaker_dict = getSpeakerDurations(rttm)
    threshold = 0.1
    unknown_speakers = [k for k in speaker_dict.keys() if speaker_dict[k] < threshold]
    unknown_speaker_tag = 'SPEAKER_UNK'
    for i in range(len(rttm)):
        if rttm[i][2] in unknown_speakers:
            rttm[i][2] = unknown_speaker_tag
    return rttm

def rttmToSecLevelLabels(rttm, max_length = -1):
    if max_length == -1:
        max_length = int(rttm[-1][0] + rttm[-1][1]) + 1000
    labels = [None] * max_length
    for d in rttm:
        low = int(d[0])
        high = int(d[0] + d[1])
        for i in range(low, high+1):
            labels[i] = d[2]
    return labels

def getLikelySpeaker(sec_level_labels, start_sec, end_sec):
    speaker_dict = {}
    if end_sec > len(sec_level_labels):
        end_sec = len(sec_level_labels) - 1
    if start_sec > len(sec_level_labels):
        start_sec = len(sec_level_labels) - 1
    for i in range(start_sec, end_sec + 1):
        label = sec_level_labels[i]
        if label == None:
            continue
        if label in speaker_dict:
            speaker_dict[label] += 1
        else:
            speaker_dict[label] = 1
    sorted_speaker_dict = sorted(speaker_dict.items(), key = lambda x:x[1], reverse=True)
    if len(sorted_speaker_dict) > 0:
        return sorted_speaker_dict[0][0]
    else:
        return 'SPEAKER_UNK'
    
def subsTimeToSeconds(t):
    sec = t.hours*3600 + t.minutes*60 + t.seconds
    if t.milliseconds > 500:
        sec += 1
    return sec

# def isSpeakerAnnotated(text):
#     if text.startswith('[')

def combine_rttm_sub(rttm, sub):
    sec_level_labels = rttmToSecLevelLabels(rttm)
    for i in range(len(sub)):
        start_sec = subsTimeToSeconds(sub[i].start)
        end_sec = subsTimeToSeconds(sub[i].end)
        speaker = getLikelySpeaker(sec_level_labels, start_sec, end_sec)
        sub[i].text = '[' + speaker + ']: ' + sub[i].text
    return sub

def getSpeakerFromText(text):
    return text[1:text.find(']:')]

def getMessageFromText(text):
    return text[text.find(']: ')+3:]

def replaceSpeakerNames(subs):
    # find which one is amit
    is_speaker_amit_dict = {}
    amit_phrases = ['welcome to the seen and the unseen', 
                    'Welcome to The Scene and the Unseen',
                    'welcome to seen unseen',
                    'i am amit varma',
                    'my name is amit varma',
                    'i am your host amit bhadma']
    amit_identity = ''
    found = False
    speakers = set()
    for s in subs:
        text = s.text
        speaker = getSpeakerFromText(text)
        if speaker == 'SPEAKER_UNK':
            continue
        speakers.add(speaker)
        if found == False:
            for ap in amit_phrases:
                if ap.lower() in text.lower():
                    amit_identity = speaker
                    # print(text)
                    found = True
            
    if not found:
        print('amit not found')
        # first non unknown speaker is amit
        for s in subs:
            text = s.text
            speaker = getSpeakerFromText(text)
            if speaker == 'SPEAKER_UNK':
                continue
            else:
                amit_identity = speaker
                break
        
    replace_dict = {}
    replace_dict[amit_identity] = 'Amit Varma'
    replace_dict['SPEAKER_UNK'] = 'Unknown'
    guest_id = 1
    for speaker in speakers:
        if speaker == amit_identity:
            continue
        if len(speakers) > 2:
            replace_dict[speaker] = 'Guest ' + str(guest_id)
            guest_id += 1
        else:
            replace_dict[speaker] = 'Guest'
            
    for i in range(len(subs)):
        text = subs[i].text
        orig_speaker = getSpeakerFromText(text)
        message = getMessageFromText(text)
        new_speaker = replace_dict[orig_speaker]
        subs[i].text = '[' + new_speaker + ']: ' + message
    return subs
      
def getProcessedSubs(mp3_basename):
    rttm_fname = 'data/seenunseen_rttm_raw/' + mp3_basename.replace('.mp3', '.rttm')
    rttm = read_rttm(rttm_fname)
    rttm = replaceRandomSpeakers(rttm)
    subs_fname = 'data/seenunseen_transcripts_raw/' + mp3_basename + '.vtt'
    subs = pyvtt.open(subs_fname)
    
    subs_combined = combine_rttm_sub(rttm, subs)
    subs_with_names = replaceSpeakerNames(subs_combined)
    
    return subs_with_names