import requests
import json

with open ('tokens.txt') as keys:      # первая строка - токен VK, вторая строка - токен Yandex Disk
    YD_token = keys.readline().strip()
    VK_token = keys.readline().strip()

def yd_functions(command):
    url = 'https://cloud-api.yandex.net/v1/disk/resources'
    headers = {'Content-Type': 'application/json', 'Accept': 'application/json', 'Authorization': f'OAuth {YD_token}'}
    if command == 'make folder':
        res = requests.put(f'{url}?path={folder}&overwrite=False', headers= headers).json()
    elif command == 'save file':
        res = requests.post(f'{url}/upload?url={file_url}&path={file_name}&overwrite=True', headers=headers).json()
    return res

def get_photo_data(album,count):
	ph_data = requests.get("https://api.vk.com/method/photos.get", params = { 
		#'owner_id': vk_user_id,
		'access_token': VK_token,
        'album_id': album,
		'count': count,
        'extended': '1',
		'photo_sizes': '1',
		'v': 5.131
	}).json()
	return ph_data      

def save_info_file(data):
    with open("backup_info.json", "w") as write_file:  
        json.dump(data, write_file)

# ********** main program ***************        
i = 0
num_photos = 5
names = []
out_data = []
bar_length = 15    
folder = 'VK backup'
photo_source = 'profile' # 'wall' 'saved'

yd_functions('make folder')

photo_data = get_photo_data(photo_source,num_photos)
photo_count = photo_data['response']['count']   # количество фотографий в альбоме
if num_photos > photo_count:
    print(f'В папке {photo_source} содержится только {photo_count} фото, а запрошено {num_photos}')
for files in photo_data["response"]["items"]:
    file_size = files["sizes"][-1]["type"]      
    file_url = files["sizes"][-1]["url"]        # последний тип файла в массиве - самый большой
    file_url = file_url.replace('&','%26')
    num_likes = str(files['likes']['count'])     
    filename = ((file_url.split("/")[-1]).split('?')[0]).split('.')
    if num_likes in names: 
        filename[0] = f'{folder}/{num_likes}' + str(files['date'])   #если есть фото с таким же кол-вом лайков, добавляем дату
    else: 
        filename[0] = f'{folder}/{num_likes}'
    file_name = '.'.join(filename)
    names.append(num_likes)
    out_data.append({'file_name':file_name, 'size':file_size })
    
    res = yd_functions('save file')         # запись файла на ЯД

    if 'error' not in (res):
        i +=1
        step = bar_length // num_photos             # ******************
        progress = step * i                         # расчёт статус-бара
        space = bar_length - progress               #
        progress_bar = '▄'*progress + '_'*space     # ******************
        print (f'файл {file_name} сохранён {progress_bar}')
    else: 
        print(res['error'])
    
save_info_file(out_data)    # сохраняем информацию о скопированных фото 
