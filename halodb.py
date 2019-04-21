#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""HaloDB.

Halo Discord Bot

Requires:
    Environment Variables:
        HALODB_TOKEN
        HAPI_KEY
"""
import os
import logging
import asyncio
import json
import requests
import discord

__title__ = 'HaloDB'
__author__ = 'Brad Gibson & Richard Noble'
__github__ = 'napalm255, nobler1050'
__version__ = '0.1.0'
__token__ = os.environ.get('HALODB_TOKEN', None)
__hapi_api__ = 'https://api.naponline.net/hapi'
__hapi_key__ = os.environ.get('HAPI_KEY', None)


class Message():
    """Message that is JSON serializable."""
    def __init__(self, message):
        self.message = message

    def data(self):
        """Return data."""
        msg = self.message
        return {'author': {'dir': dir(msg.author),
                           'name': msg.author.name,
                           'discriminator': msg.author.discriminator,
                           'mention': msg.author.mention}
               }


class HaloDbClient(discord.Client):
    """HaloDB Client."""
    commands = list()

    async def on_ready(self):
        """On ready."""
        logging.info('Logged in as %s:%s', self.user.name, self.user.id)
        await self.get_commands(loop=True)
        logging.info('Available commands: %s', self.commands)

    async def on_message(self, message):
        """On message."""
        # we do not want the bot to reply to itself
        if message.author.id == self.user.id:
            return

        data = Message(message).data()
        logging.info('Data: %s', json.dumps(data))

        commands = tuple(self.commands['commands'])
        mention = message.author.mention

        if message.content == '!refresh commands':
            await self.get_commands()
            msg = self.commands['message']
            await message.channel.send('{0}\n{1}'.format(mention, msg))

        if message.content.startswith(commands):
            endpoint = message.content.replace(' ', '/')[1:]
            api = await self.api(endpoint, data=data)
            response = api['message']
            await message.channel.send('{0}\n{1}'.format(mention, response))

    async def get_commands(self, loop=False, refresh=1800):
        """Query API for available commands."""
        self.commands = await self.api('')
        while loop:
            await asyncio.sleep(refresh)
            self.commands = await self.api('')

    async def api(self, endpoint, method='POST', data=None):
        """Query API."""
        logging.info('Calling %s/%s', __hapi_api__, endpoint)
        headers = {'Content-Type': 'application/json'}
        if method == 'POST':
            response = requests.post('{}/{}'.format(__hapi_api__, endpoint),
                                     data=data, headers=headers)
        elif method == 'GET':
            response = requests.get('{}/{}'.format(__hapi_api__, endpoint),
                                    headers=headers)
        logging.info('Response: %s: %s', response, response.json())
        return response.json()


def return_help(error=None, code=0):
    """Exit and output help."""
    if error:
        logging.critical(error)
        code = 1
    print("""
          {0} Help
          {1}

          Environment Variables Required:
            HALODB_TOKEN
            HAPI_KEY
          """.format(__title__, '-'*50))
    exit(code)

def main():
    """Main entry point."""
    log_file, log_level = (None, logging.INFO)
    log_format = '%(levelname)s: %(message)s'
    logging.basicConfig(filename=log_file, level=log_level, format=log_format)
    logging.info('Running %s', __file__)
    if not __token__:
        return_help('HaloDB token not found.')
    if not __hapi_key__:
        return_help('HaloAPI key not found.')

    logging.info('Starting %s', __title__)
    client = HaloDbClient()
    client.run(__token__)

if __name__ == '__main__':
    main()
