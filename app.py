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
    print('!')
    response = requests.get(map_api_url, params=map_api_params)
    with open(map_api_file, 'wb') as file:
        file.write(response.content)
    screen.blit(pygame.image.load(map_api_file), (0, 0))


def change_spn(change_type):
    spn, spn_num = map_api_params['spn'], float(map_api_params['spn'].split(',')[0])
    if change_type == '+':
        if spn_num > 0.0025:
            spn = ','.join([str(spn_num - 0.0025)] * 2)
    else:
        if spn_num < 5:
            spn = ','.join([str(spn_num + 0.0025)] * 2)

    map_api_params['spn'] = spn
    update_map()


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
            if event.key == pygame.K_PAGEUP:
                change_spn('+')
            elif event.key == pygame.K_PAGEDOWN:
                change_spn('-')

    pygame.display.flip()
pygame.quit()
os.remove(map_api_file)
