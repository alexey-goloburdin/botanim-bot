from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def get_categories_keyboard(
    current_category_index: int, categories_count: int, callback_prefix: str
) -> InlineKeyboardMarkup:
    prev_index = current_category_index - 1
    if prev_index < 0:
        prev_index = categories_count - 1
    next_index = current_category_index + 1
    if next_index > categories_count - 1:
        next_index = 0
    keyboard = [
        [
            InlineKeyboardButton("<", callback_data=f"{callback_prefix}{prev_index}"),
            InlineKeyboardButton(
                f"{current_category_index + 1}/{categories_count}", callback_data=" "
            ),
            InlineKeyboardButton(
                ">",
                callback_data=f"{callback_prefix}{next_index}",
            ),
        ]
    ]
    return InlineKeyboardMarkup(keyboard)
