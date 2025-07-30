import datetime

dt_now = datetime.datetime(2025, 7, 13)
days_ago = (datetime.datetime.now() - dt_now).days
__appid__ = 'usound'
__title__ = 'usound (kNowlege the Sound)'
__version__ = '0.1.7'
__copyright__ = f'Copyright © 2023-{dt_now.strftime("%Y")} hamacom2004jp'
__pypiurl__ = 'https://pypi.org/project/usound/'
__srcurl__ = 'https://github.com/hamacom2004jp/usound'
__docurl__ = 'https://hamacom2004jp.github.io/usound/index.html'
# https://patorjk.com/software/taag/#p=display&f=ANSI%20Shadow&t=usound
__logo__ = '''
██╗   ██╗███████╗ ██████╗ ██╗   ██╗███╗   ██╗██████╗ 
██║   ██║██╔════╝██╔═══██╗██║   ██║████╗  ██║██╔══██╗
██║   ██║███████╗██║   ██║██║   ██║██╔██╗ ██║██║  ██║
██║   ██║╚════██║██║   ██║██║   ██║██║╚██╗██║██║  ██║
╚██████╔╝███████║╚██████╔╝╚██████╔╝██║ ╚████║██████╔╝
 ╚═════╝ ╚══════╝ ╚═════╝  ╚═════╝ ╚═╝  ╚═══╝╚═════╝ '''
__description__ = f'{__title__} {__version__}\n\n' + \
                  f'{__copyright__}\n' + \
                  (f'Build Date: {dt_now.strftime("%Y-%m-%d")}\n' if days_ago < 60 else '') + \
                  f'Web Site: PyPi <{__pypiurl__}>\n' + \
                  f'Web Site: SorceCode <{__srcurl__}>\n' + \
                  f'Web Site: Document <{__docurl__}>\n' + \
                  f'License: MIT License <https://opensource.org/license/mit/>\n' + \
                  f'This is free software: you are free to change and redistribute it.\n' + \
                  f'There is NO WARRANTY, to the extent permitted by law.'
__all__ = ['__logo__', '__title__', '__version__', '__copyright__', '__srcurl__', '__docurl__']
