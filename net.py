import json
import requests
import socket
import socketserver
import sys
import threading
from _thread import *
from time import sleep
import pickle
import genalg
import uuid
import numpy as np
import pickle

status = {
    "qid": 0,
    "table" : [
        {"port":12345, "address": "volunteered_genalg.com", "c": False}
        #{"port":12345, "address": "localhost.localdomain", "c": False}
    ],
    "p": {},
    "s": {},
    "scr": 0
}

history = {}

MAX_ITERATIONS = 10
RANGE = 100
BATCH = 15
DEGREE = 2
VARS = 3

host = socket.gethostname()
addr = socket.gethostbyname(host)
print_lock = threading.Lock()

def in_table(table, address):
    known_address = False
    for j in status["table"]:
        if address["port"] == j["port"] and address["address"] == j["address"]:
            known_address = True
            break
    return known_address
    
def compute_genalg(max_iterations=10):
    i = 0

    global new_results
    global status
    while True:
        if status["qid"]:
            while i < max_iterations:

                #problem = np.reshape(np.fromstring(status["p"]), (DEGREE, -1))
                #solution = np.reshape(np.fromstring(status["s"]), (BATCH, -1))
                problem = np.reshape(np.asarray(status["p"]), (DEGREE, -1))
                solution = np.reshape(np.asarray(status["s"]), (BATCH, -1))
                new_solutions, new_score = genalg.iteration(problem, solution)
                status["s"] = new_solutions.tolist()
                status["scr"] = new_score
                new_results = True
                sleep(1)
                i += 1

            history[status["qid"]] = {"p": status["p"], "s": status["s"][0], "scr": status["scr"]}
            i = 0
            print("\nGENALG ID:" + status["qid"] + " FINISHED\n")
            status["qid"] = 0
            #print(i, max_iterations, status["qid"])
        sleep(1)

def save():
    with open(host + "_history.json", "w") as f:
        json.dump(history, f)

def ping():
    return {"type": "PING", "table": status["table"], "qid": status["qid"]}

def init():
    return {"type": "INIT", "problem": status["p"], "qid": status["qid"]}

def sol():
    while status["s"] == {}:
        sleep(1)
    #print(type(status["s"][0]), type(status["qid"]), type(status["scr"])
    return {"type": "SOL", "s": status["s"][0], "qid": status["qid"], "scr": status["scr"]}

def IO():
    global status

    global port
    global host
    while True:
        c = input("CTRL+c=quit, s=status, p=generate_problem: \n")
        if c == "s" or c == "status":
            print(status)
        elif c == "p" or c == "problem":
            status["qid"] = str(uuid.uuid1())
            #status["p"] = np.array2string(genalg.generate_problem(DEGREE, VARS))
            #status["s"] = np.array2string(genalg.generate_solution(BATCH, VARS))
            
            status["p"] = genalg.generate_problem(DEGREE, VARS).tolist()
            status["s"] = genalg.generate_solution(BATCH, VARS).tolist()
        c = ""
            
def check_connections():
    global status

    while True:
        for i in status["table"]:
            if  i["port"] == port and i["address"] == host:
                sleep(1)
                continue
            
            if not i["c"]:
                i["c"] = True
                start_new_thread(m_connection, (i["address"], i["port"]))
        sleep(1)
                
def f_connection(c, address):
    global status
    #print("f New connection to ", address)

    #status["table"].append({"port":address[0], "address": address[1], "c": True})
    #connection = {"port": address[1], "address": address[0], "c": True}
    #if not in_table(status, connection):
    #    status["table"].append(connection)
    try:
        while True: 
            
            # data received from client 
            #data = pickle.loads(c.recv(4096))
            
            #exit()
            data = json.loads(str(c.recv(4096), "utf-8"))

            msg = handle_states(data, {"address": address[0], "port": address[1]})
            #msg = ping()
            #c.sendall(pickle.dumps(msg))
            c.sendall(bytes(json.dumps(msg), "utf-8"))
            
            # connection closed
    except Exception as e:
        
        for i in status["table"]:
            if i["port"] == address[0] and i["address"] == address[1]:
                i["c"] = False
        
        c.close()
    c.close()

