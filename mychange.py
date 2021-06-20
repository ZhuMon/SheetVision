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
import operator

f = open("log.txt", 'w')
f_sheet = open("log_sheet.txt", 'w')
f_debug = open("log_debug.txt", 'w')

class Sheet_Block_Class:
    def __init__(self, input_recs_list):
        self.recs_list = input_recs_list.copy()

    def sort_recs(self):
        self.recs_list.sort(key=operator.attrgetter('y'))

    def print_sheet_element(self):
        f_sheet.writelines('Sheet Block Class\n')
        for r in self.recs_list:
            f_sheet.writelines('x: ' + str(r.x) + ' type: ' + str(r.type_flag) + ' line_num: ' + str(r.line_num) + '\n')

    def show_sheet_element(self):
        for r in self.recs_list:
            f_sheet.writelines('x: ' + str(r.x) + ' type: ' + str(r.type_flag) + ' line_num: ' + str(r.line_num) + '\n')

    def get_block_information(self):
        return_list = []

        for r in self.recs_list:
            return_list.append([r.type_flag, r.line_num])
        
        return return_list




class Sheet_Line_Class:
    def __init__(self, staff_range, staff_boxes, img, line_number):
        self.staff_range = staff_range.copy()
        self.sheet_block_class_list = []
        self.recs_list = []
        self.staff_boxes = staff_boxes
        self.img = img.copy()
        self.line_number = line_number
    
    def add_recs(self, input_recs):
        self.recs_list.append(input_recs)

    def sort_recs(self):
        self.recs_list.sort(key=operator.attrgetter('x'))

    def check_line(self):
        self.line_position = []
        black_dict = np.zeros(int(self.staff_boxes.y + self.staff_boxes.h))
        left_range = int(self.staff_boxes.x + 0.1 * self.staff_boxes.w)
        right_range = int(self.staff_boxes.x + 0.9 * self.staff_boxes.w)
        print('black_dict_len: ' + str(len(black_dict)) + ' left_range: ' + str(left_range) + ' right_range: ' + str(right_range) + '\n')

        f_debug.writelines('a line block\n')
        for i in range(left_range, right_range, 5):
            for j in range(int(self.staff_boxes.y), int(self.staff_boxes.y + self.staff_boxes.h)):
                if self.img[j][i] <= 128:
                    black_dict[j] += 1
                    break
                f_debug.writelines('i : ' + str(i) + ' j : ' + str(j) + ' self.img[j][i]: ' + str(self.img[j][i]) + '\n')
                
                

        line_one = np.argmax(black_dict, axis=0)
        #f.writelines('line_one: ' + str(line_one) + '\n')

        black_dict = np.zeros(int(self.staff_boxes.y + self.staff_boxes.h + 1))

        for i in range(left_range, right_range, 5):
            for j in range(int(self.staff_boxes.y + self.staff_boxes.h), int(self.staff_boxes.y), -1):
                if self.img[j][i] <= 128:
                    black_dict[j] += 1
                    break

        line_six = np.argmax(black_dict, axis=0)

        self.line_position = [line_one, line_one + int((line_six - line_one) / 5), line_one + int((line_six - line_one) / 5 * 2), line_one + int((line_six - line_one) / 5 * 3), line_one + int((line_six - line_one) / 5 * 4), line_six]

        #f.writelines('line_six: ' + str(line_six) + '\n')
        f.writelines('line position: ' + str(self.line_position) + '\n')

        for r in range(0, len(self.recs_list)):
            for line_num in range(0, len(self.line_position)):
                if self.recs_list[r].y <= self.line_position[line_num] and self.recs_list[r].y + self.recs_list[r].h >= self.line_position[line_num]:
                    self.recs_list[r].line_num = line_num
                    break



    def add_block_class(self):
        id_count = 0
        pre_x = -100
        temp_recs_list = []
        for r in self.recs_list:
            if abs(r.x - pre_x) <= 10:
                temp_recs_list.append(r)
                pre_x = r.x
            else:
                if len(temp_recs_list) != 0:
                    self.sheet_block_class_list.append(Sheet_Block_Class(temp_recs_list.copy()))
                    temp_recs_list = []
                    
                pre_x = r.x
                temp_recs_list.append(r)

        if len(temp_recs_list) != 0:
            self.sheet_block_class_list.append(Sheet_Block_Class(temp_recs_list.copy()))
            temp_recs_list = []
        
        for k in range(0, len(self.sheet_block_class_list)):
            self.sheet_block_class_list[k].sort_recs()
            #self.sheet_block_class_list[k].print_sheet_element()

    def get_note_number(self):
        return len(self.sheet_block_class_list)

    def print_sheet_element(self):
        f_sheet.writelines('Sheet Line Class\n')
        for k in range(0, len(self.sheet_block_class_list)):
            self.sheet_block_class_list[k].print_sheet_element()

    
