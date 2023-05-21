import serial

myserial = serial.Serial("/dev/ttyACM0", 115200)


while True:
    myserial.write(b"Hello from Raspberry Pi!\n")
    
myserial.close() 