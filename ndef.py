import sys
import opcodes

import argparse

c_template = '''
int BYTECODE_size(){
    return %d;
}
int* BYTECODE_exporter() {
    static int src[] = {%s};
    return src;
}
'''

class Interpreter():
    def __init__(self,file,routine_name="",start_line=0):
        if file != "":
            self.code = open(file)
        self.name = file if file != "" else routine_name
        self.maxm = 0
        self.functions = {}
        self.line = start_line+1
        self.return_pointer = 0
        self.instruction_pointer = 0
        self.memory = []
        self.mem_start = 0
        self.code_start = 0
        self.bin = ''

        self.ext_calls = []

    def loop(self):
        lines = self.code.readlines()
        ln = len(lines)
        while self.instruction_pointer < ln:
            line = lines[self.instruction_pointer]
            if not line.startswith("#") :
                self.execute(self.breakStatement(line))
            self.line = self.line+1
            self.instruction_pointer += 1
            # print(line,end="")
        # print()

    def breakStatement(self,statement):
        # print(statement)
        r = []
        e = True
        t = ""
        s = statement.strip()
        for c in s:
            if c == "'":
                e = not e
                t += c
            elif c == " " and e:
                if t != "":
                    r.append(t)
                    t = ""
            else:
                t += c
        r.append(t)
        return r
    def execute(self,arr):
        # print(arr)
        if arr[0] != "" :
            # print("Gotcha")
            try:
                self.functions[arr[0]](self, [self.resolveValue(x) for x in arr[1:]])
            except KeyError as e:
                print(e)
                print("Error at line "+str(self.line)+" : "+arr[0]+" is not a valid code [{routine}]".format(routine=self.name))
                sys.exit()


    def loadFunction(self,name,f):
        self.functions[name] = f
        # pass
    def convertInt(self,i):
        r = 0
        try:
            r = int(i,10)
        except Exception:
            r = int(i,16)
        return r

    def resolveValue(self,a):
        try:
            try:
                return int(a,10)
            except Exception:
                return int(a,16)
        except Exception:
            pass
        if type(a) == int:
            return a
        elif a.startswith("'"):
            return a[1:-1]
        elif a.startswith("^"):
            return type(self.resolveValue(a[1:]))
        elif a.startswith("{") and a.endswith("}"):
            return len(self.resolveValue(a[1:-1].strip()))
        elif a.startswith("[") and a.endswith("]"):
            inner = a[1:-1].strip()
            arr = inner.split("#")[0]
            index = inner.split("#")[1]
            # print("IN={0}, ARR={1}, RES1={2}, RES={3}".format(index,arr,self.resolveValue(arr),self.resolveValue(index)))
            return self.resolveValue(arr)[self.resolveValue(index)]
        else:
            return a


def memory(i: Interpreter, args):
    i.mem_start = args[0]
    i.memory = list('\x00' * args[1])

def start(i: Interpreter, args):
    i.code_start = args[0]

def put(i: Interpreter, args):
    i.bin += opcodes.put + chr(args[0]) + chr(args[1])

def mov(i: Interpreter, args):
    i.bin += opcodes.mov + chr(args[0]) + chr(args[1])

def call(i: Interpreter, args):
    i.bin += opcodes.call + chr(len(i.ext_calls)) + chr(args[1])
    i.ext_calls.append(args[0])

def dump(i: Interpreter, args):
    i.bin += opcodes.dump + chr(0) + chr(0)

def main():

    parser = argparse.ArgumentParser(description='Experimental byte-code generator')

    parser.add_argument('input', type=str)
    parser.add_argument('-o', type=str, dest='output')
    parser.add_argument('-c', dest='c_output', action='store_true', default=False)

    args = parser.parse_args()

    i = Interpreter(args.input)

    i.loadFunction('memory', memory)
    i.loadFunction('start', start)
    i.loadFunction('call', call)
    i.loadFunction('dump', dump)
    i.loadFunction('put', put)
    i.loadFunction('mov', mov)
    i.loop()

    # Extern func info
    ext_funcs = ( [ x+'\x00' for x in i.ext_calls ] )

    # Code section info 
    code_info = chr(i.mem_start) + chr(len(i.memory)) + chr(i.code_start)

    header = (
        # Magic bytes
        '\x0f\x0f\x0b\x0b' +

        #Version
        '\x00\x00\x00\x01' + 

        # Section pointers
        '\x02'+chr(int(len(''.join(ext_funcs)))+2) + 

        ''.join(ext_funcs) +

        code_info + 

        # Header end
        '\x00'
    )
    bytecode = header+('\x00' * (len(i.bin)+i.mem_start-len(i.memory)))

    bytecode = list(bytecode)

    bytecode[i.mem_start+len(header):i.mem_start+len(i.memory)+len(header)] = i.memory
    bytecode[i.code_start+len(header):i.code_start+len(i.bin)+len(header)] = i.bin

    print(bytecode)

    out = bytes(''.join(bytecode), 'ISO-8859-1')

    if args.c_output:
        with open(args.output, 'w') as o:
            res = [ str(ord(x)) for x in bytecode]
            print(res)
            o.write(c_template % (len(bytecode) , ','.join(res)))
    else:
        with open(args.output, 'wb') as o:
            o.write(out)


if __name__ == "__main__":
    main()