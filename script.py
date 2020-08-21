def get_last_photos(vk_id, album, vk_token, api_version, last_date=0):
    import requests
    import json
    import math

    photo_list = []
    photo_dic = {'id': vk_id, 'contents': photo_list, 'date': 0}
    payload = {'owner_id': vk_id, 'album_id': album, 'count': 1, 'rev': 1, 'access_token': vk_token, 'v': api_version}
    r = requests.get('https://api.vk.com/method/photos.get', params=payload)
    r_json = json.loads(r.text)
    photos_count = r_json['response']['count']
    new_last_date = r_json['response']['items'][0]['date']
    photo_dic['date'] = new_last_date

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
                photo_list.append({'url': photo_url, 'id': photo_id})
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


def main():
    import telebot
    import config
    import requests
    import json
    bot = telebot.TeleBot(config.telegram_token)
    chat_id = config.tg_chat_id
    
    with open('data.json', 'r') as file:
        data = json.load(file)

    for album in data['albums']:
        vk_id = album['user_id']
        album_id = album['album_id']

        photo_dic = get_last_photos(vk_id, album_id, config.vk_token, config.api_version, last_date=album['last_date'])
        photo_list = photo_dic['contents']
        last_date = photo_dic['date']
        album['last_date'] = last_date
        vk_user = get_user_name(vk_id, config.vk_token, config.api_version)
        vk_name = vk_user['name']
        vk_domain = vk_user['domain']

        for photo in reversed(photo_list):
            photo_url = photo['url']
            photo_id = photo['id']

            text = '[%s](https://vk.com/%s?z=photo%s_%s), %s' % (vk_name, vk_domain, vk_id, photo_id, album_id)
            bot.send_photo(chat_id, photo_url, caption=text, parse_mode='MarkdownV2')
   
    with open('data.json', 'w') as file:
        json.dump(data, file)
        

if __name__ == '__main__':
    main()
