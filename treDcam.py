import threading    # Create a context object. This object owns the handles to all connected realsense devices
import pyrealsense2 as rs
import numpy as np
import Salva
import time
import synchronizer
import traceback

def Photo(e,tred,token,flag):
    try:
        
        pipe = rs.pipeline()
        color=rs.colorizer()
        ctx=rs.context()
        dev=ctx.query_devices()
        i=0
        while True:
            if dev[i].get_info(rs.camera_info(14))==tred["IP"]:
                break
            i=i+1
            if i==len(dev):
                raise Exception('This camera is not avaiable')

        tred["IP"]=dev[0].get_info(rs.camera_info(14))
        
        print("3D cam started.")
        #tempo=time.time()
        # Getting the depth sensor's depth scale (see rs-align example for explanation)
        while e.is_set():
            if(synchronizer.Synchro(token)==1):
                try:
                    pipe.start()
                    # This call waits until a new coherent set of frames is available on a device
                    # Calls to get_frame_data(...) and get_frame_timestamp(...) on a device will return stable values until wait_for_frames(...) is called
                    frames = pipe.wait_for_frames()
                    depth_frame = frames.get_depth_frame()
                    #if depth_frame and (tempo+0.5)<time.time():
                    
                    filename="depth_image_%d" % (tred["acquiredImages"]+1)
                    if(flag==1):
                        depth_col=color.colorize(depth_frame)
                        depth_data = np.asanyarray(depth_col.get_data())
                        Salva.Salva(filename, depth_data)
                    else:
                        depth_data = np.asanyarray(depth_frame.get_data())
                        Salva.Salvabn(filename, depth_data)
                    print("immagine 3d")
                    tred["acquiredImages"]=tred["acquiredImages"]+1
                    tred["timestamp"]=str(time.gmtime().tm_year)+"-"+str(time.gmtime().tm_mon)+"-"+str(time.gmtime().tm_mday)+"T"+str(time.gmtime().tm_hour)+":"+str(time.gmtime().tm_min)+":"+str(time.gmtime().tm_sec)
                    pipe.stop()
                    synchronizer.Update()
                    #tempo=time.time()
                except Exception as exc:
                    tred["error"]=str(exc) 
                    synchronizer.Update()     
        
    except Exception as err:
        tred["error"]=str(err)
        tred["status"]="error"
        synchronizer.removefromQueue(token)
        e.clear()