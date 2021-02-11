def get_last_photos(vk_id, album, vk_token, api_version, last_date=0):
    import requests
    import json
    import math

    photo_list = []
    photo_dic = {'id': vk_id, 'contents': photo_list}
    payload = {'owner_id': vk_id, 'album_id': album, 'count': 1, 'rev': 1, 'access_token': vk_token, 'v': api_version}
    r = requests.get('https://api.vk.com/method/photos.get', params=payload)
    r_json = json.loads(r.text)
    photos_count = r_json['response']['count']

    for sen in range(math.ceil(photos_count / 1000)):
        payload['count'] = 1000
        payload['offset'] = 1000 * sen
        r = requests.get('https://api.vk.com/method/photos.get', params=payload)
        r_json = json.loads(r.text)
        for photo in r_json['response']['items']:
            new_date = photo['date']
            if new_date > last_date:
                photo_url = photo['sizes'][-1]['url']
                photo_id = photo['id']
                if photo_url is not None:
                    photo_list.append({'url': photo_url, 'id': photo_id, 'date': new_date})
            else:
                return(photo_dic)
    return(photo_dic)


def get_user_name(vk_id, vk_token, api_version):
    import requests
    import json
    payload = {'user_ids': vk_id, 'access_token': vk_token, 'v': api_version, 'fields': 'domain'}
    r = requests.get('https://api.vk.com/method/users.get', params=payload)
    r_json = json.loads(r.text)
    f_name = r_json['response'][0]['first_name']
    l_name = r_json['response'][0]['last_name']
    domain = r_json['response'][0]['domain']
    full_name = "%s %s" % (f_name, l_name)

    return({'name': full_name, 'domain': domain})


def write_log(text):
    with open('log.txt', 'a+') as file:
        file.write("%s\n" % text)
    print(text)


def main(bot):
    with open('data.json', 'r') as file:
        data = json.load(file)

    for album in data['albums']:
        vk_id = album['user_id']
        album_id = album['album_id']

        photo_dic = get_last_photos(vk_id, album_id, config.vk_token, config.api_version, last_date=album['last_date'])
        photo_list = photo_dic['contents']
        vk_user = get_user_name(vk_id, config.vk_token, config.api_version)
        vk_name = vk_user['name']
        vk_domain = vk_user['domain']

        for photo in reversed(photo_list):
            photo_url = photo['url']
            photo_id = photo['id']
            photo_date = photo['date']
            text = '[%s](https://vk.com/%s?z=photo%s_%s), %s' % (vk_name, vk_domain, vk_id, photo_id, album_id)
            try:
                bot.send_photo(chat_id, photo_url, caption=text, parse_mode='MarkdownV2')
            except telebot.apihelper.ApiException:
                write_log('[400] %s' % (photo_url))
            else:
                write_log('[SUCC] %s' % (text))
                last_date = photo_date
                album['last_date'] = last_date
                with open('data.json', 'w') as file:
                    json.dump(data, file)
            time.sleep(4)
   

if __name__ == '__main__':
    import telebot
    import config
    import requests
    import json
    import time
    import time
    import requests
    bot = telebot.TeleBot(config.telegram_token)
    chat_id = config.tg_chat_id
    while True:
        try:
            main(bot)
        except requests.exceptions.ConnectionError:
            write_log('[ERR] Connection error')
            time.sleep(240)
        except Exception as e:
            write_log('[ERR] %s' % (e))
            time.sleep(3540)
        time.sleep(60)
