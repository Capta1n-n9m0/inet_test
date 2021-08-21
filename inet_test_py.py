import icmplib
import time
import statistics
import threading
from tkinter import *
from tkinter.ttk import *
import os
from multiprocessing import Pool

adrs = ['8.8.8.8', '85.132.85.85', '1.1.1.1', '217.25.25.125']


class App:
    servers = list()
    threads = list()
    serverCounter = -1

    class Server:
        def __init__(self, outer_app, adr, number):
            self.app = outer_app
            self.adr = adr
            self.master = outer_app.master
            # Creating elements
            self.address_label = Label(self.master, text=adr)
            self.pingProgress_progressbar = Progressbar(self.master, length=200, value=0)
            self.minPing_label = Label(self.master, text="Min Ping: None")
            self.avgPing_label = Label(self.master, text="Avg Ping: None")
            self.maxPing_label = Label(self.master, text="Max Ping: None")
            self.stddevOfPing_label = Label(self.master, text="Stddev Of Ping: None")
            # Placing elements
            self.address_label.grid(row=((number // 4) * 6 + 1), column=(number % 4), sticky=W + E, pady=5, padx=5)
            self.pingProgress_progressbar.grid(row=((number // 4) * 6 + 2), column=(number % 4), sticky=W, pady=5,
                                               padx=5)
            self.minPing_label.grid(row=((number // 4) * 6 + 3), column=(number % 4), sticky=W, pady=5, padx=5)
            self.avgPing_label.grid(row=((number // 4) * 6 + 4), column=(number % 4), sticky=W, pady=5, padx=5)
            self.maxPing_label.grid(row=((number // 4) * 6 + 5), column=(number % 4), sticky=W, pady=5, padx=5)
            self.stddevOfPing_label.grid(row=((number // 4) * 6 + 6), column=(number % 4), sticky=W, pady=5, padx=5)

        def host_test(self, max_time=15):
            host = icmplib.ping(self.adr, count=4, interval=0.25)
            if host.is_alive:
                # print(f"{adr} is alive! Starting intense test for {adr}")
                self.address_label['text'] = f"{self.adr}   OK!   "
                fails = 0
                tries = 0
                pings = list()
                start = time.time()
                while (time.time() - start < max_time):
                    self.pingProgress_progressbar['value'] = ((time.time() - start) / max_time) * 100
                    tries += 1
                    temp_host = icmplib.ping(self.adr, count=1, timeout=0.5, id=id(self))
                    time.sleep(0.002)
                    if temp_host.is_alive:
                        pings.append(temp_host.max_rtt)
                    else:
                        fails += 1
                pings = [int(i) for i in pings]
                self.pingProgress_progressbar['value'] = 100
                self.address_label['text'] = f"{self.adr} OK! {round((fails / tries) * 100, 2)}% exeded 500ms"
                self.minPing_label['text'] = f"Min Ping: {min(pings)}ms"
                self.avgPing_label['text'] = f"Avg Ping: {round(statistics.mean(pings), 2)}ms"
                self.maxPing_label['text'] = f"Max Ping: {max(pings)}ms"
                self.stddevOfPing_label['text'] = f"Stddev Of Ping: {round(statistics.stdev(pings), 2)}ms"
            else:
                # print(f'{adr} does not respond! Moving to the next one')
                self.address_label['text'] = f"{self.adr}   UNREACHABLE!"

    def createServer(self, master, adr):
        self.serverCounter += 1
        server = App.Server(self, adr, self.serverCounter)
        self.servers.append(server)
        return server

    def addAndCreateServer(self):
        newArd = self.newAddress_entry.get()
        if newArd not in self.adrs:
            self.adrs.append(newArd)
            self.createServer(self.master, newArd)

    def __init__(self, master):
        global adrs
        self.adrs = adrs
        self.master = master
        master.protocol("WM_DELETE_WINDOW", self.on_exit)
        # Menu setup part
        self.mainMenu = Menu(master)
        self.helpMenu = Menu(self.mainMenu, tearoff=0)
        master.config(menu=self.mainMenu)
        self.helpMenu.add_command(label="Info")
        self.helpMenu.add_command(label="Help")
        self.mainMenu.add_cascade(label="Info", menu=self.helpMenu)
        # Small options part
        self.start_button = Button(master, text="Start")
        self.start_button.grid(row=0, column=0)
        self.IP_label = Label(self.master, text="IP Address:")
        self.IP_label.grid(row=0, column=1, sticky=W, pady=10, padx=10)
        self.newAddress_entry = Entry(master)
        self.newAddress_entry.grid(row=0, column=2, sticky=W + E, pady=10, padx=10)
        self.newAddress_button = Button(master, text="Add")
        self.newAddress_button.grid(row=0, column=3, sticky=E, pady=10, padx=10)
        # Server adding part
        for adr in self.adrs:
            self.createServer(master, adr)
        self.newAddress_button['command'] = self.addAndCreateServer
        self.start_button['command'] = self.runServers

    def runServers(self):
        if self.threads.__len__() != 0:
            for thread in self.threads:
                thread.join()
            self.threads.clear()
        for server in self.servers:
            self.threads.append(threading.Thread(target=server.host_test, daemon=True))
        for thread in self.threads:
            thread.start()

    def on_exit(self):
        if self.threads.__len__() != 0:
            for thread in self.threads:
                thread.join()
            self.threads.clear()
        for server in self.servers:
            server.address_label['text'] = "EXITING!"
            server.address_label.update()
        time.sleep(1)
        self.master.destroy()


def main():
    root = Tk(screenName="Internet stability test")
    app = App(root)
    root.mainloop()


if __name__ == "__main__":
    main()

"""
def main():
    i = 0
    adrs = ['8.8.8.8', '85.132.85.85', '1.1.1.1', '217.25.25.125']
    print("Ping test will take 15 seconds and perform many pings for each host")
    for adr in adrs:
        host = icmplib.ping(adr, count=1, timeout=2)
        if host.is_alive:
            print(f"{adr} is alive! Starting intense test for {adr}")
            fails = 0
            tries = 0
            pings = list()
            start = time.time()
            while(time.time() - start < 15):
                tries += 1
                temp_host = icmplib.ping(adr, count=1, timeout=0.5)
                if temp_host.is_alive:
                    pings.append(temp_host.max_rtt)
                else:
                    fails += 1
            pings = [int(i) for i in pings]
            print(f"    Test for {adr} is done!")
            print(f"     Max ping is {max(pings)}ms\n \
    Min ping is {min(pings)}ms\n \
    Avg ping is {statistics.mean(pings)}ms\n \
    Stdev of pings is {statistics.stdev(pings)}ms\n \
    Most common ping is {statistics.mode(pings)}ms\n \
    {fails} of {tries} responses exeded 500ms")
        else:
            print(f'{adr} does not respond! Moving to the next one')
    input('Test is done! Press Enter to terminate.')

if __name__ == "__main__":
    main()
"""