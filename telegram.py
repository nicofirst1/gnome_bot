import telepot
from telepot.delegate import pave_event_space, per_chat_id, create_open
import os
from Util import calc_score, consigliami
TOKEN="434893083:AAG2B6rXCMAi9p1zl2bQYZfqAqdmmnVZvQU"

def run():
    setting_lst=[]
    setting_lst.append(pave_event_space()(per_chat_id(), create_open, gnomo, timeout=1000))
    bot = telepot.DelegatorBot(TOKEN, setting_lst)
    bot.message_loop(run_forever="listening ...")


class gnomo(telepot.helper.ChatHandler):
    def __init__(self, *args, **kwargs):
        super(gnomo, self).__init__(*args, **kwargs)
        self.numeri=[]

        # questa è la funzione per leggere i messaggi

    def on_chat_message(self, msg):
        # prendo alcuni parametri tra cui content_type
        content_type, chat_type, chat_id = telepot.glance(msg)
        print(msg.get("from").get("username"))

        # se il messaggio appena inviato è di testo allora vedo cosa c'è scritto
        if (content_type == "text"):
            message = msg.get("text").lower()
            if ("/win" in message):
                numbers=message.split()
                numbers.pop(0)
                #print(numbers)
                if len(numbers)>5:
                    self.sender.sendMessage("Hai inserito troppi numeri!")
                    return
                elif len(numbers)<5:
                    self.sender.sendMessage("Devi inserire 5 nuemri separati da spazio")
                    return
                self.numeri=[int(elem) for elem in numbers]
                win=(1-calc_score(self.numeri))*100
                self.sender.sendMessage("Possibilità di vincita : "+ "{:.3f}".format(win)+"%")
                return

            elif ("/consiglia" in message):
                if not self.numeri:
                    self.sender.sendMessage("Devi prima usare il comando /win !")
                    return
                path2img=consigliami(self.numeri)
                if path2img==0:
                    self.sender.sendMessage("Non Cambiare !")
                    return

                with open(path2img,"rb") as file:
                    self.sender.sendPhoto(file)
                os.remove(path2img)




            elif ("/help" in message or "/start" in message):
                self.sender.sendMessage("Benveuto in questo bot! Il suo scopo è semplicifcare "
                                        "l'ispezione dello gnomo del gioco @lootgamebot!\n"
                                        "Quando lo gnomo torna con le rune basta utilizzare il comando "
                                        "/win 1 2 3 4 (mi raccomando inserisci i numeri separati da spazio) per avere"
                                        " la tua probabilità di vincita!\n"
                                        "Se invece vuoi un consiglio su quale numero cambiare usa il comando /consiglia"
                                        " (dovo aver caricato i numeri con /win ) per avere una tabella con i migliori"
                                        " valori da cambiare.\n Questo è tutto! Spero di esservi utile ;)\n")
                return





run()