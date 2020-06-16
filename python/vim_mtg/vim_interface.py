# viMTG - The VIM 'Magic: The Gathering' deck builder.
# Copyright (C) 2020  yoshi1@tutanota.com
#
# viMTG is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# viMTG is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with viMTG.  If not, see <https://www.gnu.org/licenses/>.

"""The Python interface to Vim settings and messages."""


import vim

# settings

class settings:
    """Methods to return vim global variables."""

    @staticmethod
    def get(setting, type):
        """ Return a vim global variable.

        :param str setting: name of variable, as g:mtg_`setting`
        :param str type:    type of variable ('bool', 'int', or 'str')

        Example:

            get('ansi', 'str')  # returns the string value of 'g:mtg_ansi'

        """
        return {
                'bool': settings.get_bool,
                'int': settings.get_int,
                'str': settings.get_str,
                }[type](setting)

    @staticmethod
    def get_bool(setting):
        """Get a vim int global variable, g:mtg_`setting`."""
        result = vim.eval("g:mtg_"+setting)
        result = bool(int(result))
        return result

    @staticmethod
    def get_int(setting):
        """Get a vim int global variable, g:mtg_`setting`."""
        result = vim.eval("g:mtg_"+setting)
        result = int(result)
        return result

    @staticmethod
    def get_str(setting):
        """Get a vim string global variable, g:mtg_`setting`."""
        result = vim.eval("g:mtg_"+setting)
        result = str(result)
        return result


# functions

def vim_error(message):
    """Write an error to vim."""
    message = message.replace('"', r'\"')
    message = message.replace("'", r"''")
    command = "call mtg#error('{}')".format(message)
    vim.command(command)

def vim_warning(message):
    """Write a warning to vim."""
    message = message.replace('"', r'\"')
    message = message.replace("'", r"''")
    command = "call mtg#warning('{}')".format(message)
    vim.command(command)
