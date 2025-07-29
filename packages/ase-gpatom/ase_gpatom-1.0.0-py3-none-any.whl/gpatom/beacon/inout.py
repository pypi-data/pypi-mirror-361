import time


class FileWriter():
    ''' Simple file writer '''

    def __init__(self, filename, printout=True, write_time=False):

        self.filename = filename
        self.printout = printout
        self.write_time = write_time
        self.format()

    def format(self):
        with open(self.filename, 'w') as f:
            txt = ""
            if self.write_time:
                txt += "# File created: "
                txt += time.asctime()
                txt += "\n"
            f.write(txt)

    def write(self, string):
        with open(self.filename, 'a') as f:
            txt = string
            if self.write_time:
                txt = time.asctime() + " " + txt
            if self.printout:
                print(txt)
            f.write(txt)
            f.write("\n")


class FileWriter2():
    ''' Simple file writer to write results of a BEACON run.'''

    def __init__(self, filename, printout=True):

        self.filename = filename
        self.printout = printout
        self.format()

    def format(self):
        with open(self.filename, 'w') as f:
            f.write("")

    def write(self, data):
        with open(self.filename, 'a') as f:
            if not hasattr(self, 'keys'):
                self.keys = data.keys()
                f.write('#')
                for key in self.keys:
                    f.write(' {:>12s}'.format(key))
                f.write('\n')
            assert data.keys() == self.keys

            string = ' '
            for key in self.keys:
                if abs(data[key])<0.01:
                    string += ' {:>12.3e}'.format(data[key])
                else:
                    string += ' {:>12.04f}'.format(data[key])
                
            string += '\n'

            if self.printout:
                if type(self.printout) == bool:
                    N = len(self.keys)
                else:
                    N = self.printout
                for n in range(N):
                    key = list(self.keys)[n]
                    print('{:>12s}{:>12.04f}'.format(key, data[key]))
            f.write(string)

    