class Sheet_Page_Class:
    def __init__(self, staff_range, recs_list, staff_boxes, img, page_number):
        self.staff_range = staff_range.copy()
        self.sheet_line_class_list = []
        self.staff_boxes = staff_boxes.copy()
        self.img = img.copy()
        self.page_number = page_number

        for r in range(0, len(self.staff_range)):
            self.sheet_line_class_list.append(Sheet_Line_Class(self.staff_range[r], self.staff_boxes[r], self.img, r))
        #f.writelines(str(self.sheet_line_class_list))

        for r in range(0, len(recs_list)):
            for t in range(0, len(recs_list[r])):
                for k in range(0, len(self.sheet_line_class_list)):
                    if recs_list[r][t].y >= self.sheet_line_class_list[k].staff_range[0] and recs_list[r][t].y <= self.sheet_line_class_list[k].staff_range[1]:
                        self.sheet_line_class_list[k].add_recs(recs_list[r][t])
                        break

        for k in range(0, len(self.sheet_line_class_list)):
            self.sheet_line_class_list[k].sort_recs()
            self.sheet_line_class_list[k].check_line()
            self.sheet_line_class_list[k].add_block_class()
            #self.sheet_line_class_list[k].print_sheet_element()

    def get_note_number(self):
        note_number = 0
        for k in range(0, len(self.sheet_line_class_list)):
            note_number += self.sheet_line_class_list[k].get_note_number()
        return note_number

    def get_note_number_list(self):
        note_number_list = []
        for k in range(0, len(self.sheet_line_class_list)):
            note_number_list.append(self.sheet_line_class_list[k].get_note_number())

        return note_number_list

    def get_note_block(self, input_line_number, input_block_number):
        return self.sheet_line_class_list[input_line_number].sheet_block_class_list[input_block_number]

    def get_line_range(self, input_line_number):
        return self.sheet_line_class_list[input_line_number].staff_range

    def get_staff_box_by_line(self, input_line_number):
        return self.sheet_line_class_list[input_line_number].staff_boxes

    def get_block_information(self, input_line_number, input_block_number):
        return self.sheet_line_class_list[input_line_number].sheet_block_class_list[input_block_number].get_block_information()
        
    def print_sheet_element(self):
        f_sheet.writelines('Sheet Class\n')

        for k in range(0, len(self.sheet_line_class_list)):
            self.sheet_line_class_list[k].print_sheet_element()


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
    "resources/template_guitar/3_3.png",
    ]
number_4_files = [
    "resources/template_guitar/4_1.png",
    ]

number_5_files = [
    "resources/template_guitar/5_1.png",
    "resources/template_guitar/5_2.png",
    ]

number_7_files = [
    "resources/template_guitar/7_1.png",
    ]

staff_imgs = [cv2.imread(staff_file, 0) for staff_file in staff_files]
number_2_imgs = [cv2.imread(number_2_file, 0) for number_2_file in number_2_files]
number_0_imgs = [cv2.imread(number_0_files, 0) for number_0_files in number_0_files]
number_1_imgs = [cv2.imread(number_1_file, 0) for number_1_file in number_1_files]
number_3_imgs = [cv2.imread(number_3_file, 0) for number_3_file in number_3_files]
number_4_imgs = [cv2.imread(number_4_file, 0) for number_4_file in number_4_files]
number_5_imgs = [cv2.imread(number_5_file, 0) for number_5_file in number_5_files]
number_7_imgs = [cv2.imread(number_7_file, 0) for number_7_file in number_7_files]

