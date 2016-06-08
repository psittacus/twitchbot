import socket
import string
import sqlite3

#------------------------------------------------SQLite------------------------------------------------#

connection = sqlite3.connect("bets.db")

cursor = connection.cursor()

# delete 
# cursor.execute("""DROP TABLE Teilnehmer;""")

sql_command = """
CREATE TABLE Teilnehmer ( 
twitchUser TEXT PRIMARY KEY, 
betFirst TEXT, 
betSecond TEXT);"""


cursor.execute(sql_command)


#------------------------------------------------Twitch------------------------------------------------#


HOST = "irc.twitch.tv"
PORT = 6667
PASS = "" # 0auth
NICK = "username"
CHAN = "#username" 
readbuffer = ""


betTime = False;

bannedWords = {} # List of banned words

operators = {} # List of Moderators / Operators

s = socket.socket()
s.connect((HOST, PORT))
s.send(bytes("PASS " + PASS + "\r\n", "UTF-8")) 
s.send(bytes("NICK " + NICK + "\r\n", "UTF-8")) 
s.send(bytes("JOIN " + CHAN + " \r\n", "UTF-8"))


#------------------------------------------------Functions------------------------------------------------#

def fillSQL(user, firstBet, secondBet): # for the bets (CS:GO Bets)
	sql_command = """
	INSERT INTO Teilnehmer (twitchUser, betFirst, betSecond) VALUES (\""""+user+"\",\""+firstBet+"\",\"" +secondBet+"\")"
	cursor.execute(sql_command)
	connection.commit()
	cursor.execute("SELECT * FROM Teilnehmer WHERE twitchUser IS \""+user+"\"")
	print("\nfetch one:")
	res = cursor.fetchone() 
	print(res)

def send_message(message): # Send Messages to the Twitch Chat
	s.send(bytes("PRIVMSG #" + NICK + " :" + message + "\r\n", "UTF-8"))

def timeout(user): # timeouts a user
	send_message("/timeout "+user+" 60")

def findTheWinner(firstBet, secondBet): # finds the Winner from the bet time
	cursor.execute("SELECT twitchUser FROM Teilnehmer WHERE betFirst IS \""+firstBet+"\" AND betSecond IS \"" +secondBet+"\"")
	print("\nfetch one:")
	res = cursor.fetchone()
	print(res)
	send_message("The winner is: "+str(res))
	winnerFile = open("winnerfile.txt","w")
	winnerFile.write(inhalt+str(res))

#------------------------------------------------Here begins the action------------------------------------------------#

send_message("/slow 3") # slows the chat speed down

while True: 
	line = str(s.recv(1024)) 
	if "End of /NAMES list" in line: 
		break 
	while True: 
		for line in str(s.recv(1024)).split('\\r\\n'): 
			if line[0] == "PING": # if Twitch asks you, if you are awake
				send_message("PONG "+line[1])
			parts = line.split(':') 
			if len(parts) > 2:
				words = parts[2].split(" ") # later for better command checking

			if len(parts) < 3: 
				continue 
			if "QUIT" not in parts[1] and "JOIN" not in parts[1] and "PART" not in parts[1]: 
				message = parts[2][:len(parts[2])] 
			usernamesplit = parts[1].split("!") 
			username = usernamesplit[0] 
			print(username + ": " + message) 
			
#------------------------------------Commands------------------------------------#

			if message == "Hey": 
				send_message("Willkommen, " + username)
			for banned in bannedWords:
				if message == banned:
					send_message("Das war eine unschöne Äußerung von dir, "+username+". Zitat: \""+message+"\"")
					timeout(username)
					

			if message == "!werbung":
				send_message("") # Here your commercial text (for example your Twitter Account
			for operatorNames in operators:
				if username == operatorNames and message == "!":
					send_message("Unknown Command entered")

			if len(words) > 2:
				if words[0] == "!bet" and betTime == True:
					fillSQL(username, words[1], words[2])
				if words[0] == "!bet" and betTime == False:
					send_message(username + " sorry, at the moment, there is no time for bets")

			for operatorNames in operators:
				if message == "!start bet time" and username == operatorNames:
					send_message("@All! Bet time has started. Now you can vote in this syntax: !bet (our points) (their points). For Example: \"!bet 16 7\"")
					betTime = True
			
			for operatorNames in operators:
				if message == "!end bet time" and username == operatorNames:
					send_message("@All! Bet time has ended. Now you can't vote anymore!")
					betTime = False
			if len(words) > 2:
				for operatorNames in operators:
					if words[0] == "!findTheWinner" and username == operatorNames:
						findTheWinner(words[1], words[2])
