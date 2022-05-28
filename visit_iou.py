import pandas as pd
import numpy as np
import glob
import copy
from deep_sort.sort.tracker import custom_labels


def df_file(save_txt_path): 
    txt_path = save_txt_path

    # 저장된 텍스트 파일 가져오기
    file_list = glob.glob(txt_path)
    file_list_py = [file for file in file_list if file.endswith(".txt")]

    # 텍스트 파일을 데이터 프레임 형태로 불러오기
    file = pd.read_table(file_list_py[0], header=None, names=['frame','track_id','bbox_left','bbox_top','w','h','cx','cy','2','3','4'], sep=' ')
    return file
   

def IoU(box1, box2):
    # box = (lx, ly, w, h)
    box1_area = (box1[4]) * (box1[5])
    box2_area = (box2[4]) * (box2[5])

    # obtain x1, y1, x2, y2 of the intersection
    x1 = max(box1[2], box2[2])
    y1 = max(box1[3], box2[3])
    x2 = min(box1[2]+box1[4], box2[2]+box1[4])
    y2 = min(box1[3]+box1[5], box2[3]+box1[5])

    # compute the width and height of the intersection
    w = max(0, x2 - x1 + 1)
    h = max(0, y2 - y1 + 1)

    inter = w * h
    iou = inter / (box1_area + box2_area - inter)
    return iou


def analysis(save_txt_path):
	file = df_file(save_txt_path)
	file.drop(['2','3','4'], inplace=True, axis=1)

	stay_frame = 0
	visit_time = 0
	time_list = []


	for i in range(len(custom_labels)):
	    ### 각 클래스 별로 불러오기
	    class_id = (file.track_id == i+1)
	    # class_file : 클래스 별 필요한 전체 정보
	    class_file = file[class_id]
	    # frame : frame 정보만 가져옴
	    frame = class_file.drop(['track_id','bbox_left','bbox_top','w','h','cx','cy'], inplace=False, axis=1)
	    # df의 인덱싱을 위해 인덱스 초기화
	    class_file.reset_index(level=None, drop=True, inplace=False, col_level=0, col_fill='')
	    frame.reset_index(level=None, drop=True, inplace=False, col_level=0, col_fill='')
	    np_class_file = class_file.to_numpy()

	    ### 프레임 별로 분석
	    for j in range(len(class_file)):
	        if ((j+1)>= len(class_file)):
	            break
	        
	        this_frame = frame.iloc[j,0]
	        next_frame = frame.iloc[j+1,0]

	        pet = np_class_file[j]
	        next_pet = np_class_file[j+1]
	        # 임의로 지정, 웹에서 받아와야 함
	        place = [0, 0, 300, 347, 281, 172]
	        iou = IoU(pet, place)
	        next_iou = IoU(next_pet, place)
	        if(iou > 0.2):
	            stay_frame += 1
	            if((this_frame+1 == next_frame) & (next_iou < 0.2)):
	                visit_time+=1
	            elif(this_frame+1 != next_frame):
	                visit_time+=1
	            
	    stay_time = stay_frame / 60
	    time_list.append(stay_time)
	    time_list.append(visit_time)
	    stay_frame = 0
	    stay_time = 0
	    visit_time = 0  
	# print("까망 머문시간, 까망 횟수, 루비 머문시간, 루비 횟수")
	# print(time_list)
	return(time_list)
