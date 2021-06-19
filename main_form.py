from PyQt5 import QtGui, QtWidgets
from PyQt5.QtCore import QThread, pyqtSignal, Qt
import sys
import os
import cv2
import numpy as np
from myui import Ui_Main_Form
from mychange import create_page_sheet

class WorkThread(QThread):
    # 自定義訊號物件。引數str就代表這個訊號可以傳一個字串
    trigger = pyqtSignal(str)

    def __init__(self):
        # 初始化函式
        super(WorkThread, self).__init__()
        self.flag = 1

    def run(self):
        #重寫執行緒執行的run函式
        self.flag = 1

        count = 0
        while(1):
            if self.flag == 1:
                count += 1
                print('in multithread\n')
                if count % 1000 == 0:
                    self.trigger.emit('from multithread')
            else:
                break

    def stop(self):
        self.flag = 0

class Main_UI(QtWidgets.QMainWindow, Ui_Main_Form):
    def __init__(self, input_sheet_list):
        QtWidgets.QMainWindow.__init__(self)
        self.setupUi(self)

        # connect button
        self.next_pushButton.clicked.connect(self.next_button_clicked)
        self.back_pushButton.clicked.connect(self.back_button_clicked)
        self.listen_pushButton.clicked.connect(self.listen_butten_clicked)
        self.stop_pushButton.clicked.connect(self.stop_button_clicked)

        self.stop_pushButton.setEnabled(False)

        self.sheet_file_list = input_sheet_list
        self.sheet_list = []

        for i in range(0, len(self.sheet_file_list)):
            self.sheet_list.append(create_page_sheet(self.sheet_file_list[i], i))

        for i in self.sheet_list:
            i.print_sheet_element()

        self.note_number_accumulation_list = []

        for i in range(0, len(self.sheet_list)):
            self.note_number_accumulation_list.append(self.sheet_list[i].get_note_number())

        print('note number : ' + str(self.note_number_accumulation_list) + '\n')

        for i in range(0, len(self.note_number_accumulation_list)):
            if i > 0:
                self.note_number_accumulation_list[i] += self.note_number_accumulation_list[i-1]

        print('note number list : ' + str(self.note_number_accumulation_list) + '\n')

        self.max_note_number = self.note_number_accumulation_list[len(self.note_number_accumulation_list)-1]

        self.init_pixmap()

        ######################### multithread init
        self.workthread = WorkThread()
        self.workthread.trigger.connect(self.function_for_YX_to_use)

        #########################
        

    def init_pixmap(self):
        self.now_note_number = 0
        self.draw_pixmap(self.now_note_number)

    def next_button_clicked(self):
        if self.now_note_number < self.max_note_number - 1:
            self.now_note_number += 1
            print('now note number: ' + str(self.now_note_number) + '\n')
            self.find_note_information(self.now_note_number)
            self.draw_pixmap(self.now_note_number)


        print('next button\n')

    def back_button_clicked(self):
        if self.now_note_number > 0:
            self.now_note_number -= 1
            print('now note number: ' + str(self.now_note_number) + '\n')
            self.find_note_information(self.now_note_number)
            self.draw_pixmap(self.now_note_number)

        print('back button\n')

    def listen_butten_clicked(self):
        
        self.workthread.start()
        self.next_pushButton.setEnabled(False)
        self.back_pushButton.setEnabled(False)
        self.stop_pushButton.setEnabled(True)
        print('listen button\n')

    def stop_button_clicked(self):
        self.workthread.stop()
        self.next_pushButton.setEnabled(True)
        self.back_pushButton.setEnabled(True)
        self.stop_pushButton.setEnabled(False)
        print('stop button\n')

    def draw_pixmap(self, input_note_number):

        input_note_number, find_page_number = self.find_page_number(input_note_number)
        input_note_number, find_line_number = self.find_line_number(input_note_number, find_page_number)
        note_block = self.find_a_note(input_note_number, find_page_number, find_line_number)
        staff_box_recs = self.find_staff_box(find_page_number, find_line_number)

        icon_x = int((note_block.recs_list[0].x + note_block.recs_list[0].x +  note_block.recs_list[0].w)/2)
        icon_y = int(staff_box_recs.y)

        cut_x, cut_y, cut_w, cut_h = int(staff_box_recs.x), int(staff_box_recs.y - 50), int(staff_box_recs.w), int(staff_box_recs.h + 50)

        img = cv2.imread(self.sheet_file_list[find_page_number])
        img = cv2.circle(img, (icon_x, icon_y),radius=10, color=(0, 0, 255), thickness=4)

        img = QtGui.QImage(img.data, img.shape[1], img.shape[0], QtGui.QImage.Format_RGB888).rgbSwapped()
        img = img.copy(cut_x, cut_y, cut_w, cut_h)

        img = QtGui.QPixmap.fromImage(img)
        img = img.scaled(self.image_label.width(), self.image_label.height(), Qt.KeepAspectRatio)

        self.image_label.setPixmap(img)

    def find_a_note(self, input_note_number, find_page_number, find_line_number):
        #test: 5, 130, 290, 430
                    
        print('find page: ' + str(find_page_number) + ' find line: ' + str(find_line_number) + ' note number: ' + str(input_note_number) + '\n')

        note_block = self.sheet_list[find_page_number].get_note_block(find_line_number, input_note_number)
        note_block.show_sheet_element()

        return note_block

    def find_page_number(self, input_note_number):
        find_page_number = -1
        for i in range(0, len(self.note_number_accumulation_list)):
            if input_note_number < self.note_number_accumulation_list[i]:
                find_page_number = i
                if i > 0:
                    input_note_number = input_note_number - self.note_number_accumulation_list[i-1]
                else:
                    pass
                break

        return input_note_number, find_page_number

    def find_line_number(self, input_note_number, find_page_number):
        temp_page = self.sheet_list[find_page_number]
        line_note_number_accumulation_list = temp_page.get_note_number_list().copy()

        for i in range(0, len(line_note_number_accumulation_list)):
            if i > 0:
                line_note_number_accumulation_list[i] += line_note_number_accumulation_list[i-1]

        find_line_number = -1
        for i in range(0, len(line_note_number_accumulation_list)):
            if input_note_number < line_note_number_accumulation_list[i]:
                find_line_number = i
                if i > 0:
                    input_note_number = input_note_number - line_note_number_accumulation_list[i-1]
                else:
                    pass
                break

        return input_note_number, find_line_number

    def find_staff_box(self, find_page_number, find_line_number):
        return self.sheet_list[find_page_number].get_staff_box_by_line(find_line_number)

    def find_note_information(self, input_note_number):
        input_note_number, find_page_number = self.find_page_number(input_note_number)
        input_note_number, find_line_number = self.find_line_number(input_note_number, find_page_number)
        note_block = self.find_a_note(input_note_number, find_page_number, find_line_number)

        information_list = note_block.get_block_information()

        print('information list(type/position): ' + str(information_list) + '\n')

    ## multithread trigger function
    def function_for_YX_to_use(self, input_element):
        print('function YX say: ' + str(input_element) + '\n')






    


if __name__ == "__main__":
    np.set_printoptions(threshold=sys.maxsize)

    input_sheet_list = ['resources/sample_guitar/sample_2.png', 'resources/sample_guitar/sample_3.png', 'resources/sample_guitar/sample_4.png', 'resources/sample_guitar/sample_5.png']
    
    app = QtWidgets.QApplication(sys.argv)
    window = Main_UI(input_sheet_list)
    window.show()
    sys.exit(app.exec_())