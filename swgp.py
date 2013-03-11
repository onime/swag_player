#!/usr/bin/python

from time import sleep
import threading
from  colorama import Fore
import re
from easylast import *
import configparser
import sys
import os
import subprocess
from  shutil import move

def change_ext(name_file,new_ext):
    name_split = name_file.split(".")
    return ".".join(name_split[:len(name_split)-1]) +"."+new_ext

def incr_ep(info):
    info[-1] +=1
    return info

def sync_video_file_and_sub(info):
    
    path_ep_srt = path_of_episode(info[0],info[1],info[2],True)
    last_ep_dl = infos_of_name(info[0],"DL")
   
    new_name = format_name(info[0],".")+"."+format_SXXEXX(info[1],info[2])
    new_path = path_ep_srt[0]
    
    if(path_ep_srt[1] != ""):
    
        if change_ext(path_ep_srt[0],"srt") != path_ep_srt[1]:
            
            print(partial,os.path.basename(path_ep_srt[0]))
            print(partial,os.path.basename(path_ep_srt[1]))
            print(partial,"Name of video and name of subtitle are not the same")

            if input("Change name ? y/n : ") == "y":
                for path in path_ep_srt:
                    ext = path.split(".")[-1]
                    new_path = new_name+"."+ext
                    path_split = path.split("/")
                    path_split[-1] = new_path
                    #print(ext,new_path)
                    new_path = "/".join(path_split)
                    if new_path != path:
                        move(path,new_path)
                print(ok, new_name+".."+format_SXXEXX(last_ep_dl[1],last_ep_dl[2]))
            else:
                print(partial,new_name+".."+format_SXXEXX(last_ep_dl[1],last_ep_dl[2]))
        else:
            print(ok,new_name+".."+format_SXXEXX(last_ep_dl[1],last_ep_dl[2]))
    else:
        print(nosub,new_name+".."+format_SXXEXX(last_ep_dl[1],last_ep_dl[2]))
        if input("Trying to download sub ? y/n : ")=="y":
            os.system("/usr/local/bin/dl_sub")
        
    return new_path

def run_cmd(info,arg = "last"):

    if arg=="last":
        suiteCmd = ""
    else:
        suiteCmd = redirect
        
    if len(info) == 2:
        path_last_seen = path_scans+format_name(info[0],".") + "/"+str(info[1])
        if os.path.exists(path_last_seen):
            print("Reading",info[0],info[1])
            os.system("ristretto "+path_last_seen)
        else:
            print(path_last_seen,"doesn't exists")
            exit(0)
    else:
        ret = subprocess.check_output(["/usr/local/bin/mplayer_wrap",str(info[0]),str(info[1]),str(info[2])])
        
        match = re.search("\n([0-9]+):([0-9]+)\n",ret.decode("utf-8"))
        if match != None:
            return [int(match.group(1)),int(match.group(2))]
        else:
            return [2,1]

def save_next_not_finish(info,time_cur):
    with open(state_played,"w") as next_played:
        next_played.write(info[0]+":"+str(info[1])+":"+str(info[2])+":"+str(time_cur))


def list_ready():
    manga_last_seen = infos_last("MANGA",".","VU")
    manga_last_dl = infos_last("MANGA",".","DL")
    show_last_seen = infos_last("SHOW",".","VU")
    show_last_dl = infos_last("SHOW",".","DL")
  
    print("[SCANS]")
    for ms in manga_last_seen:
        for md in manga_last_dl:
            if md[0] == ms[0] and md[1] > ms[1]:
                print(ok,format_name(md[0],"."),str(ms[1]+1)+".."+str(md[1]))
               
    print("[SHOWS]")
    for ss in show_last_seen:
        for sd in show_last_dl:
            if ss[0] == sd[0] and  (sd[1] > ss[1] or (sd[1] == ss[1] and sd[2] > ss[2])):
                sync_video_file_and_sub([ss[0],ss[1],ss[2]+1])

