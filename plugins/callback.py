from awtg.filtering.manager import AsyncHandler

from awtg.filtering.stdfilters.callback import CustomBinRPC
from awtg.filtering.stdfilters.std import requires_config

from database import NSFWDatabase
from const import BOT_NOT_STARTED, CHECK_PM


@AsyncHandler
async def view_nsfw(callback):
    args = callback.memory['cbinrpc_args']

    async with NSFWDatabase(callback.memory['config']['db']) as context:
        try:
            pic = await context.get_picture(args['db_file_id'])
        except IndexError:
            return callback.alert()

    response = await callback.message.send_photo(pic['file_id'], chat_id=callback.data.from_.id)

    if not response['ok']:
        callback.alert(BOT_NOT_STARTED)

    callback.notify(CHECK_PM)

exports = (
    view_nsfw.add_filters(
        CustomBinRPC('view')
    ).add_mutual_callbacks(
        requires_config
    ).set_callback(),
)
