import requests
import shutil
import time

cookies = {
    '_ym_uid': '15499019871023134972',
    '_ym_d': '1549901987',
    '_ym_isad': '1',
    'sessionId': '2743ac3e-91be-c47a-dd14-cd5c96045841',
    'pageSize': '10',
}

headers = {
    'DNT': '1',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'en-US,en;q=0.9,ru-RU;q=0.8,ru;q=0.7,so;q=0.6',
    'X-Compress': 'null',
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36',
    'Accept': 'image/webp,image/apng,image/*,*/*;q=0.8',
    'Referer': 'http://os.fipi.ru/tasks/2/a',
    'Connection': 'keep-alive',
}

imgs = 0
total = 322

def save_image(path):
    global imgs
    global total

    print(f'Downloading image {imgs} / {total}')
    response = requests.get(f'http://os.fipi.ru/{path}', headers=headers, cookies=cookies, stream=True)
    res = f'tasks/{imgs}.png'
    with open(res, 'wb') as out_file:
        shutil.copyfileobj(response.raw, out_file)
    time.sleep(1)
    imgs += 1
    return res

if __name__ == '__main__':
    save_image('docs/7180F95137BF9FEF48092553403ECAB5/questions/24228C6E5E7FAE754B9C53C23E226726/xs3qstsrc24228C6E5E7FAE754B9C53C23E226726_1_1385550035.png')
    save_image('docs/7180F95137BF9FEF48092553403ECAB5/questions/24228C6E5E7FAE754B9C53C23E226726/xs3qstsrc24228C6E5E7FAE754B9C53C23E226726_1_1385550035.png')
