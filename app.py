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
    'text': ''
}


def controls_draw():
    # Кнопка сброса
    pygame.draw.circle(screen, (255, 255, 255), (423, 27), 18)
    pygame.draw.circle(screen, (255, 64, 64), (422, 28), 18, 2)
    reset_text = pygame.font.Font(None, 20).render(
        'res', 1, (255, 64, 64)
    )
    screen.blit(reset_text, (412, 22))
    # Поисковая строка
    pygame.draw.rect(screen, (255, 255, 255), (15, 400, 420, 40), 0)
    if session_storage['text']:
        sign = pygame.font.Font(None, 22).render(
            session_storage['text'], 1, (0, 0, 0)
        )
    else:
        sign = pygame.font.Font(None, 22).render(
            'Поиск...', 1, (200, 200, 200))
    screen.blit(sign, (25, 412))


def update_map():
    response = requests.get(map_api_url, params=map_api_params)
    with open(map_api_file, 'wb') as file:
        file.write(response.content)
    screen.blit(pygame.image.load(map_api_file), (0, 0))


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
    coords = get_coord_by_name(session_storage['text'])
    col = 'bl'
    map_api_params['pt'] = '{},pm2{}m'.format(coords, col)
    map_api_params['ll'] = coords
    update_map()


def del_point():
    if map_api_params['pt']:
        del map_api_params['pt']
    update_map()


def get_coord_by_name(obj_name):
    geocoder_api_server = 'https://geocode-maps.yandex.ru/1.x/'
    geocoder_params = {'geocode': obj_name, 'format': 'json'}
    res = requests.get(geocoder_api_server, params=geocoder_params)
    if res:
        json_res = res.json()['response']['GeoObjectCollection']
        geo_obj = json_res['featureMember'][0]['GeoObject']
        return geo_obj['Point']['pos'].replace(' ', ',')


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
            if 405 <= mouse_pos[0] <= 445 and 9 <= mouse_pos[1] <= 45:
                del_point()
    # Отрисовка интерфейса
    controls_draw()
    pygame.display.flip()
pygame.quit()
os.remove(map_api_file)