staff_lower, staff_upper, staff_thresh = 60, 150, 0.77
number_0_lower, number_0_upper, number_0_thresh = 50, 150, 0.77
number_1_lower, number_1_upper, number_1_thresh = 80, 150, 0.77
number_2_lower, number_2_upper, number_2_thresh = 80, 150, 0.77
number_3_lower, number_3_upper, number_3_thresh = 80, 150, 0.77
number_4_lower, number_4_upper, number_4_thresh = 80, 150, 0.77
number_5_lower, number_5_upper, number_5_thresh = 80, 150, 0.77
number_7_lower, number_7_upper, number_7_thresh = 80, 150, 0.77


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

def filter_range(recs, sheet_range, type_flage):
    new_recs = []
    for i in range(len(recs)):
        for j in sheet_range:
            if recs[i].y >= j[0] and recs[i].y <= j[1]:
                recs[i].type_flag = type_flage
                new_recs.append(recs[i])
                break

    f.writelines('new_recs: ' + str(new_recs) + '\n')
    return new_recs


def open_file(path):
    cmd = {'linux':'eog', 'win32':'explorer', 'darwin':'open'}[sys.platform]
    subprocess.run([cmd, path])

def create_page_sheet(input_img_file, page_number):
    

    #img_file = sys.argv[1:][0]
    img_file = input_img_file
    img = cv2.imread(img_file, 0)
    img_gray = img#cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    img = cv2.cvtColor(img_gray,cv2.COLOR_GRAY2RGB)
    ret,img_gray = cv2.threshold(img_gray,127,255,cv2.THRESH_BINARY)
    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    img_width, img_height = img_gray.shape[::-1]
    cv2.imwrite('gray_image.png', img_gray)

    print('img_gray shape: ' + str(img_gray.shape) + '\n')

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
    #open_file('staff_recs_img.png')

    

    print("Discovering staff locations...")
    staff_boxes = merge_recs([Rectangle(0, r.y, img_width, r.h) for r in staff_recs], 0.01)
    staff_boxes_img = img.copy()
    
    sheet_range = []

    for r in staff_boxes:
        r.draw(staff_boxes_img, (0, 0, 255), 2)
        f.writelines('x: ' + str(r.x) + ' y: ' + str(r.y) + ' w: ' + str(r.w) + ' h: ' + str(r.h) + ' middle: ' + str(r.middle) + ' area: ' + str(r.area) + '\n')
        sheet_range.append([r.y, r.y + r.h])
    
    #cv2.line(staff_boxes_img, (100, 813), (1000, 891), (0, 0, 255), 5)
    #cv2.line(staff_boxes_img, (100, 1121), (1000, 1199), (0, 0, 255), 5)
    #cv2.line(staff_boxes_img, (100, 1439), (1000, 1517), (0, 0, 255), 5)
    #cv2.line(staff_boxes_img, (100, 1750), (1000, 1828), (0, 0, 255), 5)

    cv2.imwrite('staff_boxes_img.png', staff_boxes_img)
    
    print('staff box len: ' + str(len(staff_boxes)) + '\n')
    # open_file('staff_boxes_img.png')
    f.writelines(str(sheet_range) + '\n')

    
    
    print("Matching number_0 image...")
    number_0_recs = locate_images(img_gray, number_0_imgs, number_0_lower, number_0_upper, number_0_thresh)

    print("Merging number_0 image results...")
    number_0_recs = merge_recs([j for i in number_0_recs for j in i], 0.5)
    number_0_recs = filter_range(number_0_recs, sheet_range, 0)
    number_0_recs_img = img.copy()
    for r in number_0_recs:
        r.draw(number_0_recs_img, (0, 0, 255), 2)
    cv2.imwrite('number_0_recs_img.png', number_0_recs_img)
    #open_file('number_0_recs_img.png')

    print("Matching number_1 image...")
    number_1_recs = locate_images(img_gray, number_1_imgs, number_1_lower, number_1_upper, number_1_thresh)

    print("Merging number_1 image results...")
    number_1_recs = merge_recs([j for i in number_1_recs for j in i], 0.5)
    number_1_recs = filter_range(number_1_recs, sheet_range, 1)
    number_1_recs_img = img.copy()
    for r in number_1_recs:
        r.draw(number_1_recs_img, (0, 0, 255), 2)
    cv2.imwrite('number_1_recs_img.png', number_1_recs_img)
    #open_file('number_1_recs_img.png')

    print("Matching number_2 image...")
    number_2_recs = locate_images(img_gray, number_2_imgs, number_2_lower, number_2_upper, number_2_thresh)

    print("Merging number_2 image results...")
    number_2_recs = merge_recs([j for i in number_2_recs for j in i], 0.5)
    number_2_recs = filter_range(number_2_recs, sheet_range, 2)
    number_2_recs_img = img.copy()
    for r in number_2_recs:
        r.draw(number_2_recs_img, (0, 0, 255), 2)
    cv2.imwrite('number_2_recs_img.png', number_2_recs_img)
    #open_file('number_2_recs_img.png')

    print("Matching number_3 image...")
    number_3_recs = locate_images(img_gray, number_3_imgs, number_3_lower, number_3_upper, number_3_thresh)

    print("Merging number_3 image results...")
    number_3_recs = merge_recs([j for i in number_3_recs for j in i], 0.5)
    number_3_recs = filter_range(number_3_recs, sheet_range, 3)
    number_3_recs_img = img.copy()
    for r in number_3_recs:
        r.draw(number_3_recs_img, (0, 0, 255), 2)
    cv2.imwrite('number_3_recs_img.png', number_3_recs_img)
    #open_file('number_3_recs_img.png')

    print("Matching number_4 image...")
    number_4_recs = locate_images(img_gray, number_4_imgs, number_4_lower, number_4_upper, number_4_thresh)

    print("Merging number_4 image results...")
    number_4_recs = merge_recs([j for i in number_4_recs for j in i], 0.5)
    number_4_recs = filter_range(number_4_recs, sheet_range, 4)
    number_4_recs_img = img.copy()
    for r in number_4_recs:
        r.draw(number_4_recs_img, (0, 0, 255), 2)
    cv2.imwrite('number_4_recs_img.png', number_4_recs_img)
    #open_file('number_4_recs_img.png')

    print("Matching number_5 image...")
    number_5_recs = locate_images(img_gray, number_5_imgs, number_5_lower, number_5_upper, number_5_thresh)

    print("Merging number_5 image results...")
    number_5_recs = merge_recs([j for i in number_5_recs for j in i], 0.5)
    number_5_recs = filter_range(number_5_recs, sheet_range, 5)
    number_5_recs_img = img.copy()
    for r in number_5_recs:
        r.draw(number_5_recs_img, (0, 0, 255), 2)
    cv2.imwrite('number_5_recs_img.png', number_5_recs_img)
    #open_file('number_5_recs_img.png')

    print("Matching number_7 image...")
    number_7_recs = locate_images(img_gray, number_7_imgs, number_7_lower, number_7_upper, number_7_thresh)

    print("Merging number_7 image results...")
    number_7_recs = merge_recs([j for i in number_7_recs for j in i], 0.5)
    number_7_recs = filter_range(number_7_recs, sheet_range, 7)
    number_7_recs_img = img.copy()
    for r in number_7_recs:
        r.draw(number_7_recs_img, (0, 0, 255), 2)
    cv2.imwrite('number_7_recs_img.png', number_7_recs_img)
    #open_file('number_7_recs_img.png')

    all_recs_img = img.copy()
    for r in number_0_recs:
        r.draw(all_recs_img, (0, 0, 255), 2)
    for r in number_1_recs:
        r.draw(all_recs_img, (0, 0, 255), 2)
    for r in number_2_recs:
        r.draw(all_recs_img, (0, 0, 255), 2)
    for r in number_3_recs:
        r.draw(all_recs_img, (0, 0, 255), 2)
    for r in number_4_recs:
        r.draw(all_recs_img, (0, 0, 255), 2)
    for r in number_5_recs:
        r.draw(all_recs_img, (0, 0, 255), 2)
    for r in number_7_recs:
        r.draw(all_recs_img, (0, 0, 255), 2)

    cv2.imwrite('all_recs_img.png', all_recs_img)
    open_file('all_recs_img.png')

    #f.writelines(str(img_gray) + '\n')

    sheet_page_class = Sheet_Page_Class(sheet_range, [number_0_recs, number_1_recs, number_2_recs, number_3_recs, number_4_recs, number_5_recs, number_7_recs], staff_boxes, img_gray.copy(), page_number)
    #sheet_page_class.print_sheet_element()
    return sheet_page_class

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
