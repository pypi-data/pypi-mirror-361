# no PyGameBase/cli.py

import sys
import os

def criar_projeto(nome):
    TEMPLATE = '''\
#modulos
from PyGameBase import desing as ds
import pygame
pygame.init()
#variaveis Grobais
close_control = ds.Close()
screen_loop = ds.Screen_loop("main", close_control)
#classe principal
class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((800,600),pygame.RESIZABLE)
        self.cena = 0
    def test1(self):
        for event in pygame.event.get():
            close_control.check(event)

        screen_loop.add_cena(screen=self.screen, bg_color=ds.Colors.LIGHT_GRAY, elements=[])
        pygame.time.Clock().tick(60)
        return True,self.cena
  
#chamando a classe
game = Game()
screen_loop.initiation(scene=0,scenes=[game.test1])
pygame.quit()
'''
    os.makedirs(nome, exist_ok=True)
    with open(os.path.join(nome, 'main.py'), 'w', encoding='utf-8') as f:
        f.write(TEMPLATE)
    print(f"Projeto criado em: {nome}/main.py")
def criar_projeto_em_pasta_original(nome):
    TEMPLATE = f'''\
#modulos
#projeto:{nome}
from PyGameBase import desing as ds
import pygame
pygame.init()
#variaveis Grobais
close_control = ds.Close()
screen_loop = ds.Screen_loop("main", close_control)
#classe principal
class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((800,600),pygame.RESIZABLE)
        self.cena = 0
    def test1(self):
        for event in pygame.event.get():
            close_control.check(event)

        screen_loop.add_cena(screen=self.screen, bg_color=ds.Colors.LIGHT_GRAY, elements=[])
        pygame.time.Clock().tick(60)
        return True,self.cena
  
#chamando a classe
game = Game()
screen_loop.initiation(scene=0,scenes=[game.test1])
pygame.quit()
'''
    os.makedirs(nome, exist_ok=True)
    with open('main.py', 'w', encoding='utf-8') as f:
        f.write(TEMPLATE)
    print(f"Projeto criado em: main.py")

def main():
    try:
        typefunc = sys.argv[1]
        typeoption = sys.argv[2]
    except IndexError:
        print("Use: pygamebase help --language")
        sys.exit(1)
    if typefunc == "create":
        if typeoption == "--newfolder":
           criar_projeto(sys.argv[3])
        if typeoption == "--original_folder":
            criar_projeto_em_pasta_original(sys.argv[3])
    if typefunc == "help":
        if typeoption == "--language":
            print("Use: pygamebase create --folder project_name")
            print("Use: pygamebase create --original_folder project_name (risk of overwriting)")
            print("Use: pygamebase help --language: (en-us) ||--idioma: (pt-br)")
        elif typeoption == "--idioma":
            print("Uso: pygamebase create --folder nome_do_projeto")
            print("Uso: pygamebase create --original_folder nome_do_projeto (risco de sobrescrever)")
            print("Uso: pygamebase help --language: (en-us) ||--idioma: (pt-br)")
        else:
            print("Use: pygamebase help --language: (en-us) ||--idioma: (pt-br)")
    else:
        print(f"Comando desconhecido: {typefunc}")
        sys.exit(1)

if __name__ == "__main__":
    main()
