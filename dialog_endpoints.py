from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    ContextTypes,
)
from conv_enums import BotsDataKeys, UserConstantDataFields, UsersCallbacks
from google_sheets.google_sheets import ClientsGoogleSheetsGetter, ShortClient

class BaseEndpoint: 
    def __init__(
            self,
            conversation_state: int,
            text: str,
            buttons: list[list[InlineKeyboardButton]],
            enter_callback_points:list[str] = None) -> None:
        self.conversation_state = conversation_state
        self.text = text
        self.buttons = buttons
        self.enter_callback_points = enter_callback_points

    def check_enter_callbacks(self, callback_data):
        return self.enter_callback_points and callback_data in self.enter_callback_points


    def previous_bots_responce_text_different(self, context: ContextTypes.DEFAULT_TYPE):
        return context.user_data.get(BotsDataKeys.last_bots_message_text.value) != self.text


    def change_state(self, context: ContextTypes.DEFAULT_TYPE) -> int:
        context.user_data[BotsDataKeys.last_bots_message_text.value] = self.text
        return self.conversation_state


    async def edit_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await context.bot.edit_message_text(
            chat_id=update.effective_chat.id,
            message_id=context.user_data[BotsDataKeys.last_bots_message_id.value],
            text=self.text, 
            reply_markup=InlineKeyboardMarkup(self.buttons))
    
 
    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        await self.edit_message(update, context)
        return self.change_state(context)
    
 
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        if self.previous_bots_responce_text_different(context):
            await self.edit_message(update, context)        
        await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=update.message.message_id)
        return self.change_state(context)



class ClientListEndpoint(BaseEndpoint):

    async def send_messages_from_clients_table(self, update: Update, context: ContextTypes.DEFAULT_TYPE, clients: list[ShortClient]):
        clients_text_for_message = ""

        for i in range(len(clients)):
            clients_text_for_message += f"{clients[i].name} --> {clients[i].payment_date}\n"
            if ((i + 1) % 10 == 0) or i == (len(clients) - 1):
                await context.bot.send_message(update.effective_chat.id, clients_text_for_message)
                clients_text_for_message = "" 

    async def send_clients_list(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        current_clients, future_clietns  = ClientsGoogleSheetsGetter().get_clients_by_responsible_user(context.user_data.get(UsersCallbacks.user_profile.value))
        await context.bot.send_message(update.effective_chat.id, text=f"не оплатившие клиенты {len(current_clients)} человек(а)")
        await self.send_messages_from_clients_table(update, context, current_clients)
        await context.bot.send_message(update.effective_chat.id, text="не взятые клиенты")
        await self.send_messages_from_clients_table(update, context, future_clietns)
        
        last_message = await context.bot.send_message(update.effective_chat.id, text=self.text, reply_markup=InlineKeyboardMarkup(self.buttons))
        context.user_data[BotsDataKeys.last_bots_message_id.value] = last_message.message_id
        context.user_data[BotsDataKeys.last_bots_message_text.value] = last_message.text
          
    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=context.user_data[BotsDataKeys.last_bots_message_id.value])
        # await context.bot.send_message(update.effective_chat.id, text="предыдущее сообщение удаено")
        await self.send_clients_list(update, context)
        return self.change_state(context)


class SetTimerEndPoint(BaseEndpoint):
    async def set_date_time():
        ...


class UpdateRecipientEndpoint(BaseEndpoint):
    def __init__(
            self,
            conversation_state: int,
            text: str, buttons: list[list[InlineKeyboardButton]],
            enter_callback_points:list[str] = None,
            next_write_field_name: str = None
            ) -> None:
        self.next_write_field_name = next_write_field_name
        super().__init__(conversation_state, text, buttons, enter_callback_points)


    def write_data_if_field_key_exists(self, data: str, context: ContextTypes.DEFAULT_TYPE):
        field_name = context.user_data.get(UserConstantDataFields.write_data_field_name.value)
        if field_name:
            context.user_data[field_name] = data


    def set_new_data_write_key_if_exists(self, context: ContextTypes.DEFAULT_TYPE):
        if self.next_write_field_name:
            context.user_data[UserConstantDataFields.write_data_field_name.value] = self.next_write_field_name
        

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        if self.previous_bots_responce_text_different(context):
            self.write_data_if_field_key_exists(data=update.message.text, context=context)
        self.set_new_data_write_key_if_exists(context)
        return await super().handle_message(update, context)
    
    
    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        if self.previous_bots_responce_text_different(context):
            self.write_data_if_field_key_exists(data=update.callback_query.data, context=context)      
        self.set_new_data_write_key_if_exists(context)
        return await super().handle_callback(update, context)


class MainMenuEndPoint(UpdateRecipientEndpoint):
    async def handle_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        if update.message.text == "/start":
            
            message = await update.message.reply_text(self.text, reply_markup=InlineKeyboardMarkup(self.buttons))
            context.user_data[BotsDataKeys.last_bots_message_id.value] = message.message_id
            return self.change_state(context)
            # return self.conversation_state
            
    