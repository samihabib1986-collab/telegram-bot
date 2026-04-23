if data in ["taaleel", "images", "where", "level", "result1", "function", "compare"]:

    if user_id not in user_data:
        return

    unit = user_data[user_id]["unit"]
    section = user_data[user_id]["section"]

    category = f"{unit}_{section}_{data}"

    if category not in subjects["bio"]:
        await query.message.reply_text("❌ لا يوجد أسئلة لهذا القسم")
        return

    user_data[user_id]["category"] = category
