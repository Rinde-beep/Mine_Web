import sqlite3
import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message, KeyboardButton, ReplyKeyboardRemove, ReplyKeyboardMarkup
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import Command
from werkzeug.security import generate_password_hash, check_password_hash
from aiogram.client.default import DefaultBotProperties
from config import BOT_TOKEN
from aiogram.fsm.state import any_state

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.DEBUG
)
logger = logging.getLogger(__name__)

# переменные
name = None
password = None
balance = 0
donate_options = {
    "Воин - 200 руб.": 200,
    "Офицер - 500 руб.": 500,
    "Генерал - 1000 руб.": 1000,
    "Маршал - 1999 руб.": 1999,
    "Император - 3999 руб.": 3999
}

TOKEN = BOT_TOKEN
bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

# таблица для регистрации и для входа
reg_log_keyboard = [[KeyboardButton(text='/registration'), KeyboardButton(text='/login')]]

# таблица для доната
donate_keyboard = [[KeyboardButton(text='Воин - 200 руб.'), KeyboardButton(text='Офицер - 500 руб.')],
                   [KeyboardButton(text='Генерал - 1000 руб.'), KeyboardButton(text='Маршал - 1999 руб.')],
                   [KeyboardButton(text='Император - 3999 руб.')],
                   [KeyboardButton(text='/main')]]

# таблица для выбора количества денег для пополнения на счет
balance_keyboard = [[KeyboardButton(text='300 руб.'), KeyboardButton(text='500 руб.')],
                    [KeyboardButton(text='1200 руб.'), KeyboardButton(text='4000 руб.')],
                    [KeyboardButton(text='/main')]
                    ]

# главная таблица
main_keyboard = [[KeyboardButton(text='/help'), KeyboardButton(text='/donate')],
                 [KeyboardButton(text='/balance'), KeyboardButton(text='/add_balance')]]

mk = ReplyKeyboardMarkup(keyboard=main_keyboard, resize_keyboard=True, one_time_keyboard=False)
bk = ReplyKeyboardMarkup(keyboard=balance_keyboard, resize_keyboard=True, one_time_keyboard=False)
rl = ReplyKeyboardMarkup(keyboard=reg_log_keyboard, resize_keyboard=True, one_time_keyboard=False)
dk = ReplyKeyboardMarkup(keyboard=donate_keyboard, resize_keyboard=True, one_time_keyboard=False)


# работа с состояниями сообщений
class Register(StatesGroup):
    username = State()
    password = State()


class Login(StatesGroup):
    username = State()
    password = State()


def check_password(passwd: str):
    if passwd.startswith("/"):
        return
    special = "!@#$%^&*"
    numbers = "1234567890"
    uppercase = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

    if len(passwd) < 8:
        return False, "Пароль должен быть не меньше 8 символов."

    has_special = False
    for ch in passwd:
        if ch in special:
            has_special = True
            break
    if not has_special:
        return False, "Пароль должен содержать хотя бы один специальный символ."

    has_digit = False
    for ch in passwd:
        if ch in numbers:
            has_digit = True
            break
    if not has_digit:
        return False, "Пароль должен содержать хотя бы одну цифру."

    has_upper = False
    for ch in passwd:
        if ch in uppercase:
            has_upper = True
            break
    if not has_upper:
        return False, "Пароль должен содержать хотя бы одну заглавную букву."

    return True, ""


@dp.message(Command("start") or Command('старт'))
async def start_cmd(message: Message, state: FSMContext):
    photo = types.FSInputFile("static/img/minecraft.png")
    await message.answer_photo(
        photo=photo,
        caption="👋 Привет! Добро пожаловать на наш сервер!\n\n"
                "Для начала пройди регистрацию или войди в свой аккаунт.\n"
                "Если у вас будут вопросы, обратитесь к /help.\n",
        reply_markup=rl
    )
    await state.clear()


