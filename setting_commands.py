from aiogram.types import BotCommand, BotCommandScopeDefault


async def set_default_commands(bot):
    my_commands = [
        BotCommand('start', 'Запуск'),
        BotCommand('cancel', 'Отмена'),
    ]
    await bot.set_my_commands(
        commands=my_commands,
        scope=BotCommandScopeDefault()
    )
