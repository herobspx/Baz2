import os
import logging
from aiogram import Bot, Dispatcher, executor, types

# ========= إعدادات عامة =========
API_TOKEN = os.getenv("CLEANER_BOT_TOKEN")
if not API_TOKEN:
    raise RuntimeError("CLEANER_BOT_TOKEN مفقود. أضِفه في Render > Environment.")

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# كلمات/عبارات نعتبرها رسالة نظامية مزعجة (لو ظهرت كنص عادي)
BLOCK_WORDS = [
    "انضم", "غادر", "غادَر", "تمت دعوة", "غير اسم المجموعة", "غيّر اسم المجموعة",
    "غير صورة المجموعة", "غيّر صورة المجموعة", "ثبّت الرسائل", "تم التثبيت"
]

# ========= حذف رسائل “الخدمة” التي يصدرها تيليجرام تلقائياً =========
# أعضاء جدد
@dp.message_handler(content_types=['new_chat_members'])
async def _del_new_members(message: types.Message):
    try:
        await message.delete()
    except Exception as e:
        logging.warning(f"لم أستطع حذف رسالة دخول عضو: {e}")

# عضو غادر
@dp.message_handler(content_types=['left_chat_member'])
async def _del_left_member(message: types.Message):
    try:
        await message.delete()
    except Exception as e:
        logging.warning(f"لم أستطع حذف رسالة خروج عضو: {e}")

# تغيير اسم المجموعة
@dp.message_handler(content_types=['new_chat_title'])
async def _del_new_title(message: types.Message):
    try:
        await message.delete()
    except Exception as e:
        logging.warning(f"لم أستطع حذف رسالة تغيير الاسم: {e}")

# تغيير صورة المجموعة
@dp.message_handler(content_types=['new_chat_photo', 'delete_chat_photo'])
async def _del_photo_updates(message: types.Message):
    try:
        await message.delete()
    except Exception as e:
        logging.warning(f"لم أستطع حذف رسالة تغيير الصورة: {e}")

# ========= فلترة أي نص/تسمية مع صورة تحتوي كلمات مزعجة =========
@dp.message_handler(content_types=types.ContentType.ANY)
async def _del_keywords(message: types.Message):
    text = (message.text or "") + " " + (message.caption or "")
    if any(word in text for word in BLOCK_WORDS):
        try:
            await message.delete()
        except Exception as e:
            logging.warning(f"لم أستطع حذف رسالة مطابقة للكلمات: {e}")

if __name__ == "__main__":
    # يفضّل تشغيله بـ skip_updates لتجاهل الرسائل القديمة عند إعادة التشغيل
    executor.start_polling(dp, skip_updates=True)
