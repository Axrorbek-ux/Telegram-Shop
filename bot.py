import os
import logging
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

TOKEN = os.environ.get("BOT_TOKEN")
ADMIN_ID = int(os.environ.get("ADMIN_ID", "0"))

logging.basicConfig(level=logging.INFO)

PRODUCTS = {
    "premium_3": ("💎 Premium — 3 oy", 168000),
    "premium_6": ("👑 Premium — 6 oy", 220000),
    "premium_12": ("💠 Premium — 12 oy", 0),
}


def main_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("💎 Telegram Premium", callback_data="premium")],
        [InlineKeyboardButton("⭐ Telegram Stars", callback_data="stars")],
        [InlineKeyboardButton("🛍️ Mening buyurtmalarim", callback_data="orders")],
        [InlineKeyboardButton("🎁 Aksiyalar", callback_data="offers")],
        [InlineKeyboardButton("📞 Yordam", callback_data="help")],
    ])


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "💎✨ TELEGRAM SHOP ⭐\n\n"
        "Xush kelibsiz!\n"
        "Premium va Stars xizmatlarini tanlang.\n\n"
        "🔥 Tezkor xizmat | 💬 Qo‘llab-quvvatlash"
    )
    await update.message.reply_text(
        text,
        reply_markup=main_menu()
    )


async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "premium":
        keyboard = [
            [InlineKeyboardButton(
                "💎 3 oy — 168 000 so‘m",
                callback_data="buy_premium_3"
            )],
            [InlineKeyboardButton(
                "👑 6 oy — 220 000 so‘m",
                callback_data="buy_premium_6"
            )],
            [InlineKeyboardButton(
                "💠 12 oy — narxni so‘rash",
                callback_data="buy_premium_12"
            )],
            [InlineKeyboardButton("⬅️ Bosh menyu", callback_data="home")],
        ]
        await query.edit_message_text(
            "💎 TELEGRAM PREMIUM\n\nKerakli muddatni tanlang:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif query.data == "stars":
        await query.edit_message_text(
            "⭐ TELEGRAM STARS\n\n"
            "Stars buyurtmasi uchun yordam xizmatiga murojaat qiling.\n"
            "Narxlar buyurtma vaqtida aniqlashtiriladi.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton(
                    "📞 Yordam",
                    callback_data="help"
                )],
                [InlineKeyboardButton(
                    "⬅️ Bosh menyu",
                    callback_data="home"
                )],
            ])
        )

    elif query.data.startswith("buy_"):
        product_key = query.data[4:]
        product = PRODUCTS.get(product_key)

        if not product:
            await query.edit_message_text("Mahsulot topilmadi.")
            return

        name, price = product
        price_text = f"{price:,}".replace(",", " ") + " so‘m" if price else "Narxni aniqlashtirish kerak"

        context.user_data["pending_product"] = name

        keyboard = [
            [InlineKeyboardButton(
                "✅ Buyurtmani yuborish",
                callback_data="confirm_order"
            )],
            [InlineKeyboardButton("⬅️ Bosh menyu", callback_data="home")],
        ]

        await query.edit_message_text(
            f"🛍️ Buyurtma:\n{name}\n💰 Narxi: {price_text}\n\n"
            "Davom etishni xohlaysizmi?",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif query.data == "confirm_order":
        product = context.user_data.get("pending_product")

        if not product:
            await query.edit_message_text(
                "Iltimos, mahsulotni qaytadan tanlang.",
                reply_markup=main_menu()
            )
            return

        user = query.from_user
        text = (
            "🆕 YANGI BUYURTMA\n\n"
            f"Mahsulot: {product}\n"
            f"Mijoz: {user.full_name}\n"
            f"Telegram ID: {user.id}\n"
            f"Username: @{user.username or 'yo‘q'}"
        )

        if ADMIN_ID:
            await context.bot.send_message(
                chat_id=ADMIN_ID,
                text=text
            )

        await query.edit_message_text(
            "✅ Buyurtmangiz qabul qilindi!\n"
            "Admin siz bilan bog‘lanadi.",
            reply_markup=main_menu()
        )

    elif query.data == "orders":
        await query.edit_message_text(
            "🛍️ Buyurtmalar tarixi hozircha mavjud emas.",
            reply_markup=main_menu()
        )

    elif query.data == "offers":
        await query.edit_message_text(
            "🎁 Maxsus takliflar tez orada!",
            reply_markup=main_menu()
        )

    elif query.data == "help":
        await query.edit_message_text(
            "📞 Yordam xizmati\n\n"
            "Admin bilan bog‘lanish uchun quyidagi tugmani bosing.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton(
                    "💬 Admin",
                    url="https://t.me/buy_premium_1bot"
                )],
                [InlineKeyboardButton(
                    "⬅️ Bosh menyu",
                    callback_data="home"
                )],
            ])
        )

    elif query.data == "home":
        await query.edit_message_text(
            "💎✨ TELEGRAM SHOP ⭐\n\nBo‘limni tanlang:",
            reply_markup=main_menu()
        )


def main():
    if not TOKEN:
        raise RuntimeError("BOT_TOKEN sozlanmagan!")

    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(buttons))
    app.run_polling()


if __name__ == "__main__":
    main()
