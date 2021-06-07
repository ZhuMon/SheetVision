import sys
import subprocess
import cv2
import time
import numpy as np
from best_fit import fit
from rectangle import Rectangle
from note import Note
from random import randint
from midiutil.MidiFile import MIDIFile

staff_files = [
    "resources/template_guitar/staff_1.png",
    "resources/template_guitar/staff_2.png",
    "resources/template_guitar/staff_3.png",
    "resources/template_guitar/staff_4.png",
    "resources/template_guitar/staff_5.png",
    ]
number_0_files = [
    "resources/template_guitar/0_1.png",
    ]
number_1_files = [
    "resources/template_guitar/1_1.png",
    ]
number_2_files = [
    "resources/template_guitar/2_1.png",
    "resources/template_guitar/2_2.png",
    ]
number_3_files = [
    "resources/template_guitar/3_1.png",
    "resources/template_guitar/3_2.png",
    ]
number_4_files = [
    "resources/template_guitar/4_1.png",
    ]

number_5_files = [
    "resources/template_guitar/5_1.png",
    ]

staff_imgs = [cv2.imread(staff_file, 0) for staff_file in staff_files]
number_2_imgs = [cv2.imread(number_2_file, 0) for number_2_file in number_2_files]
number_0_imgs = [cv2.imread(number_0_files, 0) for number_0_files in number_0_files]
number_1_imgs = [cv2.imread(number_1_file, 0) for number_1_file in number_1_files]
number_3_imgs = [cv2.imread(number_3_file, 0) for number_3_file in number_3_files]
number_4_imgs = [cv2.imread(number_4_file, 0) for number_4_file in number_4_files]
number_5_imgs = [cv2.imread(number_5_file, 0) for number_5_file in number_5_files]

staff_lower, staff_upper, staff_thresh = 60, 150, 0.77
number_0_lower, number_0_upper, number_0_thresh = 50, 150, 0.70
number_1_lower, number_1_upper, number_1_thresh = 80, 150, 0.77
number_2_lower, number_2_upper, number_2_thresh = 80, 150, 0.77
number_3_lower, number_3_upper, number_3_thresh = 80, 150, 0.77
number_4_lower, number_4_upper, number_4_thresh = 80, 150, 0.77
number_5_lower, number_5_upper, number_5_thresh = 80, 150, 0.77


def locate_images(img, templates, start, stop, threshold):
    locations, scale = fit(img, templates, start, stop, threshold)
    img_locations = []
    for i in range(len(templates)):
        w, h = templates[i].shape[::-1]
        w *= scale
        h *= scale
        img_locations.append([Rectangle(pt[0], pt[1], w, h) for pt in zip(*locations[i][::-1])])
    return img_locations

def merge_recs(recs, threshold):
    filtered_recs = []
    while len(recs) > 0:
        r = recs.pop(0)
        recs.sort(key=lambda rec: rec.distance(r))
        merged = True
        while(merged):
            merged = False
            i = 0
            for _ in range(len(recs)):
                if r.overlap(recs[i]) > threshold or recs[i].overlap(r) > threshold:
                    r = r.merge(recs.pop(i))
                    merged = True
                elif recs[i].distance(r) > r.w/2 + recs[i].w/2:
                    break
                else:
                    i += 1
        filtered_recs.append(r)
    return filtered_recs

def open_file(path):
    cmd = {'linux':'eog', 'win32':'explorer', 'darwin':'open'}[sys.platform]
    subprocess.run([cmd, path])

