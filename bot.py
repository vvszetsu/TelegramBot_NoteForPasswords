from backend.settings import TOKEN
import telebot as tb

bot = tb.TeleBot(TOKEN)
keyboard = tb.types.ReplyKeyboardMarkup()
keyboard.row('Да', 'Нет')
empty_kb = tb.types.ReplyKeyboardRemove()