@dp.message(Command("registration"))
async def registration_start(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Введите логин (от 2 до 10 символов):")
    await state.set_state(Register.username)


@dp.message(Register.username)
async def registration_username(message: Message, state: FSMContext):
    if message.text.startswith("/"):
        if message.text == '/help':
            await state.clear()
            await help(message)
        elif message.text == '/balance':
            await state.clear()
            await balance(message)
        elif message.text == '/login':
            await state.clear()
            await login_start(message, state)
        elif message.text == '/add_balance':
            await state.clear()
            await add_balance_command(message)
        elif message.text == '/info':
            await state.clear()
            await info_command(message)
        elif message.text == '/donate':
            await state.clear()
            await donate_command(message)
        return
    username = message.text.strip()
    if not (2 <= len(username) <= 10):
        await message.answer("Логин должен быть от 2 до 10 символов.")
        return

    conn = sqlite3.connect("user.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM user WHERE user = ?", (username,))
    if cursor.fetchone():
        await message.answer("❌ Пользователь с таким логином уже существует.")
        conn.close()
        return
    conn.close()

    await state.update_data(username=username)
    await message.answer("Введите пароль (мин. 8 символов, заглавная буква, цифра, спец. символ):")
    await state.set_state(Register.password)


@dp.message(Register.password)
async def registration_password(message: Message, state: FSMContext):
    if message.text.startswith("/"):
        await state.clear()
        return
    passwd = message.text.strip()
    valid, reason = check_password(passwd)
    global name, password
    if not valid:
        await message.answer(f"❌ {reason}")
        return

    data = await state.get_data()
    username = data["username"]
    hashed_password = generate_password_hash(passwd)

    conn = sqlite3.connect("user.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO user (user, password, balance, donate) VALUES (?, ?, ?, ?)",
                   (username, hashed_password, 0, 1))
    conn.commit()
    conn.close()

    await message.answer(f"✅ Пользователь <b>{username}</b> успешно зарегистрирован!",
                         reply_markup=mk)
    name = username
    password = passwd

    await state.clear()


@dp.message(Command("login"))
async def login_start(message: Message, state: FSMContext):
    print('nen')
    await state.clear()
    await message.answer("Введите логин:")
    await state.set_state(Login.username)


@dp.message(Login.username)
async def login_username(message: Message, state: FSMContext):
    if message.text.startswith("/"):
        if message.text == '/help':
            await state.clear()
            await help(message)
        elif message.text == '/balance':
            await state.clear()
            await balance(message)
        elif message.text == '/registration':
            await state.clear()
            await registration_start(message, state)
        elif message.text == '/add_balance':
            await state.clear()
            await add_balance_command(message)
        elif message.text == '/info':
            await state.clear()
            await info_command(message)
        elif message.text == '/donate':
            await state.clear()
            await donate_command(message)
        return
    await state.update_data(username=message.text.strip())
    await message.answer("Введите пароль:")
    await state.set_state(Login.password)


@dp.message(Login.password)
async def login_password(message: Message, state: FSMContext):
    if message.text.startswith("/"):
        await state.clear()
        return
    global name, password, balance
    user_pass = message.text.strip()
    data = await state.get_data()
    user_login = data["username"]

    conn = sqlite3.connect("user.db")
    cursor = conn.cursor()
    cursor.execute("SELECT password FROM user WHERE user = ?", (user_login,))
    row = cursor.fetchone()
    conn.close()

    if row is None:
        await message.answer("❌ Такого пользователя не существует.")
        return

    stored_password_hash = row[0]
    if not check_password_hash(stored_password_hash, user_pass):
        await message.answer("❌ Неверный логин или пароль.")
        return
    name = user_login
    password = user_pass

    await message.answer(f"✅ Добро пожаловать, <b>{name}</b>! Вы успешно вошли в аккаунт.",
                         reply_markup=mk)
    await state.clear()


@dp.message(Command("help"))
async def help(message: Message):
    await message.answer('Вам доступны команды:\n'
                         '/start - начинает весь процес с нуля,\n'
                         '/login - начало входа в аккаунт,\n'
                         '/registration - начало регистрации,\n'
                         '/balance - проверка баланса,\n'
                         '/add_balance - пополнение баланса,\n'
                         '/donate - покупка доната,\n'
                         '/info - полная информация об игроке.')


@dp.message(Command('balance'))
async def balance(message: Message):
    if not name:
        await message.answer("⚠️ Вы не авторизованы. Войдите или зарегистрируйте аккаунт.")
        return
    try:
        conn = sqlite3.connect("user.db")
        cursor = conn.cursor()
        money = cursor.execute("SELECT balance FROM user WHERE user = ?", (name,)).fetchone()
        print(money)
        print(name, password)
        await message.answer(f'💎{name}, ваш баланс - {money[0]}.')
    except Exception as e:
        await message.answer('Похоже вы не зарегистрировались или не вошли в аккаунт!\n'
                             'Попробуйте еще раз.')


@dp.message(Command("add_balance"))
async def add_balance_command(message: types.Message, state: FSMContext):
    if not name:
        await message.answer("⚠️ Вы не авторизованы. Войдите или зарегистрируйте аккаунт.")
        return
    await message.answer("💰 Выберите сумму для пополнения:", reply_markup=bk)
    await state.set_state("choosing_balance")


@dp.message(Command("main"))
async def main(message: Message):
    await message.answer("Возвращаемся в главное меню...", reply_markup=mk)


@dp.message(lambda message: message.text in ["300 руб.", "500 руб.", "1200 руб.", "4000 руб."])
async def process_balance_choice(message: types.Message, state: FSMContext):
    if not name:
        await message.answer("⚠️ Вы не авторизованы. Войдите или зарегистрируйте аккаунт.")
        return

    money = int(message.text.split()[0])

    conn = sqlite3.connect("user.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE user SET balance = balance + ? WHERE user = ?", (money, name))
    conn.commit()
    conn.close()

    await message.answer(f"✅ Ваш баланс пополнен на {money} ₽!", reply_markup=mk)
    await state.clear()


@dp.message(Command("donate"))
async def donate_command(message: types.Message):
    if not name:
        await message.answer("⚠️ Вы не авторизованы. Войдите или зарегистрируйте аккаунт.")
        return
    await message.answer("💎 Выберите донат:", reply_markup=dk)


@dp.message(lambda message: message.text in donate_options)
async def process_donation(message: types.Message):
    if not name:
        await message.answer("⚠️ Сначала войдите в аккаунт командой /login")
        return

    item = message.text
    price = donate_options[item]
    donate_name = item.split(" -")[0]

    conn = sqlite3.connect("user.db")
    cursor = conn.cursor()

    # Получаем текущий баланс
    cursor.execute("SELECT balance FROM user WHERE user = ?", (name,))
    row = cursor.fetchone()
    current_balance = row[0]
    if current_balance < price:
        await message.answer(f"❌ Недостаточно средств! Ваш баланс: {current_balance} руб., нужно: {price} руб.")
        conn.close()
        return

    cursor.execute("SELECT id FROM donate WHERE name = ?", (item.split(' -')[0],))
    donate_row = cursor.fetchone()
    cursor.execute("SELECT balance, donate FROM user WHERE user = ?", (name,))
    user_row = cursor.fetchone()
    donate_id = donate_row[0]
    current_balance, current_donate = user_row

    # Проверка: если уже такой донат
    if current_donate == donate_id:
        await message.answer(f"⚠️ У вас уже есть донат <b>{donate_name}</b>.")
        conn.close()
        return
    if current_donate is not None and current_donate > donate_id:
        cursor.execute("SELECT name FROM donate WHERE id = ?", (current_donate,))
        current_donate_name = cursor.fetchone()[0]
        await message.answer(
            f"⚠️ У вас уже есть более высокий донат: <b>{current_donate_name}</b>.\n"
            f"Вы не можете купить <b>{donate_name}</b>."
        )
        conn.close()
        return
    # Обновляем баланс и назначаем донат
    cursor.execute(
        "UPDATE user SET balance = balance - ?, donate = ? WHERE user = ?",
        (price, donate_id, name)
    )
    conn.commit()
    conn.close()

    await message.answer(
        f"Спасибо за покупку!\nВы приобрели донат: <b>{item.split(' -')[0]}</b>.\nНовый баланс: {current_balance - price} руб.",
        reply_markup=mk
    )


@dp.message(Command("info"))
async def info_command(message: types.Message):
    if not name:
        await message.answer("⚠️ Вы не авторизованы. Войдите или зарегистрируйте аккаунт.")
        return
    conn = sqlite3.connect("user.db")
    cursor = conn.cursor()

    # Получаем id доната пользователя
    cursor.execute("SELECT donate FROM user WHERE user = ?", (name,))
    row = cursor.fetchone()
    donate_id = row[0]
    cursor.execute("SELECT name FROM donate WHERE id = ?", (donate_id,))
    donate_name = cursor.fetchone()
    conn.close()
    await message.answer(f'💎Информация об аккаунте: \n'
                         f'👤Имя: <b>{name}</b>\n'
                         f'🔑Пароль: <b>{password}</b>\n'
                         f'✨Уровень доната: <b>{donate_name[0]}</b>')


async def main_start():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main_start())
