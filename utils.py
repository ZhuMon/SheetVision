ref_table = 'ABCDEFG'
base_midi = [21, 23, 12, 14, 16, 17, 19]
guitar_base = [40, 45, 50, 55, 59, 64]
guitar_base = guitar_base[::-1]

def base_tone(capo):
    return [b+capo for b in guitar_base]
    
def convert_pos2midi(string, pos, capo):
    base = base_tone(capo)
    return base[string-1]+pos

def convert_noteName2midi(note):
    i = ref_table.index(note[0])
    sharp = 0
    level = 0
    if note[1] == '#':
        sharp = 1
        level = int(note[2])
    else:
        level = int(note[1])

    return base_midi[i] + level*12 + sharp
