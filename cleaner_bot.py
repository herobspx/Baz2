import logging
import os
from aiogram import Bot, Dispatcher, executor, types
from aiogram.utils.exceptions import MessageToDeleteNotFound, MessageCantBeDeleted, ChatAdminRequired
from dotenv import load_dotenv

# ===== إعدادات عامة =====
logging.basicConfig(level=logging.INFO)
load_dotenv()

BOT_TOKEN     = os.getenv("CLEANER_TOKEN") or os.getenv("JOIN_TOKEN") or os.getenv("BOT_TOKEN")
TARGET_CHAT_ID = os.getenv("TARGET_CHAT_ID")  # اختياري لتقييد العمل على مجموعة معيّنة
ADMIN_ID      = os.getenv("ADMIN_ID")         # اختياري: معرف المشرف لإرسال تنبيه عند التشغيل

if not BOT_TOKEN:
    raise RuntimeError("CLEANER_TOKEN مفقود. أضفه في Render > Environment.")

bot = Bot(token=BOT_TOKEN, parse_mode="HTML")
dp = Dispatcher(bot)

def in_target_chat(message: types.Message) -> bool:
    """يتأكد أن الرسالة داخل المجموعة المطلوبة (إذا تم ضبط TARGET_CHAT_ID)."""
    if not TARGET_CHAT_ID:
        return True
    try:
        return str(message.chat.id) == str(TARGET_CHAT_ID)
    except Exception:
        return False

async def delete_service_message(message: types.Message):
    """يحذف الرسالة الخدمية بأمان مع معالجة الاستثناءات."""
    try:
        await message.delete()
        logging.info(f"Deleted service message {message.message_id} in chat {message.chat.id}")
    except (MessageToDeleteNotFound, MessageCantBeDeleted) as e:
        logging.warning(f"Can't delete message {message.message_id}: {e}")
    except ChatAdminRequired:
        logging.error("البوت يحتاج صلاحية حذف الرسائل (اجعله مشرفًا بصلاحية الحذف).")
    except Exception as e:
        logging.exception(f"Unexpected error while deleting message: {e}")

# ===== معالجات الرسائل الخدمية =====
# انضمام أعضاء (بما فيها الانضمام عبر رابط دعوة)
@dp.message_handler(content_types=['new_chat_members'])
async def handle_new_members(message: types.Message):
    if not in_target_chat(message): 
        return
    await delete_service_message(message)

# مغادرة عضو
@dp.message_handler(content_types=['left_chat_member'])
async def handle_left_member(message: types.Message):
    if not in_target_chat(message):
        return
    await delete_service_message(message)

# تغيير عنوان المجموعة
@dp.message_handler(content_types=['new_chat_title'])
async def handle_new_title(message: types.Message):
    if not in_target_chat(message):
        return
    await delete_service_message(message)

# تغيير صورة المجموعة
@dp.message_handler(content_types=['new_chat_photo', 'delete_chat_photo'])
async def handle_photo_changes(message: types.Message):
    if not in_target_chat(message):
        return
    await delete_service_message(message)

# تثبيت رسالة
@dp.message_handler(content_types=['pinned_message'])
async def handle_pinned(message: types.Message):
    if not in_target_chat(message):
        return
    await delete_service_message(message)

# (اختياري) فلترة رسائل النظام القادمة عبر chat_member updates
# لا تُنشئ رسالة مرئية عادةً، لكن نضعها للاكتمال
@dp.chat_member_handler()
async def on_chat_member_update(event: types.ChatMemberUpdated):
    if TARGET_CHAT_ID and str(event.chat.id) != str(TARGET_CHAT_ID):
        return
    # لا يوجد delete هنا (لأنها ليست رسالة)، نكتفي بالتسجيل
    logging.info(f"Chat member update in {event.chat.id}: {event.from_user.id}")

# رسالة /start مختصرة للمالك
@dp.message_handler(commands=['start'])
async def start_cmd(message: types.Message):
    if not in_target_chat(message) and message.chat.type == 'private':
        await message.answer("بوت تنظيف الرسائل الخدمية يعمل 👌\n\n"
                             "أضِف البوت إلى مجموعتك كـ مشرف مع صلاحية حذف الرسائل.")
        return

async def on_startup(_):
    if ADMIN_ID:
        try:
            await bot.send_message(ADMIN_ID, "✅ بوت التنظيف بدأ العمل.")
        except Exception:
            pass
    logging.info("Cleaner bot is up and running.")

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
