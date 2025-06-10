import sys
import socket
import threading
import time

client_connected = "Connected to {} on port {}"
connection_failed_username_taken = "Connection Failed: Username Taken"
subscribe_added = "subscribe: {} added"
subscribe_too_many = "subscribe: Too many Subscriptions"
message_sent = "{}: {} {} sent"
message_illegal = "Message: Illegal Message"
unsubscribe_removed = "unsubscribe: {} removed"
timeline_no_messages = "timeline: No Messages Available"
exit_message = "Exiting client"


def input_handler(client_socket, username, running, hashtags):
    # this is what im typing in on the client terminal
    while True:
        command = input(">> ").strip()
        #print(f"curr command is {command}")
        if not command:
            continue
        if command.lower().startswith("exit "):
            client_socket.sendall("exit".encode())
            running[0] = False
            break
        elif command.startswith("message "):
            _, hashtag, message = command.split(" ", 2)
            if len(message) < 1 or len(message) > 150 or not hashtag.startswith("#"):
                print(message_illegal, flush=True)
                continue
            else:
                client_socket.sendall(command.encode())
                print(f"{username}: {hashtag} {message} sent", flush=True)


        elif command.startswith("subscribe "):
            #print("here1")
            if len(hashtags) == 5:
                print(subscribe_too_many, flush=True)
                continue
            # ok so its valid
            client_socket.sendall(command.encode()) #now the server can add i t
            # now it'll tell me the hashtag
            # this is where it stops working
            response = client_socket.recv(2048).decode()
            #print(f"response is {response}")
            hashtags.add(response[1:])
            # print added
            print(f"subscribe: {response} added", flush=True)


        elif command.startswith("unsubscribe "):
            client_socket.sendall(command.encode())
            response = client_socket.recv(2048).decode()
            # should get back the hashtage to unsub from
            hashtags.remove(response[1:])
            print(f"unsubscribe: {response} removed", flush=True)

        elif command.startswith("timeline"):
            #print("client detects that the command is timeline1", flush=True)
            client_socket.sendall("timeline".encode())
        else:
            client_socket.sendall(command.encode())



def recieve_handler(client_socket, running):
    while running[0]:
        time.sleep(1)
        try:
            type_msg = client_socket.recv(2048, socket.MSG_PEEK)
        except socket.timeout:
            continue

        #print(f"type_msg is {type_msg}", flush=True)
        if type_msg:
            if type_msg.decode().startswith("M"):
                message = client_socket.recv(2048).decode()
                print(message[1:], flush=True)
            elif type_msg.decode().startswith("e"):
                #print("client detects that it is empty")
                #client_socket.recv(2048)
                print(timeline_no_messages, flush=True)
                # infinitie lop here
                break
            elif type_msg.decode().startswith("p"):
                #print("client detects we need timeline", flush=True)
                message = client_socket.recv(2048).decode()
                print(message[1:], flush=True)


if __name__ == "__main__":
    ip = sys.argv[1]
    port = int(sys.argv[2])
    username = sys.argv[3]

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((ip, port))
    client_socket.sendall(username.encode())

    response = client_socket.recv(2048).decode()

    if "Username Taken" in response:
        print("Connection Failed: Username Taken", flush=True)
        client_socket.close()
        sys.exit(1)

    print(f"Connected to {ip} on port {port}", flush=True)

    running = [True]
    hashtags = set()

    input_thread = threading.Thread(target=input_handler, args=(client_socket, username, running, hashtags))
    input_thread.start()

    recieving_thread = threading.Thread(target=recieve_handler, args=(client_socket, running))
    recieving_thread.start()

    input_thread.join()
    recieving_thread.join()

    client_socket.close()
    sys.exit(0)
