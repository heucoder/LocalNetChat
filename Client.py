# -*- coding: utf-8 -*-  
from socket import socket, AF_INET, SOCK_STREAM
from threading import Thread
import curses

class sockClient(object):
    def __init__(self):
        self._sock = None
        self._stdscr = curses.initscr()
        self._print_index = 3
        self._input_index = 25
        self._message_queue = []

    def init(self, host = "localhost", post = 15968):
        self.set_win()
        self.connect(host = "localhost", post = 15968)
        self._stdscr.addstr(1, 0, "connection establish\n", curses.color_pair(1))
        self._stdscr.refresh()

    def close(self):
        self.unset_win()
        self._sock.close()

    def running(self):
        input_thread = Thread(target = self.input)
        input_thread.daemon = True
        input_thread.start()

        print_thread = Thread(target = self.print_message)
        print_thread.daemon = True
        print_thread.start()
        self._stdscr.addstr(2, 0, "Running... ", curses.color_pair(1))
        self._stdscr.addstr(self._input_index, 0, "ME: ", curses.color_pair(1))
        self._stdscr.refresh()
        while True:
            if not input_thread.is_alive() or not print_thread.is_alive():
                break

    def set_win(self):
        '''控制台设置'''
        #使用颜色首先需要调用这个方法
        curses.start_color()
        #文字和背景色设置，设置了两个color pair，分别为1和2
        curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)
        #关闭屏幕回显
        #设置nodelay，使得控制台可以以非阻塞的方式接受控制台输入，超时1秒
        self._stdscr.nodelay(1)
    
    def unset_win(self):
        '''控制台重置'''
        curses.echo()
        #结束窗口
        curses.endwin()

    def print_message(self):
        while True:
            # 堵塞
            message = self._sock.recv(1024)
            if not message:
                break
            if len(self._message_queue) > 20:
                self._message_queue.pop(0)
            self._message_queue.append(message)

            for i in range(len(self._message_queue)):
                index = i + self._print_index
                m = self._message_queue[i]
                self._stdscr.addstr(index, 3, ' '*50, curses.color_pair(1))
                self._stdscr.addstr(index, 3, m, curses.color_pair(1))

            self._stdscr.addstr(self._input_index, 0, "ME: ", curses.color_pair(1))
            self._stdscr.refresh()

    def input(self):
        self._stdscr.nodelay(0)
        while True:
            s = self._stdscr.getstr(self._input_index, 5)
            self._stdscr.addstr(self._input_index, 4, " "*100, curses.color_pair(1))
            if s == b"":
                break
            self._sock.sendall(s)
        self._stdscr.nodelay(1)

    def connect(self, host = "localhost", post = 15968):
        sock = socket(AF_INET, SOCK_STREAM)
        sock.connect((host, post))
        self._sock = sock


if __name__ == "__main__":
    client = sockClient()
    # init
    client.init()

    # run Loop
    try:
        client.running()
    except Exception:
        pass
    # close
    finally:
        client.close()