def m_connection(add, p):
    global status
    #connection = {"port": p, "address": add, "c": True}
    #if not in_table(status, connection):
    #    status["table"].append(connection)
    
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:

        #sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # Connect to server and send data
        #sock.bind((host, port))
        #print(status)
        try:
            sock.connect((add, p))
        except ConnectionRefusedError:
            for i in status["table"]:
                if i["address"] == add and i["port"] == p:
                    i["c"] = False
                    break
            return
        print("New connection to ", add)
        #c, addr = socket.create_connection((i["address"], i["port"]))
        msg = None

        try:
            while True:
                if not msg:
                    msg = ping()
                #sock.sendall(pickle.dumps(msg))
                sock.sendall(bytes(json.dumps(msg), "utf-8"))
                # Receive data from the server and shut down
                #received = pickle.loads(sock.recv(4096))'
            
                received = json.loads(str(sock.recv(4096), "utf-8"))
            
                #print(received)
                #exit()
                #msg["table"].append({"port": p, "address": add, "c": True})
                #received = json.loads(str(sock.recv(4096), "utf-8"))
                msg = handle_states(received, {"address": add, "port": p})
                #print(received)
                sleep(1)
        except Exception as e:
            print("Connection to " + add + " closed.")
            sock.close()
            for i in status["table"]:
                
                if i["port"] == p and i["address"] == add:
                    i["c"] = False
            
            
def handle_states(msg, address):
    #print(status)
    if msg["type"] == "PING":
        for i in msg["table"]:
            if not in_table(status, i):
                #if not known_address:
                status["table"].append({"port":i["port"], "address": i["address"], "c": False})

        if not status["qid"]:
            return ping()
        else:
            return init()
    elif msg["type"] == "INIT":
        if not status["qid"] and msg["qid"] and not msg["qid"] in history:
            status["qid"] = msg["qid"]
            status["p"] = msg["problem"]
            status["s"] = genalg.generate_solution(BATCH, VARS).tolist()
        return sol()
        #return ping()
    elif msg["type"] == "SOL":
        if in_table(status, address):
            if abs(int(msg["scr"])) < abs(int(status["scr"])):
                status["s"][0] = msg["s"]#np.asarray(msg["s"])
                print("Accepted new solution from " + address["address"])
            if status["qid"]:
                return sol()
            else:
                return ping()
        return ping()
    
    
def Main():
    global port
    global host
    

    global new_results
    global status
   
    port = 12345#int(sys.argv[1])
    #host = "localhost"
    print(host, port, "gg")
    new_results = False
    status["table"].append({"port": port, "address": socket.gethostname(), "c": True})
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((host, port))
    start_new_thread(IO, ())
    start_new_thread(check_connections, ())
    start_new_thread(compute_genalg, ())
    print("socket binded to port", port) 
    
    # put the socket into listening mode 
    s.listen(5) 
    print("socket is listening")

    #    start_new_thread(ping, (port,))
    # a forever loop until client wants to exit 
    while True: 
  
        # establish connection with client 
        c, addr = s.accept() 
  
        # lock acquired by client 
        #print_lock.acquire() 
        #print('Connected to :', addr[0], ':', addr[1])
        already_on = True
        for i in status["table"]:
            if i["port"] == addr[1] and i["addr"] == addr[0]:
                #print_lock.release()
                already_on = False
        # Start a new thread and return its identifier
        if  already_on:
            start_new_thread(f_connection, (c,addr))
        else:
            c.close()
        #print_lock.release()
        #s.listen(5)
    s.close()

if __name__=="__main__":
    try:
        Main()
    except KeyboardInterrupt:
        print("\nUSER CLOSED PROGRAM")
        save()
    
