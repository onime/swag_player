#!/usr/bin/python

import threading
from  colorama import Fore
import re
from easylast import *
import configparser
import sys
import os
from  shutil import move

def change_ext(name_file,new_ext):
    name_split = name_file.split(".")
    return ".".join(name_split[:len(name_split)-1]) +"."+new_ext


def path_of_episode(name,season,episode,srt=False):

    list_show = os.listdir(path_shows)
    for show in list_show:
        if re.search(name,show,re.IGNORECASE):
            path_ep = path_shows+show+"/Saison."+str(season)+"/"

    if srt==True:
        path_ep_srt=["",""]
   
    if os.path.exists(path_ep):
        list_episode = os.listdir(path_ep)
        for name_ep in list_episode:
            if re.search(format_SXXEXX(season,episode),name_ep,re.IGNORECASE):
                if srt == False:
                    if not re.search(".srt$",name_ep):
                        path_ep +=name_ep
                else:
                    if re.search(".srt$",name_ep):
                        path_ep_srt[1] = path_ep+name_ep
                    else:
                        path_ep_srt[0] = path_ep+name_ep
    else:
        print(path_ep + " doesn't exists")
        exit(0)
    
    if srt == False:
        return path_ep
    else:
        return path_ep_srt

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


def run_cmd(info):

     if len(info) == 2:
         path_last_seen = path_scans+format_name(info[0],".") + "/"+str(info[1])
         if os.path.exists(path_last_seen):
             print("Reading",info[0],info[1])
             os.system("ristretto "+path_last_seen)
         else:
             print(path_last_seen,"doesn't exists")
             exit(0)
     else:
         path_last_seen = path_of_episode(info[0],info[1],info[2])
         if os.path.exists(path_last_seen):
             print("Playing",format_name(info[0],".")+"."+format_SXXEXX(info[1],info[2]))
             os.system(cmd_mplayer + path_last_seen)
         else:
             print(path_last_seen,"doesn't exists")
             exit(0)

def play_last(args):

    if len(args) >= 1:
        run_cmd(infos_of_name(args[0],"VU"))
                
    
def play_next(args):
    
    if len(args) >= 1:
        if args[0] == "--shows":
            print("play next shows ready")
        elif args[0] == "--scans":
            print("play next scans ready")
        else:
            info = infos_of_name(args[0],"VU")
            info_dl = infos_of_name(args[0],"DL")
    
            run_cmd([info[0],info[1],info[2]+1])
            print("fuck")
            #incr_last(info[0],"--VU")

fifo_mplayer = "/home/yosholo/.config/utils/fifo_mplayer"
cmd_mplayer = "mplayer --slave -input file="+fifo_mplayer+" --really-quiet 2> /dev/null "
ok = "[ "+Fore.GREEN + "OK"+Fore.RESET+" ]"
partial = "[ "+Fore.YELLOW + "PARTIAL" + Fore.RESET+" ]"
nosub = "[ "+Fore.RED + "NO SUB" + Fore.RESET+" ]"

args = sys.argv[1:]
if len(args) == 0:
    print("Nothing to do")
    exit(0)

config = configparser.ConfigParser()
config.read("/home/yosholo/.config/utils/swgp.conf")

path_scans = config.get("PATHS","scans")
path_shows = config["PATHS"]["shows"]

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

