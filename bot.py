import json
from bot_paths.paths import BOT_TOKEN
from telegram import InlineKeyboardButton, Update, InlineKeyboardMarkup

from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)


from conv_enums import UsersCallbacks, MainMenuCallbacks, ClientListCallbacks
from dialog_endpoints import MainMenuEndPoint, UpdateRecipientEndpoint, ClientListEndpoint

(
    MAIN_MENU,
    USER_CHOOSE,
    SET_TIMER,
    GET_USER_LIST,
) = range(4)


main_menu_buttons = [
    [InlineKeyboardButton(text="выбрать ответсвенного", callback_data=MainMenuCallbacks.chose_user.value)],
    # [InlineKeyboardButton(text="установить дни когда получать список неоплативших пользователей", callback_data=MainMenuCallbacks.set_timer.value)],
    [InlineKeyboardButton(text="получить список для тещего ответственного",callback_data=MainMenuCallbacks.get_current_clients.value)]
]

user_chose_buttons = [
    [InlineKeyboardButton("Loqi", callback_data=UsersCallbacks.loqi.value)],
    [InlineKeyboardButton("Андрей Осипов", callback_data=UsersCallbacks.andrei.value)],
    [InlineKeyboardButton("Артем", callback_data=UsersCallbacks.artem.value)],
    [InlineKeyboardButton("Алексей", callback_data=UsersCallbacks.sergei.value)],
    [InlineKeyboardButton("Все", callback_data=UsersCallbacks.everybody.value)],
]

clients_message_buttons = [[
    InlineKeyboardButton("В меню", callback_data=ClientListCallbacks.main_menu.value)
]]


main_menu_endpoint = MainMenuEndPoint(
    conversation_state=MAIN_MENU,
    text="LOL",
    buttons=main_menu_buttons,
    enter_callback_points=[
        UsersCallbacks.loqi.value,
        UsersCallbacks.andrei.value,
        UsersCallbacks.artem.value,
        UsersCallbacks.sergei.value,
        UsersCallbacks.everybody.value
    ])


user_choose_endpoint = UpdateRecipientEndpoint(
    USER_CHOOSE, 
    text="выбери профиль",
    next_write_field_name=UsersCallbacks.user_profile.value,
    buttons=user_chose_buttons)


clients_list_endpoint = ClientListEndpoint(
    GET_USER_LIST,
    text="====================",
    buttons=clients_message_buttons    
)


def main():
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', main_menu_endpoint.handle_command)],
        states = {
            MAIN_MENU: [
                # CallbackQueryHandler(),
                CallbackQueryHandler(user_choose_endpoint.handle_callback, MainMenuCallbacks.chose_user.value),
                CallbackQueryHandler(clients_list_endpoint.handle_callback, MainMenuCallbacks.get_current_clients.value),
                MessageHandler(filters.Text(), main_menu_endpoint.handle_message)
            ],
            USER_CHOOSE: [
                CallbackQueryHandler(main_menu_endpoint.handle_callback, main_menu_endpoint.check_enter_callbacks)
            ],
            GET_USER_LIST: [
                CallbackQueryHandler(main_menu_endpoint.handle_callback, ClientListCallbacks.main_menu.value)
            ]

        },
        fallbacks=[MessageHandler(filters.Text(), main_menu_endpoint.handle_message)]
    )

    
    with open(BOT_TOKEN) as file:
        bot_token = json.load(file)["token"]

    application = Application.builder().token(bot_token).build()
    application.add_handler(conv_handler)
    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()