if __name__ == "__main__":
    img_file = sys.argv[1:][0]
    img = cv2.imread(img_file, 0)
    img_gray = img#cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    img = cv2.cvtColor(img_gray,cv2.COLOR_GRAY2RGB)
    ret,img_gray = cv2.threshold(img_gray,127,255,cv2.THRESH_BINARY)
    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    img_width, img_height = img_gray.shape[::-1]
    cv2.imwrite('gray_image.png', img_gray)

    print("Matching staff image...")
    staff_recs = locate_images(img_gray, staff_imgs, staff_lower, staff_upper, staff_thresh)

    print("Filtering weak staff matches...")
    staff_recs = [j for i in staff_recs for j in i]
    heights = [r.y for r in staff_recs] + [0]
    histo = [heights.count(i) for i in range(0, max(heights) + 1)]
    avg = np.mean(list(set(histo)))
    staff_recs = [r for r in staff_recs if histo[r.y] > avg]

    print("Merging staff image results...")
    staff_recs = merge_recs(staff_recs, 0.01)
    staff_recs_img = img.copy()
    for r in staff_recs:
        r.draw(staff_recs_img, (0, 0, 255), 2)
    cv2.imwrite('staff_recs_img.png', staff_recs_img)
    open_file('staff_recs_img.png')

    

    print("Discovering staff locations...")
    staff_boxes = merge_recs([Rectangle(0, r.y, img_width, r.h) for r in staff_recs], 0.01)
    staff_boxes_img = img.copy()
    for r in staff_boxes:
        r.draw(staff_boxes_img, (0, 0, 255), 2)
    cv2.imwrite('staff_boxes_img.png', staff_boxes_img)
    open_file('staff_boxes_img.png')

    
    
    print("Matching number_0 image...")
    number_0_recs = locate_images(img_gray, number_0_imgs, number_0_lower, number_0_upper, number_0_thresh)

    print("Merging number_0 image results...")
    number_0_recs = merge_recs([j for i in number_0_recs for j in i], 0.5)
    number_0_recs_img = img.copy()
    for r in number_0_recs:
        r.draw(number_0_recs_img, (0, 0, 255), 2)
    cv2.imwrite('number_0_recs_img.png', number_0_recs_img)
    open_file('number_0_recs_img.png')

    print("Matching number_1 image...")
    number_1_recs = locate_images(img_gray, number_1_imgs, number_1_lower, number_1_upper, number_1_thresh)

    print("Merging number_1 image results...")
    number_1_recs = merge_recs([j for i in number_1_recs for j in i], 0.5)
    number_1_recs_img = img.copy()
    for r in number_1_recs:
        r.draw(number_1_recs_img, (0, 0, 255), 2)
    cv2.imwrite('number_1_recs_img.png', number_1_recs_img)
    open_file('number_1_recs_img.png')

    print("Matching number_2 image...")
    number_2_recs = locate_images(img_gray, number_2_imgs, number_2_lower, number_2_upper, number_2_thresh)

    print("Merging number_2 image results...")
    number_2_recs = merge_recs([j for i in number_2_recs for j in i], 0.5)
    number_2_recs_img = img.copy()
    for r in number_2_recs:
        r.draw(number_2_recs_img, (0, 0, 255), 2)
    cv2.imwrite('number_2_recs_img.png', number_2_recs_img)
    open_file('number_2_recs_img.png')

    print("Matching number_3 image...")
    number_3_recs = locate_images(img_gray, number_3_imgs, number_3_lower, number_3_upper, number_3_thresh)

    print("Merging number_3 image results...")
    number_3_recs = merge_recs([j for i in number_3_recs for j in i], 0.5)
    number_3_recs_img = img.copy()
    for r in number_3_recs:
        r.draw(number_3_recs_img, (0, 0, 255), 2)
    cv2.imwrite('number_3_recs_img.png', number_3_recs_img)
    open_file('number_3_recs_img.png')

    print("Matching number_4 image...")
    number_4_recs = locate_images(img_gray, number_4_imgs, number_4_lower, number_4_upper, number_4_thresh)

    print("Merging number_4 image results...")
    number_4_recs = merge_recs([j for i in number_4_recs for j in i], 0.5)
    number_4_recs_img = img.copy()
    for r in number_4_recs:
        r.draw(number_4_recs_img, (0, 0, 255), 2)
    cv2.imwrite('number_4_recs_img.png', number_4_recs_img)
    open_file('number_4_recs_img.png')

    print("Matching number_5 image...")
    number_5_recs = locate_images(img_gray, number_5_imgs, number_5_lower, number_5_upper, number_5_thresh)

    print("Merging number_5 image results...")
    number_5_recs = merge_recs([j for i in number_5_recs for j in i], 0.5)
    number_5_recs_img = img.copy()
    for r in number_5_recs:
        r.draw(number_5_recs_img, (0, 0, 255), 2)
    cv2.imwrite('number_5_recs_img.png', number_5_recs_img)
    open_file('number_5_recs_img.png')

    exit()

    note_groups = []
    for box in staff_boxes:
        staff_number_0s = [Note(r, "number_0", box) 
            for r in number_0_recs if abs(r.middle[1] - box.middle[1]) < box.h*5.0/8.0]
        staff_number_1s = [Note(r, "number_1", box) 
            for r in number_1_recs if abs(r.middle[1] - box.middle[1]) < box.h*5.0/8.0]
        number_2_notes = [Note(r, "4,8", box, staff_number_0s, staff_number_1s) 
            for r in number_2_recs if abs(r.middle[1] - box.middle[1]) < box.h*5.0/8.0]
        number_3_notes = [Note(r, "2", box, staff_number_0s, staff_number_1s) 
            for r in number_3_recs if abs(r.middle[1] - box.middle[1]) < box.h*5.0/8.0]
        number_4_notes = [Note(r, "1", box, staff_number_0s, staff_number_1s) 
            for r in number_4_recs if abs(r.middle[1] - box.middle[1]) < box.h*5.0/8.0]
        staff_notes = number_2_notes + number_3_notes + number_4_notes
        staff_notes.sort(key=lambda n: n.rec.x)
        staffs = [r for r in staff_recs if r.overlap(box) > 0]
        staffs.sort(key=lambda r: r.x)
        note_color = (randint(0, 255), randint(0, 255), randint(0, 255))
        note_group = []
        i = 0; j = 0;
        while(i < len(staff_notes)):
            if (staff_notes[i].rec.x > staffs[j].x and j < len(staffs)):
                r = staffs[j]
                j += 1;
                if len(note_group) > 0:
                    note_groups.append(note_group)
                    note_group = []
                note_color = (randint(0, 255), randint(0, 255), randint(0, 255))
            else:
                note_group.append(staff_notes[i])
                staff_notes[i].rec.draw(img, note_color, 2)
                i += 1
        note_groups.append(note_group)

    for r in staff_boxes:
        r.draw(img, (0, 0, 255), 2)
    for r in number_0_recs:
        r.draw(img, (0, 0, 255), 2)
    number_1_recs_img = img.copy()
    for r in number_1_recs:
        r.draw(img, (0, 0, 255), 2)
        
    cv2.imwrite('res.png', img)
    open_file('res.png')
   
    for note_group in note_groups:
        print([ note.note + " " + note.sym for note in note_group])

    midi = MIDIFile(1)
     
    track = 0   
    time = 0
    channel = 0
    volume = 100
    
    midi.addTrackName(track, time, "Track")
    midi.addTempo(track, time, 140)
    
    for note_group in note_groups:
        duration = None
        for note in note_group:
            note_type = note.sym
            if note_type == "1":
                duration = 4
            elif note_type == "2":
                duration = 2
            elif note_type == "4,8":
                duration = 1 if len(note_group) == 1 else 0.5
            pitch = note.pitch
            midi.addNote(track,channel,pitch,time,duration,volume)
            time += duration

    midi.addNote(track,channel,pitch,time,4,0)
    # And write it to disk.
    binfile = open("output.mid", 'wb')
    midi.writeFile(binfile)
    binfile.close()
    open_file('output.mid')
