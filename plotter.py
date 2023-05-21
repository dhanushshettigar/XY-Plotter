import os
import time
import serial
import threading
import bluetooth

server_socket=bluetooth.BluetoothSocket( bluetooth.RFCOMM )
port = 1
encoding = 'utf-8'
server_socket.bind(("",port))
server_socket.listen(1)

type_mode = True

if not type_mode:
    print("Ready To Connect...")
    client_socket,address = server_socket.accept()
    print ("Accepted Connection From ",address)

# Open grbl serial port
try:
    s = serial.Serial('/dev/ttyACM0',115200)
    print("arduino port: ","/dev/ttyACM0")
except:
    s = serial.Serial('/dev/ttyACM1',115200)
    print("arduino port: ","/dev/ttyACM1")

" buffer is a keyword in python for some reason .."

buff = " "
oneline = 10#40 #characters that can be writen in a line
current_line = 0
line_drop = 10
scale = 0.15 # goes well with line yoffset drop of 10
#scale = 0.25 # also tweak yoffset

#font = "scriptc" #doble stroke
#font = "scripts" #cursive 
font = "rowmans"

cmd = "./h2g/src/hf2gcode" # ./prog -params "text"
gcd_folder = "linegcodes/" # use / after folder
gcd_filename = "line"

os.system(f"rm -rf {gcd_folder}") #flush out revious gcodes from storage
os.system(f"mkdir {gcd_folder}")

from collections import deque
plotter_queue = []
plotter_queue = deque(plotter_queue) # to store pending line.gc filenames

def home():
    home_cmd = 'G0 X0 Y0\n'
    s.write(home_cmd.encode())


def stream_gcode(filename):
    # Open g-code file
    f = open(filename,'r')

    # Wake up grbl
    s.write("\r\n\r\n".encode())
    time.sleep(2)   # Wait for grbl to initialize 
    s.flushInput()  # Flush startup text in serial input

    # Stream g-code to grbl
    for line in f:
        
        l = line.strip() # Strip all EOL characters for consistency
        #print('current line: ' + l)
        
        if l.find('Z1.000') == 3:
            new_line = l.replace("Z1.000", "M03 S0" )
            ln_cmd = new_line + '\n'
        elif l.find('Z-1.000') == 3:
            new_line = l.replace("Z-1.000", "M03 S180")
            ln_cmd = new_line + '\n'
        else:
            ln_cmd = l + '\n'
        
        print('sending line: ' + ln_cmd)
        s.write(ln_cmd.encode()) # Send g-code block to grbl
        grbl_out = s.readline() # Wait for grbl response with carriage return
        print(grbl_out.strip())

    # Wait here until grbl is finished to close serial port and file.
    print("finished" + filename)
    
    home()
    client_socket.send('Done')

    # Close file and serial port
    f.close()
    
    #s.close() # dont know whether closing and opening of port is required ... might be redundant   

def gen_gcode(mesg,x,y,linefn):
    print("Generating gcode for: ",mesg)
    print(f"Writing to {linefn}{gcd_filename}")
    x,y,lineno = str(x),str(y),str(linefn)
    sca = str(scale)
    generatecmd = cmd +" --font "+font+" -o "+gcd_folder+linefn+" --scale "+sca+" -x "+ x +" -y "+ y + " " + "\"" +mesg +"\""
    return os.system(generatecmd)

def run_plotter():
    while True:
        global plotter_queue
        if (len(plotter_queue) >= 1):
            cur_line_file = plotter_queue.popleft() # pop first line ,then second, and so on..
            print("Plotter is writing :"+cur_line_file)
            stream_gcode(f"{gcd_folder}{cur_line_file}")
        else:
            #print("No pending gcodes ..",end=" ")
            pass
        time.sleep(1)

def main():
    global buff
    global current_line
    global oneline
    
    while True:
        #print("Here :" + str(len(buff))+ ' ' + str(oneline))
        if(len(buff) >= oneline):
            offset_txt = None
            #check for the first space from the end of buff
            if buff[oneline-1] == " " or buff[oneline] == " ": #check current and next lettr is space?
                print_txt = buff[:oneline]
                buff = buff[oneline:]  # retain remaining buff text

            else:
                index = 0
                for i in range(len(buff[:oneline])-1, -1, -1): #check for space from last 
                    index += 1
                    if buff[i] == " ":
                        print_txt = buff[:len(buff[:oneline])-index] #send to gcd conveter
                        buff = buff[oneline-index:]  # retain remaining buff text
                        break
                    
            linefn = f"{gcd_filename}{current_line}.gc" #linefilename
            gen_gcode(print_txt,0,current_line,linefn) #text , xoffset , yoffset 
            plotter_queue.append(linefn)

            current_line -= line_drop #step down a line
            
        else:
            if type_mode:
                newtext = input("Enter text:")+" "
                if newtext is not None:
                    buff += ''+ newtext
            else:
                print("Ready to take txt")
                data = client_socket.recv(1024)
                if data is not None:
                    buff += ' ' + data.decode(encoding)
                    print ("Received: %s" % data)

def plotter_handler():
    threading.Thread(target=run_plotter,daemon=True).start()

if __name__ == "__main__":
	plotter_handler() # sequentialy serial_stream each new file generated in gcd_folder
	main() #main thread performs continous speech recog and gcode generation

client_socket.close()
server_socket.close()
