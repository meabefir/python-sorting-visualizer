import pygame
import random
import time
import datetime

colors = {'white': (255, 255, 255), 'black': (0, 0, 0), 'red': (255, 0, 0), 'blue': (0, 0, 255), 'green': (0, 255, 0),'yellow':(0,255,255)}

window_height = 500
window_width = 1000
cell_height = 30
cell_width = 150
margin = 10

pygame.init()
screen = pygame.display.set_mode((window_width, window_height),pygame.RESIZABLE)
pygame.display.set_caption('sorting visualizer')
#font = pygame.font.Font('freesansbold.ttf', 16)
font = pygame.font.SysFont('calibri', 23)

class Text():
    def set_text_size(self, text):
        text_rect = text.get_rect()
        return ((text_rect[2] - text_rect[0], text_rect[3] - text_rect[1]))

    def draw_text(self, text_render, x_off=0, y_off=0, color=colors['black'], centered=1):
        if not isinstance(text_render, pygame.Surface):
            if type(text_render) is type([]):
                text_render = " ".join([str(el.name) for el in text_render])
                text_render = font.render(text_render, True, color)
            else:
                text_render = font.render(str(text_render), True, color)
        text_size = self.set_text_size(text_render)
        screen.blit(text_render,
                    (self.x - (text_size[0] // 2) * centered + x_off, self.y - (text_size[1] // 2) * centered + y_off))


class Debug():
    def run(self, event):
        # alway run
        # print(mouse.mouse_over)

        # kb input
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_m:
                print(mouse.mouse_over)


class Mouse():
    def __init__(self):
        self.x = 0
        self.y = 0
        self.left_pressed = False
        self.middle_pressed = False
        self.right_pressed = False
        self.mouse_over = None

    def update(self, new_pos, mb_states):
        self.x, self.y = new_pos
        self.left_pressed, self.middle_pressed, self.right_pressed = mb_states
        for gui_el in reversed(gui.gui_elements):
            if gui_el.mouse_over:
                mouse.mouse_over = gui_el
                break
        else:
            mouse.mouse_over = None

    def click(self):
        if mouse.mouse_over is not None and mouse.mouse_over.clickable:
            mouse.mouse_over.simulate_click()


class GUI():
    scopes = {'Menu': [{'Sort Type': ['Brute Force', 'Bubble Sort', 'Quick Sort','Radix Sort', 'Bogo Sort']},
                       {'Set Options': ['Randomize Set', 'Bigger Set', 'Smaller Set', 'Bigger Range',
                                        'Smaller Range']}]}
    menu = None

    def __init__(self):
        self.gui_elements = []
        self.init_gui_elements()

    def update(self):
        for el in self.gui_elements:
            el.draw_self()

    def init_gui_elements(self):
        self.create_gui_element((screen.get_width() - margin * 5 - cell_width, margin),
                               (screen.get_width() - margin, screen.get_height() - margin), 'Menu', False)
        GUI.menu = self.gui_elements[0]

        current_height = margin + cell_height
        for level, sub_menus in enumerate(GUI.scopes['Menu']):
            for sub_menu, content in sub_menus.items():
                self.create_gui_element(
                    (screen.get_width() - margin * 4 - cell_width, current_height),
                    (screen.get_width() - margin * 2, current_height + margin + (cell_height) * (1 + len(content))), sub_menu,
                    False)
                current_height += cell_height

                for option in content:
                    self.create_gui_element(
                        (screen.get_width() - margin * 3 - cell_width, current_height),
                        (screen.get_width() - margin * 3, current_height + (cell_height)), option, True)
                    current_height += cell_height
                current_height += 2 * margin

    def create_gui_element(self,pos1, pos2, name, clickable):
        self.gui_elements.append(GUIElement(pos1, pos2, name, clickable))


class GUIElement(Text):
    default_color = colors['white']
    highlight_color = colors['red']

    def __init__(self, pos1, pos2, name, clickable):
        self.clickable = clickable
        self.name = name
        self.x, self.y = pos1
        self.x_end, self.y_end = pos2
        self.width = self.x_end - self.x
        self.height = self.y_end - self.y
        self.mouse_over = False
        self.color = self.default_color

    def draw_self(self):
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height), 1)
        self.draw_text(self.name, self.width // 2, cell_height // 2, colors['white'])

    def update(self):
        # if mouse over self
        if self.x_end > mouse.x > self.x and self.y_end > mouse.y > self.y:
            self.mouse_over = True
            if self.clickable:
                self.color = self.highlight_color
        else:
            self.mouse_over = False
            self.color = self.default_color
        # if moved mouse, menu gets update so all get updated
        if self is GUI.menu:
            for gui_el in gui.gui_elements:
                if gui_el is not self:
                    gui_el.update()

    def simulate_click(self):
        number_set.sorting = False

        if self.name == 'Bigger Set':
            number_set.increase_size()
        elif self.name == 'Smaller Set':
            number_set.decrease_size()
        elif self.name == 'Bigger Range':
            number_set.increase_range()
        elif self.name == 'Smaller Range':
            number_set.decrease_range()
        elif self.name == 'Randomize Set':
            number_set.init_set()
        elif self.name == 'Brute Force':
            number_set.sort(number_set.brute_force)
        elif self.name == 'Bubble Sort':
            number_set.sort(number_set.bubble_sort)
        elif self.name == 'Quick Sort':
            number_set.sort(number_set.quick_sort)
        elif self.name == 'Merge Sort':
            number_set.sort(number_set.merge_sort)
        elif self.name == 'Bogo Sort':
            number_set.sort(number_set.bogo_sort)
        elif self.name == 'Radix Sort':
            number_set.sort(number_set.radix_sort)


class NumberSet(Text):

    def __init__(self):
        self.range = 100
        self.size = 100
        self.max_size = 300
        self.x_pad = 6 * margin
        self.y_pad = 12 * margin
        self.width = screen.get_width() - GUI.menu.width - self.x_pad
        self.bar_width = self.width / self.size
        self.height = screen.get_height() - self.y_pad
        self.x = self.x_pad // 2
        self.y = self.y_pad // 2
        self.x_end = self.x + self.width
        self.y_end = self.y + self.height
        self.bars = []
        self.short_delay = 10000
        self.long_delay = 10000
        self.iteration_delay = self.short_delay
        self.last_iteration = datetime.datetime.today()
        self.sorting = False
        self.sort_start = None
        self.sort_end = None

        self.init_set()

    def init_set(self):
        # self.set = random.sample(population=range(self.range[0],self.range[1]),k=self.size)
        self.set = [random.randint(0, self.range) for i in range(self.size)]
        self.bar_width = self.width / self.size

        # create bars and append to bar list
        self.create_bars_from_set()

    def create_bars_from_set(self,calc_max = 1):
        if calc_max:
            self.max = max(self.set)
        self.bars = []
        for i, nr in enumerate(self.set):
            bar_height = (nr / self.max) * self.height
            bar_x = int(self.x + i * self.bar_width)
            bar_y = int(self.y_end - bar_height)
            new_bar = NumberBar(bar_x, bar_y, int(self.bar_width), int(bar_height), nr)
            self.bars.append(new_bar)

    def update(self):
        self.iterate_sort()

        self.draw_info()
        self.draw_bars()

    def draw_info(self):
        self.draw_text(f'Set size: {self.size}', 0, -20, colors['white'], 0)
        self.draw_text(f'Set range: {self.range}', 0, -40, colors['white'], 0)
        if self.sort_start is not None and self.sorting:
            seconds = (datetime.datetime.today() - self.sort_start).seconds
            microseconds = (datetime.datetime.today() - self.sort_start).microseconds
            self.draw_text(f'Time elapsed: {seconds}.{microseconds // 10000}s', 120, -20, colors['white'], 0)
        elif self.sort_end is not None:
            seconds = (self.sort_end - self.sort_start).seconds
            microseconds = (self.sort_end - self.sort_start).microseconds
            self.draw_text(f'Time elapsed: {seconds}.{microseconds // 10000}s', 120, -20,
                           colors['white'], 0)
        pygame.draw.rect(screen, colors['white'], (self.x, self.y, self.width, self.height), 1)

    def draw_bars(self):
        for bar in self.bars:
            bar.draw_self()

    def iterate_sort(self):
        if self.sorting:
            now = datetime.datetime.now()
            if (now - self.last_iteration).microseconds > self.iteration_delay:
                self.last_iteration = now
                try:
                    try:
                        pos1,pos2,color = next(self.sorter)
                        if color == colors['red']:
                            self.iteration_delay = self.long_delay
                        else:
                            self.iteration_delay = self.short_delay
                        self.create_bars_from_set(0)

                        self.bars[pos1].set_color(color)
                        self.bars[pos2].set_color(color)
                    except Exception as e:
                        print(e)
                        next(self.sorter)
                        self.create_bars_from_set(0)
                except:
                    print("GOT OUT")
                    self.sorting = False
                    for bar in self.bars:
                        bar.reset_color()
                    self.sort_end = datetime.datetime.today()

    def sort(self, sort_type):
        self.sorter = sort_type()
        self.sorting = True
        self.sort_start = datetime.datetime.today()

    def brute_force(self):
        if self.sorted(self.set): return
        l = len(self.set)
        for i in range(0, l):
            for j in range(i + 1, l):
                if self.set[i] > self.set[j]:
                    self.set[i], self.set[j] = self.set[j], self.set[i]
                    yield (i,j,colors['red'])
                else:
                    yield (i,j,colors['yellow'])

    def bubble_sort(self):
        if self.sorted(self.set): return
        n = len(self.set)
        for i in range(n - 1):
            for j in range(0, n - i - 1):
                if self.set[j] > self.set[j + 1]:
                    self.set[j], self.set[j + 1] = self.set[j + 1], self.set[j]
                    yield (i,j,colors['red'])
                else:
                    yield (i,j,colors['yellow'])

    def quick_sort(self):
        if self.sorted(self.set): return
        def get_poz(ls, ld):
            piv = self.set[ls]
            while ls < ld:
                if self.set[ls] > self.set[ld]:
                    self.set[ls], self.set[ld] = self.set[ld], self.set[ls]
                    yield (ls,ld,colors['red'])
                else:pass
                    #yield (ls, ld, colors['yellow'])
                if self.set[ls] == piv:
                    ld -= 1
                else:
                    ls += 1
            yield ls

        def quick(ls, ld):
            if ls < ld:
                gen2 = get_poz(ls, ld)
                poz = next(gen2)
                while type(poz) == type(()):
                    # print(self.set)
                    # print(poz)
                    yield poz
                    poz = next(gen2)
                yield  from quick(ls, poz)
                yield  from quick(poz + 1, ld)

        gen1 = quick(0, len(self.set) - 1)
        running = True
        while running:
            try:
                move = next(gen1)
                yield move
            except Exception as e:
                print(e)
                running = False

    def merge_sort(self):





        gen1 = mergeSort(self.set,0,len(self.set))
        running = True
        while running:
            try:
                move = next(gen1)
                yield move
            except Exception as e:
                print(e)
                running = False
        self.create_bars_from_set()

    def radix_sort(self):
        if self.sorted(self.set): return
        p = 0
        while 10 ** p <= self.max:
            print(10**p,self.max)
            cpy = []
            for i in range(10):
                #cpy += [nr for nr in self.set if (nr // 10 ** p) % 10 == i]
                for j,nr in enumerate(self.set):
                    if (nr // 10 ** p) % 10 == i:
                        cpy += [nr]
                        self.set.pop(j)
                        self.set[len(cpy)-1:len(cpy)-1] = [nr]
                        yield (j,j,colors['red'])
                    else:pass
                        #yield (j,j,colors['yellow'])
            self.set = cpy
            yield
            p += 1
        #yield

    def bogo_sort(self):
        while not self.sorted(self.set):
            self.set = random.sample(population=self.set, k=len(self.set))
            yield

    def sorted(self,arr):
        for i in range(1, len(arr)):
            if arr[i] < arr[i - 1]:
                return False
        return True

    def increase_range(self):
        if self.range < 10 ** 6:
            self.range *= 10
            self.init_set()

    def decrease_range(self):
        if self.range > 10:
            self.range //= 10
            self.init_set()

    def increase_size(self):
        if self.size < self.max_size:
            self.size += 20
            self.init_set()

    def decrease_size(self):
        if self.size > 20:
            self.size -= 20
            self.init_set()


class NumberBar():
    padding = 1

    def __init__(self, x, y, width, height, value):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.value = value
        self.default_color = colors['white']
        self.color = self.default_color

    def draw_self(self):
        pygame.draw.rect(screen, self.color, (
            self.x + self.padding, self.y, self.width - self.padding, max(self.height - self.padding, 0)))

    def set_color(self,color):
        self.color = color

    def reset_color(self):
        self.color = self.default_color

debug = Debug()
mouse = Mouse()
gui = GUI()
number_set = NumberSet()

running = True
while running:
    screen.fill(colors['black'])

    for event in pygame.event.get():
        debug.run(event)
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEMOTION:  ####### MOUSE MOVE
            mouse.update(event.pos, event.buttons)
            # if GUI.menu is not None:
            GUI.menu.update()
        if event.type == pygame.MOUSEBUTTONUP:
            mouse.click()
        if event.type == pygame.VIDEORESIZE:
            screen = pygame.display.set_mode((event.w,event.h),pygame.RESIZABLE)
            gui.gui_elements = []
            gui = GUI()
            number_set = NumberSet()

    gui.update()
    number_set.update()

    pygame.display.update()
