from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def get_categories_keyboard(
    current_index: int, overall_count: int, prefix: str
) -> InlineKeyboardMarkup:
    prev_index = current_index - 1
    if prev_index < 0:
        prev_index = overall_count - 1
    next_index = current_index + 1
    if next_index > overall_count - 1:
        next_index = 0
    keyboard = [
        [
            InlineKeyboardButton("<", callback_data=f"{prefix}{prev_index}"),
            InlineKeyboardButton(
                f"{current_index + 1}/{overall_count}", callback_data=" "
            ),
            InlineKeyboardButton(
                ">",
                callback_data=f"{prefix}{next_index}",
            ),
        ]
    ]
    return InlineKeyboardMarkup(keyboard)
