from awtg.api import Telegram

from awtg.filtering.manager import Manager
from awtg.filtering.plugin_extractors import extract_from_dir

from awtg.configparser import load

config = load('config.awcfg')
plugins = extract_from_dir('plugins')

manager = Manager(config=config)
manager.import_plugins(plugins)

tg = Telegram(config['token'])
tg.set_callback(manager)

tg.poll()