def play_last(args):

    if len(args) >= 1:
        run_cmd(infos_of_name(args[0],"VU"),"last")

def play_show(info):
       
    sync_video_file_and_sub(info)       
    return run_cmd(info)         

def cmp_info(info_a,info_b):

    if len(info_b) != len(info_b):
        return None

    info_a[1] = int(info_a[1])
    info_b[1] = int(info_b[1])

    if len(info_a) == 2:
        
        if info_a[1] > info_b[1]:
            return 1
        elif info_a[1] < info_b[1]:
            return -1
        else:
            return 0
    elif len(info_a) == 3:
        info_a[2] = int(info_a[2])
        info_b[2] = int(info_b[2])

        if info_a[1] == info_b[1] and info_a[2] > info_b[2]:
            return 1
        elif info_a[1] == info_b[1] and info_a[2] < info_b[2]:
            return -1
        elif info_a[1] > info_b[1]:
            return 1
        elif info_a[1] < info_b[1]:
            return -1
        else:
            return 0

    else:
            return None

def increment_or_save(info,time_total,time_final):
    
    if len(info) != 2:
        
        ratio = time_final/time_total * 100
        name_ep = format_name(info[0],".")+"."+format_SXXEXX(info[1],info[2])
        
        if ratio>  90:
            incr_last(info[0],"VU")
            print(name_ep,"seen")
        else:
            save_next_not_finish(info,time_final)
            print(name_ep,"save at",str(int(ratio))+"%")
    else:
        incr_last(info[0],"VU")

def play_fix(tab_order):

     for name in tab_order:
         info = infos_of_name(name,"VU")
         info_dl = infos_of_name(name,"DL")
         
         if info != None:
             info = incr_ep(info)         
         
             while cmp_info(info,info_dl) < 1:
                 print(info)
                 #play_show()
                 info = incr_ep(info)
                 increment_or_save(info,1,1)              

def play_circle(tab_order):
    
    still_ep_to_play = True
    while still_ep_to_play:
        still_ep_to_play = False
        
        for name in tab_order:
            info = infos_of_name(name,"VU")
            info_dl = infos_of_name(name,"DL")

            if info != None:
                info = incr_ep(info)
                if cmp_info(info,info_dl) < 1:
                    print(info)
                    #play_show()
                    increment_or_save(info,1,1)
                    still_ep_to_play = True
                
def play_list(type_media,args):
    swgp_config = read_config(path_config)
    order_shows = swgp_config["ORDER"][type_media]

    tab_order = order_shows.split(",")
    still_ep_to_play = True
    
    if len(args) > 0:
        if  args[0] == "--fix":
            play_fix(tab_order)
    else:
        play_circle(tab_order)
   
       
#--all play all episode till the last ready
#--fix will play all media before change i.e play all naruto then one.piece
def play_next(args):
    
    if len(args) >= 1:
        if args[0] == "--shows":

            print("play next shows ready")
            play_list("shows",args[1:])

        elif args[0] == "--scans":
            print("play next scans ready")
            play_list("scans",args[1:])
        else:
            info = infos_of_name(args[0],"VU")
            
            (time_total,time_final) = play_show(incr_ep(info))
            
            increment_or_save(info,time_total,time_final)
          

state_played = "/home/yosholo/.config/utils/swgp/state_played"
ok = "[ "+Fore.GREEN + "OK"+Fore.RESET+" ]"
partial = "[ "+Fore.YELLOW + "PARTIAL" + Fore.RESET+" ]"
nosub = "[ "+Fore.RED + "NO SUB" + Fore.RESET+" ]"

time_total = 0
args = sys.argv[1:]

if len(args) == 0:
    print("Nothing to do")
    exit(0)


if args[0] == "list_ready":
    list_ready()
elif args[0] == "play_last":
    play_last(args[1:])
elif args[0] == "play_next":
    play_next(args[1:])
#elif args[0] == "play":
#    play()
#for arg in args:
#    if 

