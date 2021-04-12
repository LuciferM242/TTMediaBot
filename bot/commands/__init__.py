import logging
import re
import traceback

from .commands import *
from bot import errors

re_command = re.compile('[a-z]+')

class CommandProcessor:
    def __init__(self, player, ttclient, module_manager, service_manager):
        self.player = player
        self.ttclient = ttclient
        self.service_manager = service_manager
        self.module_manager = module_manager
        self.locked = False
        self.commands_dict = {
            'h': HelpCommand(self),
            'a': AboutCommand(self),
            'p': PlayPauseCommand(self),
            'u': PlayUrlCommand(self),
            'sv': ServiceCommand(self),
            's': StopCommand(self),
            'b': PreviousTrackCommand(self),
            'n': NextTrackCommand(self),
            'c': SelectTrackCommand(self),
            'sb': SeekBackCommand(self),
            'sf': SeekForwardCommand(self),
            'v': VolumeCommand(self),
            # 'r': RateCommand(self),
            # It has bugs on windows
            'm': ModeCommand(self),
            'gl': GetLinkCommand(self),
        }
        self.admin_commands_dict = {
            'girl': lambda arg, user: 'Настенька',
            'cn': ChangeNicknameCommand(self),
            'cs': ChangeStatusCommand(self),
            'l': LockCommand(self),
            'va': VoiceTransmissionCommand(self),
            'q': QuitCommand(self),
        }

    def __call__(self, message):
        if message.user.is_banned:
            return _('You are banned')
        if not message.user.is_admin:
            if message.user.channel_id != self.ttclient.get_my_channel_id():
                return _('You are not in bot\'s channel')
            if self.locked:
                return _('Bot is locked')
        try:
            command = re.findall(re_command, message.text.split(' ')[0].lower())[0]
        except IndexError:
            return self.help('', message.user)
        arg = ' '.join(message.text.split(' ')[1::])
        try:
            if command in self.commands_dict:
                return self.commands_dict[command](arg, message.user)
            elif message.user.is_admin and command in self.admin_commands_dict:
                return self.admin_commands_dict[command](arg, message.user)
            else:
                return _('Unknown command') + ' "' + command + '"\n' + self.help('', message.user)
        except errors.InvalidArgumentError as e:
            return self.help(command, message.user)
        except Exception as e:
            logging.error(traceback.format_exc())
            return _('Error: {}'.format(e))

    def help(self, arg, user):
        if arg:
            if arg in self.commands_dict:
                try:
                    return '{command} {help}'.format(command=arg, help=self.commands_dict[arg].help)
                except AttributeError:
                    return _('{command} Help text not found'.format(command=arg))
            elif user.is_admin and arg in self.admin_commands_dict:
                try:
                    return '{command} {help}'.format(command=arg, help=self.admin_commands_dict[arg].help)
                except AttributeError:
                    return _('{command} Help text not found'.format(command=arg))
            else:
                return _('Unknown command "{command}"\n{help}').format(command=arg, help=self.help('', user))
        else:
            help_strings = []
            for i in list(self.commands_dict):
                try:
                    help_strings.append(
                        '{} {}'.format(i, self.commands_dict[i].help)
                    )
                except AttributeError:
                    help_strings.append('{} help text not found'.format(i))
            if user.is_admin:
                for i in list(self.admin_commands_dict)[1::]:
                    try:
                        help_strings.append(
                            '{} {}'.format(i, self.admin_commands_dict[i].help)
                        )
                    except AttributeError:
                        help_strings.append('{} help text not found'.format(i))
            return '\n'.join(help_strings)

    def lock(self,  arg, user):
        self.locked = not self.locked
        return _('Locked') if self.locked else _('Unlocked')
