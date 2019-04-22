import os
import pygame
import requests

map_api_url = 'http://static-maps.yandex.ru/1.x/'
map_api_params = {
    'll': '37.620070,55.753630',
    'spn': '0.01,0.01',
    'size': '450,450',
    'l': 'map'
}
map_api_file = 'map.png'


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


def change_l():
    l = map_api_params['l']
    type_list = ['map', 'sat', 'sat,skl']
    type_index = type_list.index(l)
    map_api_params['l'] = type_list[(type_index + 1) % 3]


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
            # Изменение типа
            elif event.key == pygame.K_t:
                change_l()
            update_map()
    pygame.display.flip()
pygame.quit()
os.remove(map_api_file)
