import curses
import locale
import os
import string
import sys
import time
import threading

from ui import UI
#from whatsappCli import feed
from whatsappCli.feed import contacts

locale.setlocale(locale.LC_ALL,'')



class CursesUI(UI):

    def __init__(self, feeder):
        self.feeder = feeder
        self.windows = []
        self.lock = threading.Lock()

    def start(self):
        curses.wrapper(self.__curses)

    def stop(self):
        pass

    def __curses(self, stdscr):
        curses.noecho()
        curses.cbreak()    #enable cbreak mode

        stdscr.nodelay(True) 
        
        (mlines, mcols) = stdscr.getmaxyx()

    	win = Window(self, self.lock, 0, 'whatsapp', mlines, mcols)
        self.windows.append(win)
        self.__show_all('',0)
        self.__refresh()
        win.register_command(self.lock)

    def __refresh(self):
        for w in self.windows:
            w.refresh()

    def __new_window(self):
        win = curses.newwin(mlines, mcols)
        win.border()

    def execute(self, command, win_index=0):
        if command.startswith('/help'):
            self.__show_help(command.split('/help', 1)[1].strip(), win_index)
        elif command.startswith('/chat'):
            self.__show_chat(command.split('/chat', 1)[1].strip(), win_index)
        elif command.startswith('/all'):
            self.__show_all(command.split('/all', 1)[1].strip(), win_index)
        elif command.startswith('/users'):
            self.__show_users(command.split('/users', 1)[1].strip(), win_index) 
        elif command.startswith('/add'):
            self.__add_contact(command.split('/add', 1)[1].strip(), win_index)
        elif command.startswith('/clear'):
            self.__clear(command.split('/clear', 1)[1].strip(), win_index)
        elif command.startswith('/q'):
            self.__quit(command.split('/q', 1)[1].strip(), win_index)
        elif command.startswith('/'):
            self.__show_unsupported(command.split('/', 1)[1].strip(), win_index)
        else:
            self.__send_message(command.strip(), win_index)

    def __show_help(self, command, win_index=0):
        self.windows[win_index].show_message('HELP: use /all for read only mode', self.lock)
        self.windows[win_index].show_message('HELP: use /chat name (partial names are allowed) to chat with a person/group', self.lock)
        self.windows[win_index].show_message('HELP: type message followed by enter key to send a message in chat mode', self.lock)
        self.windows[win_index].show_message('HELP: use /users to get list of all contacts', self.lock)
        self.windows[win_index].show_message('HELP: use /add mobile(12 digit mobile number) name(as it appears in your contacts) to add contact', self.lock)
        self.windows[win_index].show_message('HELP: use /clear to clear screen', self.lock)
        self.windows[win_index].show_message('HELP: use /q to quit', self.lock)
        self.windows[win_index].show_message('HELP: use /help for help', self.lock)

    def __show_users(self, command, win_index=0):
        my_list = self.feeder.users()
        for name in my_list:
           self.windows[win_index].show_message('USER: ' + name, self.lock)

    def __add_contact(self, command, win_index=0):
        if len(command) > 13:
            number = command[:12]
            name = command[12:].strip()
            if number.isnumeric() and name:
                self.feeder.add_user(number, name)
                return
        self.windows[win_index].show_message('ERROR: use /add mobile(12 digit mobile number) name(as it appears in your contacts) to add contact', self.lock)
        self.windows[win_index].show_message('HELP: use /help for help', self.lock)

    def __show_all(self, command, win_index=0):
        if self.windows[win_index].usr_tag != '':
            self.windows[win_index].win_name = 'whatsapp'
            self.windows[win_index].usr_tag = ''
            self.windows[win_index].tail_on_thread(self.feeder.get(), self.lock, '')

    def __show_chat(self, command, win_index=0):
        try:
            tag = self.feeder.resolve_user(command)
        except ValueError as err:
            self.windows[win_index].show_message('ERROR: 0 or more than 1 matches for ' + command, self.lock)
            self.windows[win_index].show_message('HELP: use /help for help', self.lock)
            return
   
        if self.windows[win_index].usr_tag != tag: 
            self.windows[win_index].win_name = contacts[tag]
            self.windows[win_index].usr_tag = tag
            self.windows[win_index].tail_on_thread(self.feeder.get(contacts[tag]), self.lock, tag)

    def __quit(self, command, win_index=0):
        curses.endwin()
        os._exit(0)

    def __clear(self, command, win_index=0):
        self.windows[win_index].clear(self.lock)

    def __show_unsupported(self, command, win_index=0):
        self.windows[win_index].show_message('ERROR: unkown command', self.lock)
        self.windows[win_index].show_message('HELP: use /help for help', self.lock) 

    def __send_message(self, command, win_index=0):

        if self.windows[win_index].usr_tag:
            if not command:
                self.windows[win_index].show_message("ERROR: cannot send empty message", self.lock)
                return
            else:
                self.feeder.post(contacts[self.windows[win_index].usr_tag], command)
        else:
            self.windows[win_index].show_message('ERROR: cannot send messages in this window. Use /chat to open chat window', self.lock)
            self.windows[win_index].show_message('HELP: use /help for help', self.lock)

