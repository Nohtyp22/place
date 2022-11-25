import requests
import json
# import time
# from tqdm import tqdm

def init_access_keys():
    with open ('tokens.txt') as keys:      # первая строка - токен VK, вторая строка - токен Yandex Disk
        yandex = keys.readline().strip()
        vk = keys.readline().strip()
    return yandex, vk

def yd_functions(command,*params):
    global msg_log
    file_url = params[0]
    file_name = params[1]
    url = 'https://cloud-api.yandex.net/v1/disk/resources'
    headers = {'Content-Type': 'application/json', 'Accept': 'application/json', 'Authorization': f'OAuth {YD_token}'}
    if command == 'make folder':
        res = requests.put(f'{url}?path={FOLDER}&overwrite=False', headers= headers).json()
    elif command == 'save file':
        res = requests.post(f'{url}/upload?url={file_url}&path={file_name}&overwrite=True', headers=headers).json()
    if 'error' in res: 
        msg_log += res['message']+'\n'
        return False
    else:
        return True

def get_photo_data(album,count):
    data = requests.get('https://api.vk.com/method/photos.get', params = { 
		#'owner_id': vk_user_id,
		'access_token': VK_token,
        'album_id': album,
		'count': count,
        'extended': '1',
		'photo_sizes': '1',
		'v': 5.131 
	}).json()
    if 'error' in data:
        status = False
    else:
        status = True 
    return status, data      

def processing_photos_data(photo_data):
    global msg_log
    names = []
    out_data = []
    photo_count = photo_data['response']['count']   # количество фотографий в альбоме
    if NUM_photos > photo_count:
        msg_log += (f' В папке {ALBUM} содержится только {photo_count} фото, а запрошено {NUM_photos}, \n' )
    for files in photo_data['response']['items']:
        file_size = files['sizes'][-1]['type']      
        file_url = files['sizes'][-1]['url']        # последний тип файла в массиве - самый большой
        file_url = file_url.replace('&','%26')
        num_likes = str(files['likes']['count'])     
        filename = ((file_url.split('/')[-1]).split('?')[0]).split('.')
        if num_likes in names: 
            filename[0] = f'{FOLDER}/{num_likes}' + str(files['date'])   #если есть фото с таким же кол-вом лайков, добавляем дату
        else: 
            filename[0] = f'{FOLDER}/{num_likes}'
        file_name = '.'.join(filename)
        names.append(num_likes)
        out_data.append({'file_name':file_name, 'size':file_size })
        if yd_functions('save file',file_url,file_name) is True:        # запись файла на ЯД
            msg_log += (f' Файл {file_name} сохранён на диске Yandex, \n')
    return out_data

def save_info_file(data, file_name, type):
    with open(file_name, 'w') as write_file:  
        if type == 'j':
            json.dump(data, write_file)
        elif type == 't': 
            write_file.writelines(data)

def progress_bar():
    global bar_counter
    print('\r', end='')
    progress = BAR_step * bar_counter               
    space = BAR_length - progress               
    progress_bar = '▓'*progress + '_'*space    
    print (progress_bar, end='')
    bar_counter +=1

# ********** main program ***************        
NUM_photos = 5
FOLDER = 'VK backup'
ALBUM = 'profile' # 'wall' 'saved'
msg_log = ''
BAR_length = 21 
BAR_step = 3 
bar_counter = 0

progress_bar() # 0
YD_token, VK_token = init_access_keys()
progress_bar()   # 1
if yd_functions('make folder','','') is True:
    msg_log += f'Папка {FOLDER} на диске Yandex создана успешно,\n'
progress_bar()   # 2
status, raw_data = get_photo_data(ALBUM,NUM_photos)
if status is True:
    progress_bar() # 3
    inf_data = processing_photos_data(raw_data)
    progress_bar() # 4
    save_info_file(inf_data,'backup_info.json','j')    # сохраняем информацию о скопированных фото 
    progress_bar() # 5
else: 
    msg_log +='Ошибка VK:'+raw_data['error']['error_msg']+'\n'
progress_bar()   # 6
save_info_file(msg_log,'log.txt','t')         # сохраняем log файл
progress_bar()   # 7
print (' Информация о файлах сохранена в backup_info.json, лог программы в файле log.txt')