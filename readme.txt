2021-06-17

我把整個程式主要的啟動移到了 main_form.py
使用: python main_form.py

有幾個 function 應該是 YX 你需要使用的

class Main_UI 的 listen_butten_clicked & stop_button_clicked 
這兩個 function 我設想是用來開始聽音樂和暫停聽音樂
這兩個用上了 multithread，看你需不需要

class Main_UI 的 find_note_information
這個 function 你只要 input note 編號(第幾個 note)，他就會回傳type (0~7 沒有6)和 information(0~5)

class Main_UI 的 function_for_YX_to_use
這個 function 和 multithread 連著，multithread 中可以呼叫到這個 function

main 裡面的 input_sheet_list 是要讀入的樂譜
