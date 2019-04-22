import os
import pygame
import requests

rus_alphabet = [let for let in 'йцукенгшщзхъфывапролджэячсмитьбюЙЦУКЕНГШЩЗХЪФЫВАПРОЛДЖЭЯЧСМИТЬБЮ1234567890,.']
map_api_url = 'http://static-maps.yandex.ru/1.x/'
map_api_params = {
    'll': '37.620070,55.753630',
    'spn': '0.01,0.01',
    'size': '450,450',
    'l': 'map'
}
map_api_file = 'map.png'
session_storage = {
    'show_postal_code': False,
    'postal_code': '',
    'text': '',
    'full_address': ''
}


def interface_draw():
    screen.blit(pygame.image.load(map_api_file), (0, 0))
    # Строка полного адреса
    pygame.draw.rect(screen, (255, 255, 255), (15, 10, 382, 32), 0)
    if session_storage['full_address']:
        address_text = pygame.font.Font(None, 15).render(
            session_storage['full_address'], 1, (150, 150, 150)
        )
        screen.blit(address_text, (25, 21))
    # Кнопка включения показа почтового индекса
    pygame.draw.circle(screen, (255, 255, 255), (30, 62), 15)
    if session_storage['show_postal_code']:
        pygame.draw.circle(screen, (255, 64, 64), (30, 62), 7)
        pygame.draw.rect(screen, (255, 255, 255), (55, 49, 200, 26), 0)
        post_index_text = pygame.font.Font(None, 18).render(
            session_storage['postal_code'], 1, (150, 150, 150)
        )
        screen.blit(post_index_text, (58, 58))
    # Кнопка сброса
    pygame.draw.circle(screen, (255, 255, 255), (424, 26), 16)
    pygame.draw.circle(screen, (255, 64, 64), (424, 26), 16, 2)
    reset_text = pygame.font.Font(None, 20).render(
        'res', 1, (255, 64, 64)
    )
    screen.blit(reset_text, (414, 20))
    # Поисковая строка
    pygame.draw.rect(screen, (255, 255, 255), (15, 400, 420, 40), 0)
    if session_storage['text']:
        search_text = pygame.font.Font(None, 22).render(
            session_storage['text'], 1, (0, 0, 0)
        )
    else:
        search_text = pygame.font.Font(None, 22).render(
            'Поиск...', 1, (200, 200, 200))
    screen.blit(search_text, (25, 412))


def update_map():
    response = requests.get(map_api_url, params=map_api_params)
    with open(map_api_file, 'wb') as file:
        file.write(response.content)


def change_spn(change_type):
    spn = map_api_params['spn']
    spn_num = float(map_api_params['spn'].split(',')[0])
    if change_type == '+':
        if spn_num > 0.01:
            spn = ','.join([str(spn_num - 0.01)] * 2)
    elif change_type == '-':
        if spn_num < 10:
            spn = ','.join([str(spn_num + 0.01)] * 2)
    map_api_params['spn'] = spn
    update_map()


def change_ll(change_type):
    spn_num = float(map_api_params['spn'].split(',')[0])
    ll_nums = [float(num) for num in map_api_params['ll'].split(',')]

    if change_type == 'up':
        ll_nums[1] += 0.5 * spn_num
    elif change_type == 'right':
        ll_nums[0] += 0.5 * spn_num
    elif change_type == 'down':
        ll_nums[1] -= 0.5 * spn_num
    elif change_type == 'left':
        ll_nums[0] -= 0.5 * spn_num
    ll = ','.join([str(num) for num in ll_nums])
    map_api_params['ll'] = ll
    update_map()


def change_l():
    l = map_api_params['l']
    type_list = ['map', 'sat', 'sat,skl']
    type_index = type_list.index(l)
    map_api_params['l'] = type_list[(type_index + 1) % 3]
    update_map()


def add_point():
    coords = get_info_by_name(session_storage['text'], 'pos')
    session_storage['full_address'] = get_info_by_name(
        session_storage['text'], 'full_address'
    )
    session_storage['postal_code'] = get_info_by_name(
        session_storage['text'], 'post_index'
    )
    col = 'bl'
    map_api_params['pt'] = '{},pm2{}m'.format(coords, col)
    map_api_params['ll'] = coords
    update_map()


def del_point():
    if 'pt' in map_api_params.keys():
        del map_api_params['pt']
        session_storage['text'] = ''
    session_storage['full_address'] = ''
    session_storage['postal_code'] = ''
    update_map()


def get_info_by_name(obj_address, info_type):
    geocoder_api_server = 'https://geocode-maps.yandex.ru/1.x/'
    geocoder_params = {
        'geocode': obj_address,
        'format': 'json'
    }
    res = requests.get(geocoder_api_server, params=geocoder_params)
    if res:
        json_res = res.json()
        geo_obj = json_res['response']['GeoObjectCollection']['featureMember'][0]['GeoObject']

        if info_type == 'pos':
            return geo_obj['Point']['pos'].replace(' ', ',')
        elif info_type == 'full_address':
            return geo_obj['metaDataProperty']['GeocoderMetaData']['text']
        elif info_type == 'post_index':
            try:
                return geo_obj['metaDataProperty']['GeocoderMetaData']['AddressDetails']['Country']['AdministrativeArea']['SubAdministrativeArea']['Locality']['Thoroughfare']['Premise']['PostalCode']['PostalCodeNumber']
            except Exception:
                session_storage['show_postal_code'] = False
                return ''
    return None


pygame.init()
screen = pygame.display.set_mode((450, 450))
pygame.display.flip()

running = True
update_map()
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            # Изменение размера
            if event.key == pygame.K_PAGEUP:
                change_spn('+')
            elif event.key == pygame.K_PAGEDOWN:
                change_spn('-')
            # Изменение положения
            elif event.key == pygame.K_UP:
                change_ll('up')
            elif event.key == pygame.K_RIGHT:
                change_ll('right')
            elif event.key == pygame.K_DOWN:
                change_ll('down')
            elif event.key == pygame.K_LEFT:
                change_ll('left')
            # Изменение типа карты
            elif event.key == pygame.K_F1:
                change_l()
            # Работа с поисковой строкой
            elif (event.unicode in rus_alphabet
                  and len(session_storage['text']) <= 50):
                session_storage['text'] += event.unicode
            elif event.key == 8 and len(session_storage['text']) > 0:
                session_storage['text'] = session_storage['text'][:-1:]
            elif event.key == 13:
                add_point()
        # Работа с кнопкой res
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            if 408 <= mouse_pos[0] <= 440 and 10 <= mouse_pos[1] <= 42:
                del_point()
            elif 15 <= mouse_pos[0] <= 45 and 47 <= mouse_pos[1] <= 77:
                session_storage['show_postal_code'] = not session_storage['show_postal_code']
    # Отрисовка интерфейса
    interface_draw()
    pygame.display.flip()
pygame.quit()
os.remove(map_api_file)
