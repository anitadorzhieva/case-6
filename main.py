"""Case-study #6
Developers:
Titova Marina-50%, Malahova Anastasia-50%, Dorzhieva Anita-50% 
"""
import random
import time
from math import pi, cos, sin
import tkinter as tk
from local import *

class World:
    LINE_LEN = 19400
    TIME_COEF = 30  # мировых секунд в одной секунде
    MID_TIME_LINE = 30  # минут

    def __init__(self):
        self.stations = Station.from_dict({
            ST1: 0,
            ST2: 3,
            ST3: 6,
            ST4: 8,
            ST5: 11,
            ST6: 13,
            ST7: 14,
            ST8: 17,
            ST9: 20,
            ST10: 22,
            ST11: 25,
            ST12: 27})

        self.trains = Train.from_file(self.stations)
        self.time_model = 0

    def step(self, sec_real):
        sec = sec_real * World.TIME_COEF
        for train in self.trains:
            train.step(sec)
        self.time_model += sec


class Station:
    def __init__(self, name, pos):
        self.name = name
        self.pos = pos / World.MID_TIME_LINE * World.LINE_LEN

    @staticmethod
    def from_dict(stations):
        stats = {}
        for k, v in stations.items():
            stats[k] = (Station(k, v))
        return stats

    def check(self, left, right):
        # выравниваем
        left, right = min(left, right), max(left, right)
        if right > World.LINE_LEN:
            # двигались по часовой, перешли через 0
            left -= World.LINE_LEN
            right -= World.LINE_LEN
        if left < self.pos < right:
            return True
        return False


class Train:
    BLOCK_LEN = 20  # длинна вагона в метрах

    def __init__(self, number, station, direction, speed, count, stations):
        self.number = int(number)
        self.pos = station.pos
        self.direction = bool(int(direction))
        self.speed = float(speed)
        self.count = int(count)
        self.stations = stations

        self.stay = 0

    def step(self, secs):
        # секунды модели
        if self.stay == 0:
            last = self.pos
            if self.direction:
                self.pos += self.speed * secs
            else:
                self.pos -= self.speed * secs

            for station in self.stations.values():
                if station.check(last, self.pos):
                    self.stay = random.randint(20, 120) // 10

            self.pos = self.pos % World.LINE_LEN
        else:
            self.stay -= secs
            if self.stay <= 0:
                self.stay = 0

    @staticmethod
    def from_file(stations):
        trains = []
        f = open("metro.txt", encoding='utf-8')
        for line in f.readlines():
            if not line:
                break
            n, s, d, sp, c = line.split()
            s = stations[s]
            trains.append(Train(
                n, s, d, sp, c, stations))
        return trains


class Root:
    METER_IN_PIXEL = 10

    def __init__(self, world):
        self.root = tk.Tk()
        self.root.title(TITLE)
        self.world = world

        self.btn = tk.Button(self.root, text=START, command=self.btn_click)
        self.btn.pack()
        self.is_run = False

        self.size = 700

        self.cx = (self.size + 200) // 2
        self.cy = self.size // 2

        self.R = int(self.px(World.LINE_LEN / (2 * pi)))

        self.canvas = tk.Canvas(self.root, width=self.size + 200, height=self.size, bg = '#FFFFE0')
        self.canvas.pack()

        self.redraw()
        self.root.mainloop()

    def m(self, pixels):
        # Из пиксели получаем метров
        return pixels * Root.METER_IN_PIXEL

    def px(self, meter):
        # Из метры получаем пикселей
        return meter / Root.METER_IN_PIXEL

    def x(self, pos, radius=None):
        # По позиции получаем координату x
        if radius == None:
            radius = self.R

        angle = pos / World.LINE_LEN * 2 * pi
        angle = angle - pi / 2
        return radius * cos(angle) + self.cx

    def y(self, pos, radius=None):
        # По позиции получаем координату x
        if radius == None:
            radius = self.R

        angle = pos / World.LINE_LEN * 2 * pi
        angle = angle - pi / 2
        return radius * sin(angle) + self.cy

    def btn_click(self):
        if self.is_run:
            self.root.destroy()
            return
        self.is_run = True
        self.btn['text'] = STOP
        self.start()

    def main_line(self):
        self.canvas.create_oval(self.cx - self.R, self.cy - self.R,
                                self.cx + self.R, self.cy + self.R, width = 2, outline = 'green')
        self.canvas.create_oval(self.cx - self.R + 8, self.cy - self.R + 8,
                                self.cx + self.R - 8, self.cy + self.R - 8, width = 2, outline = 'red')
    def stantions(self):
        ss = self.world.stations.values()

        for s in ss:
            p = s.pos

            self.canvas.create_oval(
                self.x(p, self.R - 10), self.y(p, self.R - 10),
                self.x(p, self.R + 10), self.y(p, self.R + 10), fill = 'black')
            if p > World.LINE_LEN / 2:
                self.canvas.create_text(self.x(p, self.R + 10), self.y(p, self.R + 10),
                                    anchor = tk.E, text = s.name)
            else:
                self.canvas.create_text(self.x(p, self.R + 10), self.y(p, self.R + 10),
                                    anchor = tk.W, text = s.name)

    def trains(self):
        for train in self.world.trains:
            block_len = Train.BLOCK_LEN
            if not train.direction:
                block_len = -block_len
            for i in range(train.count):
                pos = train.pos - i * block_len
                first = self.x(pos), self.y(pos)
                second = self.x(pos - block_len), self.y(pos - block_len)
                third = self.x(pos - block_len / 2, self.R - 10), self.y(pos - block_len / 2, self.R - 10)
                if train.direction:
                    self.canvas.create_polygon(first, second, third, outline ='green',
                                           fill='gray', width=2)

                else:
                    self.canvas.create_polygon(first, second, third, outline = "red",
                                           fill='gray', width=2)

            third = self.x(train.pos - block_len / 2, self.R - 30), self.y(train.pos - block_len / 2, self.R - 30)
            if train.pos < World.LINE_LEN / 2:
                self.canvas.create_text(third, anchor=tk.E)
            else:
                self.canvas.create_text(third, anchor=tk.W)

    
    def start(self):
        start_step_time = time.time()
        frame_len = 25  # ms
        self.world.step(frame_len / 1000)
        self.redraw()
        step_time = int((time.time() - start_step_time) * 1000)
        self.btn.after(frame_len - step_time, self.start)

    def redraw(self):
        self.canvas.delete("all")

        self.main_line()
        self.stantions()
        self.trains()
        


world = World()
root = Root(world)
