import sys
import socket
import threading
import time 
# Formatted Print Statements for the Server Side.

# server_started = "Server started on port {}. Accepting connections".format(port)
# user_logged_in = "{} logged in".format(username)
# user_logged_out = "{} logged out".format(username)
# subscribe_confirm = "{}: subscribed {}".format(username, hashtag)
# unsubscribe_confirm = "{}: unsubscribed {}".format(username, hashtag)
# message_received_sent = "{}: {} {} sent".format(username, hashtag, message)

HOST = '127.0.0.1'

usernames = {} # maps username to socket
channels = {} # channels and who is in them 
user_timeline = {}


def start_server(port):

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, port))
    server_socket.listen()

    print(f"Server started on port {port}. Accepting connections", flush = True)

    while True: # loop to accept connections

            client_socket, _ = server_socket.accept()

            username = client_socket.recv(2048).decode()

            if username in usernames:
                client_socket.sendall("Connection Failed: Username Taken".encode())
                continue
            
            usernames[username] = client_socket
            user_timeline[username] = []

            client_socket.sendall("worked".encode())
            print(f"{username} logged in", flush=True)
            threading.Thread(target=handle_client, args=(client_socket, username)).start()
    

def handle_client(conn, username):

    while True:
        command = conn.recv(1024).decode()

        if not command:
            break

        if "exit" in command:
            if username in usernames:
                # remove from usernames
                del usernames[username]
            # unsubscribe from all channels
            for subscribers in channels.values():
                if username in subscribers:
                    subscribers.remove(username)
            print(f"{username} logged out", flush=True)
            conn.close()
            break
        elif "unsubscribe" in command:
            hashtag = command.split()[-1]
            # is the hashtag even a channel
            # is the username in that channel
            if hashtag in channels and username in channels[hashtag]: 
                channels[hashtag].remove(username)
                print(f"{username}: unsubscribed {hashtag}", flush = True)
                # tell the client that you unsubsribed 
                conn.sendall(hashtag.encode()) # in client: add a check for when you get this 
        elif "subscribe" in command:
            hashtag = command.split()[-1]
            if hashtag not in channels:
                channels[hashtag] = set()
            channels[hashtag].add(username)
            #print(channels)
            print(f"{username}: subscribed {hashtag}", flush=True) # does this
            #print(f"{hashtag}") 
            conn.sendall(hashtag.encode()) # telling client what hashtag 
        # possible problem area 
        elif "message" in command:
            # message #3251 Hello from client 2 
            parts = command.split(" ", 2)
            hashtag = parts[1]
            message = parts[2]
            if len(message) < 1 or len(message) > 150 or not hashtag.startswith("#"):
                conn.sendall("Message: Illegal Message".encode()) # telling the client message was illegal
            else:
                print(f"{username}: {hashtag} {message} sent", flush=True)
            
            # broadcast

            # who do you send the message to?
            # send the message to everyone that follows that hashtag and everyone that follows #all

            recipients = set()
            if hashtag in channels:
                recipients.update(channels[hashtag])
            if "#ALL" in channels:
                recipients.update(channels["#ALL"])

            for user in recipients:
                if user in usernames:
                    usernames[user].sendall(f"M{username}: {hashtag} {message}".encode())
                    user_timeline[user].append(f"{username}: {hashtag} {message}")
            
        elif "timeline" in command:
            print("serever detects command is timeline2", flush=True)
            if username in user_timeline:
                if len(user_timeline[username]) == 0:
                    #print("server detects no messages in timeline")
                    #empty timeline
                    conn.sendall("e".encode()) # add functionaluty o cli
                    # this is causing infinite loop
                    continue
                #print("server detects timeline is not empty3", flush=True)
                to_cli = 'p' + '\n'.join(user_timeline[username])
                #print(f"this is cli {to_cli}", flush=True)
                conn.sendall(to_cli.encode()) # add duncirtonalut to cli
                user_timeline[username] = []
        
if __name__ == "__main__":

    port = int(sys.argv[1])
    start_server(port)