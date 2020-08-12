from awtg.filtering.manager import AsyncHandler
from awtg.types import Message, InlineQuery

from awtg.filtering.stdfilters.std import Command
from awtg.filtering.stdfilters.std import requires_config

from const import (GREETING, SEND_ME_A_PHOTO,
                   LIMIT_EXCEEDED, ADD_DONE,
                   VIEW_PROMPT)
from database import NSFWDatabase, MAX_PICTURES

from awtg.keyboard import RelativeInlineKeyboard
from awtg.filtering.stdfilters.callback import build_cbinrpc_procedure


@AsyncHandler
async def start(message):
    message.reply(GREETING, parse_mode="html")


@AsyncHandler
async def create_nsfw(message):
    photos = message.data.photo

    if not photos:
        return message.reply(SEND_ME_A_PHOTO)

    config = message.memory['config']
    photo = photos[0]

    file_url = await message.tg.get_file_url(photo.file_id)

    async with NSFWDatabase(config['db']) as context:
        count = await context.get_pictures_count(message.data.from_.id)

        if count > MAX_PICTURES:
            return message.reply(LIMIT_EXCEEDED)

        await context.add_picture(photo.file_id, file_url,
                                  message.data.from_.id)

    message.reply(ADD_DONE)


@AsyncHandler
async def inline_gallery(inline: InlineQuery):
    config = inline.memory['config']

    async with NSFWDatabase(config['db']) as context:
        pictures = await context.get_pictures(inline.data.from_.id, MAX_PICTURES)

    for picture in pictures:
        kb = RelativeInlineKeyboard()
        kb.add_button('Посмотреть', callback_data=build_cbinrpc_procedure(
            'view', db_file_id=picture['id']
        ))
        kb.add_button('Удалить', callback_data=build_cbinrpc_procedure(
            'remove', db_file_id=picture['id']
        ))

        inline.builder.photo(picture['file_id'],
                             cached=True, text=VIEW_PROMPT,
                             reply_markup=kb)

    inline.respond(cache_time=0)


exports = (
    start.add_filters(
        Command('start', 'help')
    ),

    create_nsfw.add_filters(
        Command('create_nsfw')
    ).add_mutual_callbacks(
        requires_config
    ),

    inline_gallery.set_inline().add_mutual_callbacks(
        requires_config
    )
)

