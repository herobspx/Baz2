import os
import logging
from aiogram import Bot, Dispatcher, executor, types

logging.basicConfig(level=logging.INFO)

API_TOKEN = os.getenv("CLEAN_TOKEN")
if not API_TOKEN:
    raise RuntimeError("CLEAN_TOKEN is missing. Set it in Render > Environment.")

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# أنواع رسائل الخدمة التي نحذفها
SERVICE_TYPES = [
    types.ContentType.NEW_CHAT_MEMBERS,   # انضمام عبر رابط/إضافة
    types.ContentType.LEFT_CHAT_MEMBER,   # مغادرة/إزالة
    types.ContentType.NEW_CHAT_TITLE,     # تغيير الاسم
    types.ContentType.NEW_CHAT_PHOTO,     # تغيير الصورة
    types.ContentType.DELETE_CHAT_PHOTO,  # حذف صورة المجموعة
    types.ContentType.PINNED_MESSAGE,     # تم تثبيت رسالة
]

# (اختياري) لو تبغى تقيّد الحذف على مجموعة معيّنة فقط
TARGET_CHAT_ID = os.getenv("TARGET_CHAT_ID")  # مثال: "-1003041770290"

@dp.message_handler(content_types=SERVICE_TYPES,
                    chat_type=[types.ChatType.GROUP, types.ChatType.SUPERGROUP])
async def delete_service_messages(message: types.Message):
    # لو محددنا مجموعة معيّنة، تجاهل الباقي
    if TARGET_CHAT_ID and str(message.chat.id) != str(TARGET_CHAT_ID):
        return
    try:
        await message.delete()
        logging.info(f"Deleted service message in chat {message.chat.id}")
    except Exception as e:
        logging.warning(f"Couldn't delete service message: {e}")

# (اختياري) منع ظهور رسالة "قام بتثبيت رسالة" القديمة أثناء التشغيل
@dp.message_handler(lambda m: m.text and "قام بتثبيت" in m.text, 
                    chat_type=[types.ChatType.GROUP, types.ChatType.SUPERGROUP])
async def maybe_delete_text_notifications(message: types.Message):
    if TARGET_CHAT_ID and str(message.chat.id) != str(TARGET_CHAT_ID):
        return
    try:
        await message.delete()
    except Exception as e:
        logging.warning(f"Couldn't delete text notification: {e}")

if __name__ == "__main__":
    # skip_updates=True يتجاهل الرسائل القديمة حتى ما تظهر إشعارات قديمة
    executor.start_polling(dp, skip_updates=True)
