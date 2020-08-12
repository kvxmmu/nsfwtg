from awtg.filtering.manager import AsyncHandler

from awtg.filtering.stdfilters.callback import CustomBinRPC
from awtg.filtering.stdfilters.std import requires_config

from database import NSFWDatabase
from const import (BOT_NOT_STARTED, CHECK_PM,
                   CONTENT_NOT_FOUND, NO_RIGHTS)


@AsyncHandler
async def view_nsfw(callback):
    args = callback.memory['cbinrpc_args']

    async with NSFWDatabase(callback.memory['config']['db']) as context:
        try:
            pic = await context.get_picture(args['db_file_id'])
        except IndexError:
            return callback.alert(CONTENT_NOT_FOUND)

    response = await callback.message.send_photo(pic['file_id'], chat_id=callback.data.from_.id)

    if not response['ok']:
        callback.alert(BOT_NOT_STARTED)

    callback.notify(CHECK_PM)


@AsyncHandler
async def remove_nsfw(callback):
    args = callback.memory['cbinrpc_args']
    db_id = args['db_file_id']

    async with NSFWDatabase(callback.memory['config']['db']) as context:
        try:
            pic = await context.get_picture(db_id)
        except IndexError:
            return callback.alert(CONTENT_NOT_FOUND)

        if pic['by_user'] != callback.data.from_.id:
            return callback.alert(NO_RIGHTS)

        await context.remove_picture(db_id)

    callback.notify('Удалено')

exports = (
    view_nsfw.add_filters(
        CustomBinRPC('view')
    ).add_mutual_callbacks(
        requires_config
    ).set_callback(),

    remove_nsfw.add_filters(
        CustomBinRPC('remove')
    ).add_mutual_callbacks(
        requires_config
    ).set_callback()
)
