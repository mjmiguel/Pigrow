#!/usr/bin/python
import time
import os
import sys

capture_with = "uvc" # or 'fs'
settings_flie = None
caps_path = None

for argu in sys.argv:
    try:
        thearg = str(argu).split('=')[0]
        theval = str(argu).split('=')[1]
        if  thearg == 'capture_with' or thearg == 'with':
            capture_with = theval
        elif thearg == 'settings_flie' or thearg == 'set':
            settings_flie = theval
        elif thearg == 'caps_path' or thearg == 'caps':
            caps_path == theval
    except:
        print("Didn't undertand " + str(argu))

def load_camera_settings(loc_dic):
    s_val, c_val, g_val, b_val, x_dim, y_dim, cam_num, cam_opt, fsw_extra, uvc_extra = ''
    # caps folder path from loc_dic file -annoying for multicam
    if caps_path == None:
        try:
            caps_path = loc_dic['caps_path']
        except:
            caps_path = '/home/pi/Pigrow/caps/'
            if os.exists(caps_path):
                print("Using default folder; " + str(caps_path))
            else:
                caps_path = "./"
                print("default path doesn't work, using current directory (sorry)")
    else:
        print("saving to; " + str(caps_path))
    # finding camera settings file in loc_dic
    if settings_flie == None:
        try:
            settings_flie = loc_dic['camera_settings']
            print("using camera settings file as directed by dirlocs file; " + settings_flie)
        except:
            settings_flie = "/home/pi/Pigrow/config/camera_settings.txt"
            print("camera settings file not mentioned in dirlocs file, using default; " + settings_flie)
    else:
        print("Using settings file; " + str(settings_flie))
    #Grabbing all the relevent data from the settings file
    try:
        with open(settings_flie, "r") as f:
            for line in f:
                s_item = line.split("=")
                val = s_item[1].strip()
                if s_item[0] == "s_val":
                    s_val = val
                elif s_item[0] == "c_val":
                    c_val = val
                elif s_item[0] == "g_val":
                    g_val = val
                elif s_item[0] == "b_val":
                    b_val = val
                elif s_item[0] == "x_dim":
                    x_dim = val
                elif s_item[0] == "y_dim":
                    y_dim = val
           #updated
                elif s_item[0] == "cam_num":
                    cam_num = val
                elif s_item[0] == "cam_opt":
                    cam_opt = val
                elif s_item[0] == "fsw_extra":
                    try:
                        fsw_extra = ''                  ##
                        for cmdv in s_item[1:]:         ##
                            if not cmdv == '':          ##  this just puts it
                                fsw_extra += cmdv + "=" ##  back together again
                        fsw_extra = fsw_extra[:-1]      ##
                    except:
                        print("couldn't read fsw extra commands, trying without...")
                        fsw_extra = ''
                elif s_item[0] == "uvc_extra":
                    uvc_extra = s_item[1].strip()

    except:
        print("looked at " + settings_flie)
        print("but couldn't find config file for camera, so using default values")
        print("  - Run cam_config.py to create one")
        print("     - or edit dirlocs config file to point to the config file.")
#
#
#  done to this point
#
#

    return (s_val, c_val, g_val, b_val, x_dim, y_dim, cam_num, cam_opt, fsw_extra, uvc_extra, caps_path)

# take and save photo
def take_with_uvccapture(s_val="20", c_val="20", g_val="20", b_val="20", x_dim=1600, y_dim=1200, cam_num='dev/video0', uvc_extra="", caps_path="./"):
    timenow = time.time()
    timenow = str(timenow)[0:10]
    filename= "cap_"+str(timenow)+".jpg"
    cmd  = "uvccapture -d" + cam_num
    cmd += " -S" + s_val #saturation
    cmd += " -C" + c_val #contrast
    cmd += " -G" + g_val #gain
    cmd += " -B" + b_val #brightness
    cmd += " -x" + str(x_dim) + " -y" + str(y_dim)
    cmd += " " + uvc_extra
    cmd += " -v -t0" #-v verbose, -t0 take single shot
    cmd += " -o" + caps_path + filename
    os.system(cmd)
    print("Image taken and saved to "+caps_path+filename)
    return filename

def take_with_fswebcam(s_val=None, c_val=None, g_val=None, b_val=None, x_dim=1600, y_dim=1200, cam_num='/dev/video0', fsw_extra='', caps_path="./"):
    focus_val = "10"
    timenow = time.time()
    timenow = str(timenow)[0:10]
    filename= "cap_"+str(timenow)+".jpg"

    cam_cmd  = "fswebcam -r " + str(x_dim) + "x" + str(y_dim)
    cam_cmd += " -d v4l2:" + cam_select
    cam_cmd += " -D 2"      #the delay in seconds before taking photo
    cam_cmd += " -S 5"      #number of frames to skip before taking image
    # to list controls use fswebcam -d v4l2:/dev/video0 --list-controls
    if not b_val == '':
        cam_cmd += " --set brightness=" + str(b_val)
    if not c_val == '':
        cam_cmd += " --set contrast=" + str(c_val)
    if not s_val == '':
        cam_cmd += " --set Saturation=" + str(s_val)
    if not g_val == '':
        cam_cmd += " --set gain=" + str(g_val)
    cam_cmd += " " + fsw_extra
    cam_cmd += " --jpeg 90" #jpeg quality
    # cam_cmd += ' --info "HELLO INFO TEXT"'
    cam_cmd += " " + caps_path + filename  #output filename'
    os.system(cam_cmd)
    print("Image taken and saved to " + caps_path + filename)
    return filename

if __name__ == '__main__':

    sys.path.append('/home/pi/Pigrow/scripts/')
    import pigrow_defs
    #script = 'camcap.py'  #used with logging module
    loc_locs = '/home/pi/Pigrow/config/dirlocs.txt'
    loc_dic = pigrow_defs.load_locs(loc_locs)

    s_val, c_val, g_val, b_val, x_dim, y_dim, additonal_commands, caps_path = load_camera_settings(loc_dic)
    if capture_with == "uvc":
        filename = take_with_uvccapture(s_val, c_val, g_val, b_val, x_dim, y_dim, cam_num, uvc_extra, caps_path)
    elif capture_with ==  "fs":
        filename = take_with_fswebcam(s_val, c_val, g_val, b_val, x_dim, y_dim, cam_num, uvc_extra, caps_path)
    else:
        print("You selected an invalid captuire option, use 'uvc' or 'fs'")
