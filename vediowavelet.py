import os
import glob
import sys
import numpy as np
import pywt
import cv2
import time
from multiprocessing import Pool

import argparse

def run_wavelet(vid_item):
    vid_path = vid_item[0]
    vid_id = vid_item[1]
    #read vedio
    video = cv2.VideoCapture(vid_path)  
    vid_name = vid_path.split('/')[-1].split('.')[0]
    out_full_path = os.path.join(out_path, vid_name)
    fcount = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
    try:
        os.mkdir(out_full_path)
    except OSError:
        pass
    for i in xrange(fcount):
        ret, frame = video.read()
        #RGB images wavelet transform on separate channels
        if ret:
            LL_R, (LH_R, HL_R, HH_R) = pywt.dwt2(frame[:, :, 0], 'bior4.4')
            LL_G, (LH_G, HL_G, HH_G) = pywt.dwt2(frame[:, :, 1], 'bior4.4')
            LL_B, (LH_B, HL_B, HH_B) = pywt.dwt2(frame[:, :, 2], 'bior4.4')
            LL = np.dstack((LL_R, LL_G, LL_B))
            LH = np.dstack((LH_R, LH_G, LH_B))
            HL = np.dstack((HL_R, HL_G, HL_B))
            cv2.imwrite('{}/LL_{:05d}.jpg'.format(out_full_path, i), LL)#approximation
            cv2.imwrite('{}/HL_{:05d}.jpg'.format(out_full_path, i), LH)#horizonal detail
            cv2.imwrite('{}/LH_{:05d}.jpg'.format(out_full_path, i), HL)#vertical detail
        else:
            logging.debug('{} error:{}/{}'.format(vid_name, i, fcount))
    print '{} {} done'.format(vid_id, vid_name)
    sys.stdout.flush()
    return True

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="extract wavelet")
    parser.add_argument("src_dir")
    parser.add_argument("out_dir")
    parser.add_argument("--num_worker", type=int, default=3)
    parser.add_argument("--ext", type=str, default='avi', choices=['avi','mp4'], help='video file extensions')
    parser.add_argument("--new_width", type=int, default=340, help='resize image width')
    parser.add_argument("--new_height", type=int, default=256, help='resize image height')

    args = parser.parse_args()

    out_path = args.out_dir
    src_path = args.src_dir
    num_worker = args.num_worker
    ext = args.ext
    new_size = (args.new_width, args.new_height)

    if not os.path.isdir(out_path):
        os.makedirs(out_path)

    starttime = time.time()
    #list /*/* depend on the directory structure of your project(this is according to UCF101)
    vid_list = glob.glob(src_path + '/*/*.' + ext)
    print len(vid_list)
    #multiprocessing
    pool = Pool(num_worker)
    pool.map(run_wavelet, zip(vid_list, xrange(len(vid_list))))
    endtime = time.time()
    print "cocurrent time:", int(endtime - starttime)