# coding=utf-8
import telepot
from telepot.delegate import pave_event_space, per_chat_id, create_open
import os
from Util import calc_score, consigliami
from telepot.namedtuple import ReplyKeyboardMarkup, KeyboardButton
import re

# from queue import Queue
# from flask import Flask, request


# PORT = int(os.environ.get('PORT', 5000))
with open("token", "r+") as file:
    TOKEN=file.readlines()[0]
print(TOKEN)
# TOKEN = os.environ['PP_BOT_TOKEN']  # put your token in heroku app as environment variable
SECRET = '/bot' + TOKEN
# update_queue = Queue()
# app = Flask(__name__)
URL = "https://api.telegram.org/bot<" + TOKEN + "token>/"

COMMANDS = """
consiglia - Vedi gli effetti per un cambio di runa
win - Calcola la probabilità di vincita
ricerca - condensa tutti gli elemeti di /lista di @craftlootbot in gruppi da tre
help - Visualizza la guida
 """

HELP_MSG = "Benveuto in questo bot! Il suo scopo è semplificare " \
           "l'ispezione dello gnomo del gioco @lootgamebot!\n" \
           "Quando lo gnomo torna con le rune basta utilizzare il comando " \
           "/win 1 2 3 4 (mi raccomando inserisci i numeri separati da spazio) per avere la tua probabilità di vincita!\n" \
           "Se invece vuoi un consiglio su quale numero cambiare usa il comando /consiglia" \
           "(dovo aver caricato i numeri con /win ) per avere una tabella con i migliori valori da cambiare.\n" \
           "Il comando /ricerca ti permette di condensare la lista di oggetti di @craftlootbot in comodi gruppi da 3, in" \
           "modo da facilitare la ricerca su @lootplusbot, inoltre puoi mandare tutti risultati di /ricerca di @lootplusbot e" \
           "infine digitare 'fine' per avere una stima di quanto ti costerà craftare l'oggetto secondo i prezzi di mercato \n" \
           "Questo è tutto! Spero di esservi utile ;)\n"

def run2():
    setting_lst = []
    setting_lst.append(pave_event_space()(per_chat_id(), create_open, gnomo, timeout=100000))
    bot = telepot.DelegatorBot(TOKEN, setting_lst)

    # app.run( port=PORT, debug=True)
    bot.setWebhook()
    bot.setWebhook(URL + SECRET)
    bot.message_loop(source=update_queue)


def run():
    setting_lst = []
    setting_lst.append(pave_event_space()(per_chat_id(), create_open, gnomo, timeout=1000))
    bot = telepot.DelegatorBot(TOKEN, setting_lst)
    bot.message_loop(run_forever="listening ...")


# @app.route( SECRET, methods=['GET', 'POST'])
# def pass_update():
#   update_queue.put(request.data)  # pass update to bot
#  return 'OK'

class gnomo(telepot.helper.ChatHandler):
    def __init__(self, *args, **kwargs):
        super(gnomo, self).__init__(*args, **kwargs)

        self.numeri = []
        self.ricerca = False
        self.quantity=[]
        self.costo=[]
        self.stima=False

    def on_chat_message(self, msg):
        # prendo alcuni parametri tra cui content_type
        content_type, chat_type, chat_id = telepot.glance(msg)
        print(msg.get("from").get("username"))

        # se il messaggio appena inviato è di testo allora vedo cosa c'è scritto
        if (content_type == "text"):
            message = msg.get("text").lower()
            # print(message)
            if ("/win" in message):
                numbers = message.split()
                numbers.pop(0)
                # print(numbers)
                if len(numbers) > 5:
                    self.sender.sendMessage("Hai inserito troppi numeri!")
                    return
                elif len(numbers) < 5:
                    self.sender.sendMessage("Devi inserire 5 nuemri separati da spazio")
                    return
                self.numeri = [int(elem) for elem in numbers]
                win = (1 - calc_score(self.numeri)) * 100
                self.sender.sendMessage("Possibilità di vincita : " + "{:.3f}".format(win) + "%")
                return

            elif ("/consiglia" in message):
                if not self.numeri:
                    self.sender.sendMessage("Devi prima usare il comando /win !")
                    return
                path2img = consigliami(self.numeri)
                if path2img == 0:
                    self.sender.sendMessage("Non Cambiare !")
                    return

                with open(path2img, "rb") as file:
                    self.sender.sendPhoto(file)
                os.remove(path2img)




            elif ("/help" in message or "/start" in message):
                self.sender.sendMessage(HELP_MSG)
                return
            elif ("/ricerca" in message):
                self.sender.sendMessage("Inoltra la lista di @craftlootbot")
                self.ricerca = True

            elif "lista oggetti necessari per" in message and self.ricerca:
                to_send = self.estrai_oggetti(message)
                self.sender.sendMessage(to_send)
                self.ricerca = False
                self.sender.sendMessage("Adesso puoi inoltrarmi tutti i risultati di ricerca di @lootplusbot per "
                                        "avere il totale dei soldi da spendere, oppure digita 'Fine' per passare oltre")
                self.stima=True

            elif "risultati ricerca di" in message and self.stima:
                self.stima_parziale(message)

            elif "fine" in message and self.stima:
                self.stima=False
                if len(self.costo)==0: return

                #print(self.costo, self.quantity)
                tot=0
                for (much,what) in zip(self.costo, self.quantity):
                    tot+=int(what[0])*int(much[1])

                self.sender.sendMessage("Secondo le stime di mercato pagherai "+"{:. }".format(tot)+"§, più il costo di craft")
                self.costo.clear()
                self.quantity.clear()



    def estrai_oggetti(self, msg):

        restante = msg.split("già possiedi")[0].split(":")[1]
        aggiornato = ""
        # print(restante)

        for line in restante.split("\n"):
            if ">" in line:
                # print(line)
                first_num = line.split()[1]
                # print(first_num)
                second_num = line.split()[3]
                # print(second_num)
                what = line.split("di ")[1]
                # print(what)
                right_num = str(int(second_num) - int(first_num))
                right_line = right_num + " su " + right_num + " di " + what
                # print(right_line)
                aggiornato += right_line + "\n"
            else:
                aggiornato += line + "\n"

        # print(aggiornato)
        regex = re.compile(r"di (.*)?\(")
        regex2 = re.compile(r"su ([0-9]) di (.*)?\(")
        lst = re.findall(regex, aggiornato)
        self.quantity = re.findall(regex2, aggiornato)
        commands = []
        # print(lst)
        last_ixd = len(lst) - len(lst) % 3
        for i in range(0, (last_ixd) - 2, 3):
            commands.append("/ricerca " + ",".join(lst[i:i + 3]))

        commands.append("/ricerca " + ",".join(lst[last_ixd:len(lst)]))
        final_string = ""

        for command in commands:
            final_string += command + "\n"

        return final_string

    def stima_parziale(self, msg):
        prov = msg.split("negozi per ")[1:]
        lst = []
        for elem in prov:
            lst.append((elem.split(">")[0].replace("\n", "") + elem.split(">")[1].replace("\n", "")))

        #print(lst)
        regex = re.compile(r"(.*):.*\(([0-9 .]+)")

        for elem in lst:
            e = re.findall(regex, elem)
            #print(e)

            self.costo.append((e[0][0], e[0][1].replace(".", "").replace(" ", "")))




run()