class Window:
    
    def __init__(self, ui, lock, win_index, win_name, lines, cols, y=0, x=0):
        self.ui = ui
        self.win_index = win_index
        self.win = curses.newwin(lines, cols, y, x)
        self.subwin = self.win.subwin(1,cols-2,lines-2,1)
        self.win.nodelay(True)
        self.win.keypad(True)  #enable keypad mode
        self.subwin.nodelay(True)
        self.subwin.keypad(True)  #enable keypad mode
        self.win_name = win_name
        self.usr_tag = None
        self.command = ""
        self.command_x = 0
        self.clear(lock)
        self.threads = {}

    def  __del__(self):
        self.win.keypad(0)  #disnable keypad mode

    def refresh(self):
        self.win.refresh()
        self.subwin.refresh()
 
    def resize(self):
        pass

    def clear(self, lock):
       title = " %s " % (self.win_name,)
       title = title.encode('utf-8')
       max_lines, max_chars = self.win.getmaxyx() 
       self.y = 1
       self.x = 0
       with lock:
            self.win.clear()
            self.refresh()
            self.win.border()
            self.refresh()
            self.win.addstr(0, max_chars / 2 - len(title) / 2, title)
            self.__reset_curs() 

    def show(self, line, title, max_lines, max_chars, lock):

        max_line_len = max_chars - 2
    	line = line.encode('utf-8')
        
        if len(line) > max_line_len:
            first_portion = line[0:max_line_len - 1] + "\n"
            trailing_len = max_line_len - (len("> ") + 1)
            remaining = ["> " + line[i:i + trailing_len] + "\n"
                         for i in range(max_line_len - 1, len(line), trailing_len)]
            remaining[-1] = remaining[-1][0:-1]
            line_portions = [first_portion] + remaining
        else:
            line_portions = [line]

        for line_portion in line_portions:
            with lock:
                try:
                    if self.y >= max_lines - 2:
                        self.win.move(1, 1)
                        self.win.deleteln()
                        self.win.move(self.y - 1, 1)
                        self.win.deleteln()
                        self.win.addstr(line_portion) 
                    else:
                        self.win.move(self.y, self.x + 1)
                        self.win.addstr(line_portion)

                    self.win.border()
                    self.y, self.x = self.win.getyx()
                    self.win.addstr(0, max_chars / 2 - len(title) / 2, title)
                    self.__reset_curs()
                except KeyboardInterrupt:
                    return

    def show_message(self, message, lock):
        title = " %s " % (self.win_name,)
        title = title.encode('utf-8')
        max_lines, max_chars = self.win.getmaxyx()
        self.show(message.strip() + '\n', title, max_lines, max_chars, lock)
        

    def __reset_curs(self):
        max_y, max_x = self.win.getmaxyx()
        self.win.move(max_y-2, 1 + self.command_x)
        self.refresh()

    def tail_on_thread(self, generator, lock, tag):
        thread = threading.Thread(
            target=self.tail, args=(generator, lock, tag))
        thread.daemon = True
        thread.start()
        self.threads[tag] = thread
 
    def tail(self, generator, lock, tag):
        """
        Update a curses window with tailed lines from a generator.
        """
        self.clear(lock)
        title = " %s " % (self.win_name,)
        title = title.encode('utf-8')
        max_lines, max_chars = self.win.getmaxyx()
        max_line_len = max_chars - 2

        for line in generator:
            if self.usr_tag != tag:
                #user for this window has changed
                return
            if threading.current_thread() != self.threads[tag]:
                return
            self.show(line, title, max_lines, max_chars, lock)

    def register_command(self, lock):
        while True:
            with lock:
                c = self.subwin.getch()
            if c == curses.KEY_BACKSPACE:
                if self.command_x > 0:
                    with lock:
                        (y_now,x_now) = self.subwin.getyx()
                        (y_max,x_max) = self.subwin.getmaxyx()
                        if x_now > 0:
                            self.subwin.move(y_now, x_now - 1)
                            self.subwin.delch()
                            if len(self.command) - self.command_x >  x_max - x_now:
                                self.subwin.move(y_now, x_max-1)
                                self.subwin.insch(ord(self.command[self.command_x + x_max - x_now]))
                                self.subwin.move(y_now, x_now - 1)
                            self.subwin.refresh()
                             
                             
                    self.command = self.command[:self.command_x-1] + self.command[self.command_x:]
                    self.command_x = self.command_x - 1
                else:
                    curses.beep()
                   
            elif c == curses.KEY_LEFT:
                if self.command_x > 0:
                    with lock:
                        (y_now,x_now) = self.subwin.getyx()
                        (y_max,x_max) = self.subwin.getmaxyx()
                        if x_now > 0:
                            self.subwin.move(y_now, x_now - 1)
                            self.subwin.refresh()
                        else:
                            self.subwin.insch(ord(self.command[self.command_x -1]))
                            self.subwin.refresh()
                    self.command_x = self.command_x - 1
                else:
                    curses.beep()
            elif c == curses.KEY_RIGHT:
                if self.command_x < len(self.command):
                    with lock:
                        (y_now,x_now) = self.subwin.getyx()
                        (y_max,x_max) = self.subwin.getmaxyx()
                        if x_now < x_max -1:
                            self.subwin.move(y_now, x_now + 1)
                            self.subwin.refresh()
                        else:
                            self.subwin.move(y_now,0)
                            self.subwin.delch()
                            self.subwin.move(y_now,x_max-1)
                            if self.command_x + 1 < len(self.command):
                                self.subwin.insch(ord(self.command[self.command_x + 1]))
                            else:
                                self.subwin.delch()
                            self.subwin.refresh()
                    self.command_x = self.command_x + 1
                else:
                    curses.beep()
            elif c == curses.KEY_ENTER or c == 10 or c  == 13:
                c_thread = threading.Thread(target=self.ui.execute, args=(self.command, self.win_index))
                c_thread.daemon = True
                c_thread.start()
                #self.ui.execute(self.command, self.win_index)
                with lock:
                    self.subwin.clear()
                    self.subwin.refresh()
                self.command = ""
                self.command_x = 0
                    
            elif c != curses.ERR:
                s = unichr(c)
                if s in string.printable:
                   with lock:
                       (y_max,x_max) = self.subwin.getmaxyx()
                       (y_now,x_now) = self.subwin.getyx()
                       if x_now < x_max -1:
                           self.subwin.insch(c)
                           self.subwin.move(y_now, x_now + 1)
                       else:
                           self.subwin.move(y_now,0)
                           self.subwin.delch()
                           self.subwin.move(y_now,x_max-2)
                           self.subwin.insch(c)
                           self.subwin.move(y_now,x_max-1)
                       self.subwin.refresh()
                       self.command = self.command[:self.command_x] + s + self.command[self.command_x:]
                       self.command_x = self.command_x + 1
                else:
                    curses.beep()
            time.sleep(0.04)
