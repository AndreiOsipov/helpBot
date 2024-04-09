from enum import Enum


class ClientListCallbacks(Enum):
    main_menu = "main_menu"


class BotsDataKeys(Enum):
    last_bots_message_id = "last_bots_message_id"
    last_bots_message_text = "last_bots_message_text"


class UserConstantDataFields(Enum):
    write_data_field_name = "write_data_field_name"


class UsersCallbacks(Enum):
    user_profile = "user_profile"

    loqi = "Андрей"
    andrei = "Андрей Осипов"
    artem = "Артем"
    sergei = "Серега"
    everybody = "Все"


class MainMenuCallbacks(Enum):
    chose_user = "chose_user"
    set_timer = "set_timer"
    get_current_clients = "get_current_clients"