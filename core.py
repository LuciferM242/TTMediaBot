import commands
import configparser
import player
import tt
import services
import sys
from TeamTalkPy import ClientEvent



class Bot(object):
    def __init__(self, config_file):
        self.config = configparser.ConfigParser()
        with open(config_file, "r", encoding="utf-8") as f:
            self.config.readfp(f)
        self.ttclient = tt.TeamTalk(self.config["teamtalk"])
        self.player = player.Player(self.ttclient, self.config["player"])
        self.vk_audio = services.initialize_vk(self.config["vk"])
        self.process_command = commands.ProcessCommand(self.player, self.vk_audio)

    def run(self):
        while True:
            result, msg = self.ttclient.waitForEvent(ClientEvent.CLIENTEVENT_CMD_USER_TEXTMSG)
            if result:
                if msg.textmessage.nMsgType == 1:
                    print(msg.textmessage.szMessage)
                    reply_text = self.process_command(msg.textmessage.szMessage)
                    print(reply_text)
                    if reply_text:
                        self.ttclient.reply_to_message(msg.textmessage, reply_text)
