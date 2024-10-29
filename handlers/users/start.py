from aiogram import types
from aiogram.dispatcher.filters.builtin import CommandStart
from keyboards.default.menu import menu_start
from keyboards.inline.weather_buttons import get_forecast_buttons
from loader import dp
from aiogram.types import CallbackQuery
from datetime import datetime
import requests



@dp.message_handler(CommandStart())
async def bot_start(message: types.Message):
    text="Assalomu alaykum Ob-havo botiga xush kelibsiz"
    text+="agar siz qayerda ekanligingizni bilmasangiz "
    text+="manzil kinopkasi ustiga bosing!!"
    text+="agar boshqa joyning ob-havo malumotlari kerak bo`lsa"
    text+="shahar nomini kiriting!!"
    await message.answer(text,reply_markup=menu_start)
    await message.reply(
        f"<b>Assalomu alaykum {message.from_user.first_name}! \nIstalgan shahar nomini kiriting: </b>",
        parse_mode='HTML'
    )


@dp.message_handler(content_types=types.ContentType.LOCATION)
async def location_addres_function(message:types.Message):
    lon=message.location.longitude
    lat=message.location.latitude

    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true&daily=temperature_2m_max,temperature_2m_min,precipitation_sum,windspeed_10m_max&timezone=auto"
    response=requests.get(url)

    if response.status_code==200:
        data=response.json()
        if 'daily' in data:
            today=data['daily']['time'][0]
            temp_max=data['daily']['temperature_2m_max'][0]
            temp_min=data['daily']['temperature_2m_min'][0]
            precipitation=data['daily']['precipitation_sum'][0]
            win_speed=data['daily']['windspeed_10m_max'][0]

            answer=(
                f"🗓**Sana:** {today}\n\n"
                f"🔼**Eng yuqori harorat:** {temp_max}°C\n"
                f"🔼**Eng past harorat:** {temp_min}°C\n"
                f"☁️**Yog'ingarchilik:** {precipitation}\n"
                f"💨**Shamol tezligi:** {win_speed}\n"
            )

        else:
            answer=(
                "❌Kunlik ob-havo ma'lumotlari mavjud emas."

            )

    else:
        answer = (
            f"❌ Xatolik yuz berdi : {response.status_code}"

        )
    await message.answer(answer,parse_mode="Markdown",reply_markup=get_forecast_buttons(lat,lon))



@dp.callback_query_handler(lambda c:c.data.startswith('forecast_'))
async def buttons_callback_text(calback_query:CallbackQuery):
    _,days,lat,lon=calback_query.data.split('_')
    days=int(days)

    url = (
        f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&daily=temperature_2m_max,"
        f"temperature_2m_min,precipitation_sum,windspeed_10m_max&timezone=auto"
    )

    response=requests.get(url)
    if response.status_code==200:
        data=response.json()
        if 'daily' in data:
            answer=f"🗓**{days}:** kunlik ob-havo ma'lumotlari\n\n"
            for i in range(min(days,len(data['daily']['time']))):
                today = data['daily']['time'][i]
                temp_max = data['daily']['temperature_2m_max'][i]
                temp_min = data['daily']['temperature_2m_min'][i]
                precipitation = data['daily']['precipitation_sum'][i]
                win_speed = data['daily']['windspeed_10m_max'][i]

                answer += (
                    f"🗓**Sana:** {today}\n\n"
                    f"🔼**Eng yuqori harorat:** {temp_max}°C\n"
                    f"🔼**Eng past harorat:** {temp_min}°C\n"
                    f"☁️**Yog'ingarchilik:** {precipitation}\n"
                    f"💨**Shamol tezligi:** {win_speed}\n"
                )
        else:
            answer=(
                "❌Kunlik ob-havo ma'lumotlari mavjud emas."

            )

    else:
        answer = (
            f"❌ Xatolik yuz berdi : {response.status_code}"

        )
    await calback_query.message.delete()
    await calback_query.message.answer(answer,parse_mode="Markdown",reply_markup=get_forecast_buttons(lat,lon))








@dp.message_handler()
async def get_weather(message: types.Message, ob_havo_Token='f1f286c46c37811adab96607defc546e'):
    iconka_kodlari = {
        "Clear": "Quyoshli havo \U00002600",
        "Clouds": "Bulutli havo \U00002601",
        "Rain": "Yomg'irli havo \U00002614",
        "Drizzle": "Yomg'irli havo \U00002614",
        "Thunderstorm": "Chaqmoq \U000026A1",
        "Snow": "Qor \U0001F328",
        "Mist": "Tuman \U0001F32B"
    }
    try:
        r = requests.get(
            f"http://api.openweathermap.org/data/2.5/weather?q={message.text}&appid={ob_havo_Token}&units=metric"
        )
        data = r.json()
        shahar = data["name"]
        harorat = data["main"]["temp"]
        ikonka = data["weather"][0]["main"]
        sm = iconka_kodlari.get(ikonka, "Bu yerdan ko'rinmayabdi :)")
        namlik = data["main"]["humidity"]
        bosim = data["main"]["pressure"]
        shamol = data["wind"]["speed"]
        quyosh_chiqishi = datetime.fromtimestamp(data["sys"]["sunrise"])
        quyosh_botishi = datetime.fromtimestamp(data["sys"]["sunset"])
        kunning_uzunligi = quyosh_botishi - quyosh_chiqishi

        await message.reply(
            f"<b>Xozirgi Vaqt Bo'yicha ({datetime.now().strftime('%Y-%m-%d %H:%M')})\n\n"
            f"{shahar} shahar ob-havosi!\nHarorat: {harorat}°C  {sm}\n"
            f"Namlik: {namlik}%\nBosim: {bosim} mm sim. ust\nShamol: {shamol} m/s\n"
            f"Quyosh chiqishi: {quyosh_chiqishi}\nQuyosh botishi: {quyosh_botishi}\nKunning uzunligi: {kunning_uzunligi}\n"
            f"\nSalomat bo'ling! \U0001F642</b>", parse_mode='HTML'
        )
    except Exception as e:
        await message.reply(f'\U0001F642 Shahar nomi topilmadi: {str(e)} \U0001F642')






