#!/usr/bin/python
import threading
import sys
from easylast import *
from time import sleep
import re

class threadSendMplayer(threading.Thread):
    def __init__(self,path,info):       
        self.info_ep = info
        self.path = path
        threading.Thread.__init__(self)

    def run(self):
             
        while try_open_fifo(read_fifo) == False:
            sleep(0.2)

        thread_exec = threading.Thread(target = exec_mplayer,args=(self.path,))
        thread_exec.start()        
       
        info_r = restore_next_not_finish()
        if info_r[:-1] == self.info_ep:
            send_inform("seek "+str(info_r[-1]),send_fifo)
                           
        while thread_exec.is_alive():
            send_inform("get_time_length",send_fifo)
            send_inform("get_time_pos",send_fifo)       
            sleep(1)
    def get_path():
        return self.path

class threadReadMplayer(threading.Thread):
    def __init__(self):
        self.time_total = 1
        self.time_cur = 0
        threading.Thread.__init__(self)
    def run(self):
        
        read_info = ""
        while re.search("Exit",read_info)== None:
            read_info = read_inform(read_fifo)
            if self.time_total == 1:
               
                match = re.search("ANS_LENGTH=(.*)",read_info,re.IGNORECASE)
                if match != None:
                    self.time_total = int(float(match.group(1)))
                    
            match = re.search("ANS_TIME_POSITION=(.*)",read_info,re.IGNORECASE)
            if match != None:
                self.time_cur = int(float(match.group(1)))


    def get_time_total(self):
        return self.time_total
    def get_time_cur(self):
        return self.time_cur

def exec_mplayer(path):       
    cmd_mplayer = "mplayer --slave --quiet -input file="+send_fifo +" "
    redirect =  "  > "+read_fifo +"  2> /dev/null "  
    os.system(cmd_mplayer + path + redirect)
    
def restore_next_not_finish():
    with open(state_played,"r") as next_played:
        info = next_played.readline().split(":")
        return [info[0],int(info[1]),int(info[2]),int(info[3])]

state_played = "/home/yosholo/.config/utils/swgp/state_played"
send_fifo = "/home/yosholo/.config/utils/swgp/send_mplayer"
read_fifo = "/home/yosholo/.config/utils/swgp/read_mplayer"

args = sys.argv
if len(args) != 4:
    print("fuck")

info = args[1:]

path_file = path_of_episode(info[0],info[1],info[2])

print("Playing",format_name(info[0],".")+"."+format_SXXEXX(info[1],info[2]))

thread_read = threadReadMplayer()
thread_read.start()
thread_send = threadSendMplayer(path_file,info)
thread_send.start()
thread_send.join()

print(thread_read.get_time_total(),thread_read.get_time_cur())


