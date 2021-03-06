from awtg.filtering.manager import AsyncHandler

from awtg.filtering.stdfilters.std import Command
from awtg.filtering.stdfilters.std import requires_config

from const import (GREETING, SEND_ME_A_PHOTO,
                   LIMIT_EXCEEDED, ADD_DONE,
                   VIEW_PROMPT, CONTENT_REMOVED)
from database import NSFWDatabase, MAX_PICTURES

from awtg.keyboard import RelativeInlineKeyboard
from awtg.filtering.stdfilters.callback import build_cbinrpc_procedure

from awtg.types import Message, InlineQuery

from database import PHOTO, VIDEO


@AsyncHandler
async def start(message):
    message.reply(GREETING % message.memory['config']['bot_username'], parse_mode="html")


@AsyncHandler
async def create_nsfw(message: Message):
    photos = message.data.photo
    video = message.data.video

    if not (photos or video):
        return message.reply(SEND_ME_A_PHOTO)

    type_ = PHOTO

    if video:
        type_ = VIDEO
        entity = video
    else:
        entity = photos[-1]

    config = message.memory['config']
    entity = entity.file_id

    file_url = await message.tg.get_file_url(entity)

    async with NSFWDatabase(config['db']) as context:
        count = await context.get_pictures_count(message.data.from_.id)

        if count > MAX_PICTURES:
            return message.reply(LIMIT_EXCEEDED)

        await context.add_picture(entity, file_url,
                                  message.data.from_.id, message.data.text,
                                  type_)

    message.reply(ADD_DONE)


@AsyncHandler
async def remove_nsfw(message):
    config = message.memory['config']

    async with NSFWDatabase(config['db']) as context:
        await context.remove_pictures(message.data.from_.id)

    message.reply(CONTENT_REMOVED)


@AsyncHandler
async def inline_gallery(inline: InlineQuery):
    config = inline.memory['config']

    async with NSFWDatabase(config['db']) as context:
        pictures = await context.get_pictures(inline.data.from_.id, MAX_PICTURES,
                                              inline.data.query or None)

    for picture in pictures:
        kb = RelativeInlineKeyboard()
        kb.add_button('Посмотреть', callback_data=build_cbinrpc_procedure(
            'view', db_file_id=picture['id']
        ))
        kb.add_button('Удалить', callback_data=build_cbinrpc_procedure(
            'remove', db_file_id=picture['id']
        ))

        if picture['type'] == VIDEO:
            inline.builder.video(picture['file_id'], title=picture['caption'] or "Видео",
                                 text=VIEW_PROMPT, reply_markup=kb)
        else:
            inline.builder.photo(picture['file_id'],
                                 cached=True, text=VIEW_PROMPT,
                                 reply_markup=kb)

    inline.respond(cache_time=0)


exports = (
    start.add_filters(
        Command('start', 'help')
    ).add_mutual_callbacks(
        requires_config
    ),

    create_nsfw.add_filters(
        Command('create_nsfw')
    ).add_mutual_callbacks(
        requires_config
    ),

    remove_nsfw.add_filters(
        Command('delete_nsfw')
    ).add_mutual_callbacks(
        requires_config
    ),

    inline_gallery.set_inline().add_mutual_callbacks(
        requires_config
    )
)

