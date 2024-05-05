import telebot
from telebot import types
import random

bot = telebot.TeleBot('5697146554:AAHQ7n5Aff6tslbXFfgYRnWeNJqv-lPiyA8')

lobby = {}

def new_game(size):
    return [[0]*size for _ in range(size)]

def is_valid_move(move, size):
    try:
        x, y = map(int, move.split(','))
        return 0 <= x < size and 0 <= y < size
    except:
        return False

def check_winner(board):
    size = len(board)
    for i in range(size):
        if len(set(board[i])) == 1 and board[i][0] != 0:
            return board[i][0]
        if len(set(board[j][i] for j in range(size))) == 1 and board[0][i] != 0:
            return board[0][i]
    if len(set(board[i][i] for i in range(size))) == 1 and board[0][0] != 0:
        return board[0][0]
    if len(set(board[i][size-i-1] for i in range(size))) == 1 and board[0][size-1] != 0:
        return board[0][size-1]
    return 0

def log_game(board, winner):
    with open('game_log.txt', 'a') as f:
        f.write('Игра окончена. Победитель: ' + str(winner) + '\n')
        for row in board:
            f.write(' '.join(map(str, row)) + '\n')
        f.write('\n')

def ai_move(board):
    available_moves = [(i, j) for i in range(len(board)) for j in range(len(board[i])) if board[i][j] == 0]
    if available_moves:
        return random.choice(available_moves)
    return None

# Функция для проверки на наличие доступных ходов
def has_available_moves(board):
    for row in board:
        if 0 in row:
            return True
    return False

# Обработчик команды /start_bot
@bot.message_handler(commands=['start_bot'])
def start_bot(message):
    size = 3  # Размер поля по умолчанию
    chat_id = message.chat.id
    lobby[chat_id] = {'board': new_game(size), 'turn': 1, 'size': size}
    display_board(chat_id)

# Функция для создания клавиатуры игрового поля
def get_keyboard(size):
    keyboard = types.InlineKeyboardMarkup(row_width=size)
    for i in range(size):
        row_buttons = [types.InlineKeyboardButton(f" ", callback_data=f"{i},{j}") for j in range(size)]
        keyboard.add(*row_buttons)
    return keyboard

# Функция для отображения игрового поля
def display_board(chat_id):
    board = lobby[chat_id]['board']
    size = lobby[chat_id]['size']
    symbols = {0: '⬜️', 1: '❌', 2: '⭕️'}
    board_str = '\n'.join([' '.join([symbols[cell] for cell in row]) for row in board])
    if 'board_message_id' in lobby[chat_id]:
        bot.edit_message_text(chat_id=chat_id, message_id=lobby[chat_id]['board_message_id'], text=board_str, reply_markup=get_keyboard(size))
    else:
        msg = bot.send_message(chat_id, board_str, reply_markup=get_keyboard(size))
        lobby[chat_id]['board_message_id'] = msg.message_id

# Обработчик для хода игрока
@bot.callback_query_handler(func=lambda call: True)
def make_move(call):
    chat_id = call.message.chat.id
    if lobby.get(chat_id) is None:
        return
    player = lobby[chat_id]['turn']
    try:
        x, y = map(int, call.data.split(','))
        size = lobby[chat_id]['size']
        if not is_valid_move(call.data, size) or lobby[chat_id]['board'][x][y] != 0:
            return
        lobby[chat_id]['board'][x][y] = player
        display_board(chat_id)
        winner = check_winner(lobby[chat_id]['board'])
        if winner == 0:
            ai_player = 3 - player
            move = ai_move(lobby[chat_id]['board'])
            if move:
                x, y = move
                lobby[chat_id]['board'][x][y] = ai_player
                display_board(chat_id)
                winner = check_winner(lobby[chat_id]['board'])
        if winner != 0:
            bot.reply_to(call.message, f"Победил игрок {winner}!")
            log_game(lobby[chat_id]['board'], winner)
            del lobby[chat_id]
        elif not has_available_moves(lobby[chat_id]['board']):
            bot.reply_to(call.message, "Ничья!")
            log_game(lobby[chat_id]['board'], 0)
            del lobby[chat_id]
    except Exception as e:
        print(e)

bot.polling()