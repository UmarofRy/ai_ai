"""
Full Telethon userbot with:
- Admin-only commands (from your account ID)
- Per-user modes: normal | rough | polite | off
- Offensive message moderation (delete other users' offending messages)
- Pattern-based and fallback automatic replies
- /clear command with countdown
- /auto "message" * number  -> send given message number times with incremental percentage suffix (001%, 002%, ...)
- /time seconds            -> show a live progress bar (single editable message); when done: delete chat history and block the peer (if applicable)
- Logging to console
- Message editing handling

USAGE:
- Replace API_ID, API_HASH, PHONE_NUMBER with your credentials if needed.
- The admin (you) is identified by ADMIN_ID (set to 6092051746 as requested).
- Run with: python yourfile.py
"""

import asyncio
import re
import random
from telethon import TelegramClient, events, errors, functions, types
from asyncio import sleep

# -------------------------
# === CONFIGURATION ===
# -------------------------
API_ID = 29593383                    # ❗️ Replace if needed
API_HASH = '1c9eb4e8d4e24039f501f553c0cd3f22'  # ❗️ Replace if needed
PHONE_NUMBER = '+998880022685'       # ❗️ Replace if needed

# Admin identifier (your Telegram user id). Only commands from this account work.
ADMIN_ID = 7699192115  # <-- as specified by you

# -------------------------
# === MESSAGES / REPLIES ===
# -------------------------
RESPONSES = {
    # Greetings
    r"(?i)^(salom|assalomu alaykum)$": "Va alaykum assalom! 🤲",
    r"(?i).*omg.*": "Hey! 😄 Qalaysiz?",
    r"(?i).*hi.*": "Hello! 🌸",
    r"(?i).*sayonara.*": "Xayr! Yaxshi kunlar tilayman 🌞",
    r"(?i).*qalesa.*": "Good morning! ☀️",
    r"(?i).*qalesa.*": "Good night! 🌙",
    r"(?i).*konichiwa.*": "Bonjour! 🌸",

    # How are you / wellbeing
    r"(?i).*nima\?*": "Yaxshi, rahmat! Sizchi? 😊",
    r"(?i).*qancha\sbemalol\?*": "Hali ham yaxshi, rahmat! 🌿",
    r"(?i).*yaxshimisa\?*": "Ha, rahmat! Sizchi? 😇",
    r"(?i).*qalesan\?*": "Zo‘r, rahmat! Sizchi? 😄",
    r"(?i).*abdulo\?*": "Ha, hammasi joyida! 💼",
    r"(?i).*ok\?*": "Yo‘q, hammasi joyida 😊",
    r"(?i).*xafama\?*": "Ha, juda xursandman! 😄 Sizchi?",
    r"(?i).*what\?*": "Hm... ozgina, lekin yaxshilashga harakat qilayapman 😌",

    # Location / origin
    r"(?i).*qatasa\?*": "Men O‘zbekistondanman, sizchi? 🇺🇿",
    r"(?i).*qatasan\?*": "Men Toshkentdanman 🏙",
    r"(?i).*qata turasan\?*": "Hozir Toshkentda yashayapman 🌆",

    # Work / activity
    r"(?i).*nima qvosa\?*": "Hozir biroz ishlayapman, sizchi? 💼",
    r"(?i).*zerkdm\?*": "Ha, biroz ishlayapman, dam olishga ham vaqt topaman 😌",
    r"(?i).*mazzami\?*": "Ha, o‘qiyman, bilim olishni yaxshi ko‘raman 📚",
    r"(?i).*nma ish qlasa\?*": "Kitob o‘qish, musiqa tinglash fikr o'qish va kod yozish 📖🎵💻",
    r"(?i).*kino\?*": "Ha, kino yaxshi! Sizning tavsiyalaringiz bormi? 🎬",
    r"(?i).*go mk\?*": "ok san kiyinib tur xozr caqraman",

    # Names / keywords
    r"(?i)^(abdullo|abdulloh)$": "Hn",
    r"(?i).*umarov.*": "✨ Umarov hozir band, pulin bosa 200k kokida ✨💸",

    # Casual / friendly
    r"(?i).*qilasan\?*": "Hozir shu ish bilan bandman 😎",
    r"(?i).*keldinmi\?*": "Ha, endi biroz dam olaman 🍽",
    r"(?i).*charchadm\?*": "Ha, dam olaman, rahmat! 🌿",
    r"(?i).*dars\?*": "Ha, so‘nggi o‘qigan kitobim juda qiziqarli 📚",
    r"(?i).*futbol\?*": "Ha, yugurish va yoga bilan shug‘ullanaman 🏃‍♂️🧘‍♂️",
    r"(?i).*musiqa\?*": "Ha, turli janrlarni tinglayman 🎵🎧",
    r"(?i).*ok\?*": "ok bopti 🎵🎧",
    r"(?i).*Abdulo\?*": "nma? 🎵🎧",
    r"(?i).*ok\?*": "ok boldi uxla endi 🎵🧠",

    # Appreciation / thanks
    r"(?i).*sps.*": "Doimo mamnunman, xabar qilganingiz uchun ❤️",
    r"(?i).*turdinmi.*": "Sizga ham xayrli kun! 🌞",
    r"(?i).*pzds.*": "Thank you! 🙏",
    r"(?i).*uxlama.*": "Rahmat! 🎉 Sizni ham tabriklayman 🥳",

    # Fun / jokes
    r"(?i).*hazil qil.*": "Haha 😄 Haqiqatan ham qiziq! 😂",
    r"(?i).*manmi? | mami?.*": "Haha da san ukam .!. 😂",
    r"(?i).*pick.*": "Haha, pick me juda kulgili 😂📸",
    r"(?i).*jonm.*": "dnx gey bla 😂📸",
    r"(?i).*Ezoza|ezow.*": "babr bochkasande🦁💀",
    r"(?i).*Bibisora|bibisora.*": "bibisi🐸💀",
    r"(?i).*Mirjalol|mrjalol.*": "mirjii🐯💀",
    r"(?i).*sunnat|sunat.*": "allemi🕌💀",
    r"(?i).*Abdulaziz|laylo sanmi.*": "lamaaa🦙💀",
    r"(?i).*Dilshod|dlshhod.*": "dilshodjgar🎩💀",
    r"(?i).*ismoil|ismoil.*": "pidr👹💀",
    r"(?i).*hadiw|hadicha.*": "aesthetic xomudjooon💃🗿 ||5baxo shablonga||",
    r"(?i).*Abdulaziz|abdlaziz.*": "lamaaa🦙💀",
    r"(?i).*umraov|umarof.*": "mani bossim boshligim boladi umarof🎻🎯",
    r"(?i).*Mohirjon|moxir.*": "koti kotta qoy😼💀",
    r"(?i).*munisa|munis.*": "argentinali rizzayeva💃💀",
    r"(?i).*Nodira|nodra.*": "aa qodir dr dr dr matasiklku u🫀💀",
    r"(?i).*samir|Samir.*": "axaxaxa makaron kalla🍝💀",
    r"(?i).*Akbar|akbar.*": "arooo qite qite bomj vodka🍸💀",
    r"(?i).*soli|Soliha.*": "dilshodni kal rapunseli👸💀",
    r"(?i).*xy?|xy.*": "da nx qando chundin xy pilot👸💀",
    r"(?i).*Alyo?|H.*": "nma👸💀"
}

OFFENSIVE_PATTERNS = [
    r"\b(sex|porn|jinsiy|amorat|badword1|sh\*t|f\*ck)\b|dabba|dnx|wtf|skaman|skama|yba|🦒|📮|📬|🖕|hentai|qoto|tasho|yban|abl|Abl|nx|soska|pashol|wth|seks|am|bruh",
]

FALLBACKS = [
    "vay kuk",
    "ha, eshitdim",
    "qiziq, davom et",
    "gapir, tinglayman",
    "rahmat, xabar qilganing uchun",
    "hm... qanday fikrdasiz",
    "ajoyib, shunday davom eting",
    "ha, tushundim",
    "qiziq, batafsilroq aytib bera olasizmi",
    "hmm… menimcha bu juda muhim",
    "rahmat, eshitib quvonib ketdim",
    "ha, shuni oldindan bilganim yaxshi bo‘lar edi",
    "haqiqatdan ham? qanday qilib",
    "to‘g‘ri, bu fikr juda qiziq",
    "menimcha, davom etishimiz kerak",
    "wow, shuni eshitib hayron bo‘ldim",
    "ajoyib fikr, boshqalar bilan ham bo‘lishsak bo‘ladi",
    "ha, tushundim, rahmat tushuntirgani uchun",
    "tilin chiqib qopdimi",
    "haha, bu juda kulgili"
    "mani oldimda sokish sangamas"
    "nma gap bratishka"
    "gapni qisqart bratishka"
    "ismin nma?"
]

ROUGH_REPLIES = [
    "Nima gap? Keraksiz gaplarni yozma! 😒",
    "Bezota qma mani endi, gapingni qisqart! 🤨",
    "Ha, tushundim. Endi xotirjam bo‘lgin! 😤",
    "Nma, mazgi qildin? 😑",
    "Zb nma kere 🗿",
    "Pashol ket Yoqol✅🤷‍♂️",
    "Yana nechi marta etaman, bezota qma! 😠",
    "Gapni qisqart, vaqtim qimmat! ⏳",
    "Mana endi tinch bo‘lgin! 😤",
    "Dnx ket endi! 🦒",
    "gapni chunasanmi o'zi, yoki yana takrorlaymi?😑",
    "krc mazgi dnx okey",
    "Agar yana shunaqa yozsang, bloklanishing mumkin. 😑"
    "man gapni qaytarishga majbur qma☠️🦒"
]

POLITE_REPLIES = [
    "Rahmat, hurmat bilan yozing 😊",
    "Men tinglayapman 🌸",
    "Muloyimroq gapiring 🙏",
    "Rahmat, davom eting 🌼",
    "Yoqimli suhbat 🤍",
    "Samimiy yozing 🌿",
    "Gaplaringizni qadrlayman ✨",
    "Muloqot chiroyli 🌸",
    "Rahmat, tushundim 🕊️",
    "Do‘stona davom etamiz 🍀",
    "Hurmatli so‘zlar 🌟",
    "Mehribon ohangda 🌷",
    "Sizni tinglash yaxshi 🤍",
    "Qadrli so‘zlar ✨",
    "Rahmat xabaringiz uchun 🙏",
    "Yaxshi kayfiyat 🌸",
    "Samimiyatni qadrlayman 🌼",
    "Ajoyib suhbat 🌺",
    "Har bir so‘z qimmatli 💫",
    "Rahmat, davom eting 🌟"
]

# -------------------------
# === STATE ===
# -------------------------
# ACTIVE_MODES: user_id -> "normal" | "rough" | "polite" | "off"
ACTIVE_MODES = {}  # in-memory; not persisted. default = "off"

# -------------------------
# === UTILITIES ===
# -------------------------
def format_reply(text: str) -> str:
    decorations = [
        # Soft / Aesthetic
        "💬", "🌿", "🫧", "🕊", "🫶", "🫀", "😇",
        "✨", "🌸", "🌈", "🍓", "🌷", "🌹", "🌺",
        "🌼", "🌻", "🌊", "🍃", "🪷", "💐", "🍄",
        # Sigma / Aurali / Moai
        "🗿", "💀", "🧠", "💎", "⭐️", "🌙", "☀️",
        "🕯", "🎶", "🧿", "🔥", "✅", "😌", "🤍",
        # Saturn / Space vibes
        "🪐", "🌟", "🌌", "🚀", "🌠", "🌑", "🌙",
        # Rabbit / Cute
        "🐇", "🐰", "🥕", "🧸", "🎈", "🎉", "🥰",
    ]
    return f"{random.choice(decorations)} {text} {random.choice(decorations)}"

def is_offensive(text: str) -> bool:
    txt = (text or "").lower()
    for pattern in OFFENSIVE_PATTERNS:
        if re.search(pattern, txt):
            return True
    return False

async def human_delay(min_s=0.5, max_s=3.0):
    await asyncio.sleep(random.uniform(min_s, max_s))

# -------------------------
# === TELETHON CLIENT ===
# -------------------------
client = TelegramClient('autoreply_session', API_ID, API_HASH)

# Admin command regex: /start|/stop|/rough|/polite umarov ai @username
ADMIN_CMD_RE = re.compile(r"^/(start|stop|rough|polite)\s+(@?[A-Za-z0-9_]+)$", re.I)
CLEAR_CMD_RE = re.compile(r"^/clear\s*$", re.I)

# New admin-only command regexes:
# /auto "message" * number
AUTO_CMD_RE = re.compile(r'^/auto\s+(?:"([^"]+)"|\'([^\']+)\')\s*\*\s*(\d+)\s*$', re.I | re.DOTALL)
# /time seconds
TIME_CMD_RE = re.compile(r'^/time\s+(\d+)\s*$', re.I)

# -------------------------
# === ADMIN COMMAND HANDLER ===
# -------------------------
@client.on(events.NewMessage(outgoing=True))
async def admin_commands(event):
    """
    Handle admin commands sent by the admin (you). Commands only accepted if the sender's id == ADMIN_ID.
    Works when you send them in Saved Messages or any private chat (outgoing messages).

    This handler includes the new /auto and /time admin commands.
    """
    try:
        # ensure this message is from the admin account
        sender = await event.get_sender()
        sender_id = getattr(sender, "id", None)
        if sender_id != ADMIN_ID:
            return  # ignore outgoing from others (shouldn't happen)
    except Exception:
        # If unable to get sender, be conservative and ignore
        return

    text = event.raw_text or ""
    text_stripped = text.strip()

    # /clear command (no args)
    if CLEAR_CMD_RE.match(text_stripped):
        # Only admin can trigger
        print(f"[ADMIN] /clear triggered by admin (chat_id={event.chat_id})")
        # send countdown 5..0 in the same chat
        try:
            for i in range(5, -1, -1):
                await event.reply(str(i))
                await asyncio.sleep(0.8)  # short pause between numbers to be visible
        except Exception as e:
            print(f"[ERROR] Failed during countdown: {e}")

        # Now delete entire chat history (current chat)
        # We'll iterate messages in this chat and delete them in batches
        chat = event.chat_id  # this can be your own id for Saved Messages or the other person's id
        print(f"[ADMIN] Attempting to delete all messages in chat {chat} ...")
        try:
            # Collect message ids in batches to delete (we'll delete in chunks of 100)
            ids_batch = []
            batch_size = 100
            async for msg in client.iter_messages(chat, limit=None):
                ids_batch.append(msg.id)
                if len(ids_batch) >= batch_size:
                    try:
                        await client.delete_messages(chat, ids_batch, revoke=True)
                        print(f"[ADMIN] Deleted batch of {len(ids_batch)} messages in chat {chat}")
                    except Exception as de:
                        print(f"[WARN] Could not delete batch: {de}")
                    ids_batch = []
            # delete remaining ids
            if ids_batch:
                try:
                    await client.delete_messages(chat, ids_batch, revoke=True)
                    print(f"[ADMIN] Deleted final batch of {len(ids_batch)} messages in chat {chat}")
                except Exception as de:
                    print(f"[WARN] Could not delete final batch: {de}")

            # Optionally remove dialog from list to clean up (delete_dialog)
            try:
                await client.delete_dialog(chat)
                print(f"[ADMIN] Deleted dialog for chat {chat}")
            except Exception as de:
                # Not critical; some chats (Saved Messages) might not allow delete_dialog
                print(f"[WARN] delete_dialog failed: {de}")

            # done
            await asyncio.sleep(0.3)
            await event.reply(format_reply("O‘z-o‘zini yo‘q qilish tugallandi."))
            print(f"[ADMIN] /clear completed for chat {chat}")
        except Exception as e:
            print(f"[ERROR] Error while clearing chat {chat}: {e}")
            try:
                await event.reply(format_reply(f"⚠️ Xato yuz berdi: {e}"))
            except Exception:
                pass

        return

    # New: /auto command
    m_auto = AUTO_CMD_RE.match(text_stripped)
    if m_auto:
        # Parse quoted message and number
        msg_text = m_auto.group(1) or m_auto.group(2) or ""
        count = int(m_auto.group(3) or 0)
        # Safety cap to avoid accidental huge spam (adjustable)
        MAX_COUNT = 1000000000000000000000000000000000000000000000000000000000000000000000000000000
        if count <= 0:
            await event.reply(format_reply("⚠️ Iltimos, nusxalash sonini musbat butun son sifatida kiriting."))
            return
        if count > MAX_COUNT:
            await event.reply(format_reply(f"⚠️ So'rov juda katta (>{MAX_COUNT}). Iltimos, kichikroq son kiriting."))
            print(f"[ADMIN] /auto refused: requested {count} > {MAX_COUNT}")
            return

        chat = event.chat_id
        print(f"[ADMIN] /auto triggered by admin in chat {chat}: sending {count} copies of message: {repr(msg_text)}")
        try:
            for i in range(1, count + 1):
                suffix = f"{i:03d}%"
                send_text = f"{msg_text} {suffix}"
                # slight human delay per message
                await human_delay(0.2, 1.0)
                await client.send_message(chat, send_text)
                print(f"[ADMIN][AUTO] Sent ({i}/{count}) -> {send_text}")
            await event.reply(format_reply(f"Sucsesfull✅ Boshliq @umarov_py"))
            print(f"[ADMIN] /auto completed in chat {chat}")
        except Exception as e:
            print(f"[ERROR] /auto failed in chat {chat}: {e}")
            try:
                await event.reply(format_reply(f"⚠️ /auto bajarishda xato: {e}"))
            except Exception:   
                pass
        return

    # New: /time command
    m_time = TIME_CMD_RE.match(text_stripped)
    if m_time:
        seconds = int(m_time.group(1))
        if seconds <= 0:
            await event.reply(format_reply("⚠️ Iltimos, musbat son kiriting."))
            return

        chat = event.chat_id
        me = await client.get_me()
        print(f"[ADMIN] /time triggered by admin in chat {chat}: timer={seconds}s")

        # Prepare progress message
        try:
            progress_msg = await event.reply(format_reply(f"⏳ Boshlanmoqda... 0%"))
            bar_length = 20  # length of visual bar
            interval = 1.0  # update every 1 second
            steps = max(1, int(seconds / interval))
            # We'll update per-second to keep it simple and human-like
            for elapsed in range(1, seconds + 1):
                pct = int((elapsed / seconds) * 100)
                filled = int((pct / 100) * bar_length)
                bar = "█" * filled + "—" * (bar_length - filled)
                new_text = format_reply(f"⏳ {pct}% |{bar}| {elapsed}/{seconds}s")
                # human-like pause before edit
                await asyncio.sleep(0.8 + random.uniform(0.0, 0.4))
                try:
                    await progress_msg.edit(new_text)
                except Exception as ee:
                    # as fallback, try editing by id
                    try:
                        await client.edit_message(chat, progress_msg.id, new_text)
                    except Exception as eee:
                        print(f"[WARN] Could not edit progress message: {eee} / {eee}")
                print(f"[ADMIN][TIMER] {pct}% ({elapsed}/{seconds}s) in chat {chat}")

            # Finalize at 100%
            final_text = format_reply("✅ 100% - vaqti tugadi. Sayonara")
            try:
                await progress_msg.edit(final_text)
            except Exception:
                try:
                    await client.edit_message(chat, progress_msg.id, final_text)
                except Exception:
                    pass
            await asyncio.sleep(0.8)

            # Now delete all messages in this chat (same logic as /clear)
            print(f"[ADMIN] /time completed: attempting to delete all messages in chat {chat} ...")
            try:
                ids_batch = []
                batch_size = 100
                async for msg in client.iter_messages(chat, limit=None):
                    ids_batch.append(msg.id)
                    if len(ids_batch) >= batch_size:
                        try:
                            await client.delete_messages(chat, ids_batch, revoke=True)
                            print(f"[ADMIN] Deleted batch of {len(ids_batch)} messages in chat {chat}")
                        except Exception as de:
                            print(f"[WARN] Could not delete batch: {de}")
                        ids_batch = []
                if ids_batch:
                    try:
                        await client.delete_messages(chat, ids_batch, revoke=True)
                        print(f"[ADMIN] Deleted final batch of {len(ids_batch)} messages in chat {chat}")
                    except Exception as de:
                        print(f"[WARN] Could not delete final batch: {de}")
                # Attempt to delete dialog too
                try:
                    await client.delete_dialog(chat)
                    print(f"[ADMIN] Deleted dialog for chat {chat}")
                except Exception as de:
                    print(f"[WARN] delete_dialog failed (non-critical): {de}")

            except Exception as e:
                print(f"[ERROR] Error while clearing chat {chat} after /time: {e}")

            # Attempt to block the peer if it's a user and not Saved Messages (you)
            try:
                entity = await client.get_entity(chat)
                if isinstance(entity, types.User) and getattr(entity, 'id', None) != me.id:
                    # Block the user
                    await client(functions.contacts.BlockRequest(id=entity.id))
                    print(f"[ADMIN] Blocked user id={entity.id} (@{getattr(entity, 'username', None)}) after /time")
                else:
                    print(f"[ADMIN] Not blocking: entity is not a user or is self (chat={chat})")
            except Exception as e:
                print(f"[WARN] Could not block entity for chat {chat}: {e}")

            # Final log + no further reply (chat cleared)
            print(f"[ADMIN] /time sequence finished for chat {chat}")
        except Exception as e:
            print(f"[ERROR] /time failed in chat {chat}: {e}")
            try:
                await event.reply(format_reply(f"⚠️ /time buyruqda xato yuz berdi: {e}"))
            except Exception:
                pass
        return

    # Admin mode commands (/start, /stop, /rough, /polite)
    m = ADMIN_CMD_RE.match(text_stripped)
    if not m:
        return  # not an admin-mode command we recognize

    cmd = m.group(1).lower()
    username = m.group(2)  # may include @

    # normalize username (remove @)
    if username.startswith("@"):
        username = username[1:]

    # Resolve username to user entity
    try:
        target = await client.get_entity(username)
    except errors.UsernameInvalidError as e:
        await event.reply(format_reply(f"⚠️ Username @{username} noto'g'ri yoki topilmadi."))
        print(f"[ADMIN] {cmd} failed - cannot resolve @{username}: {e}")
        return
    except Exception as e:
        await event.reply(format_reply(f"⚠️ Foydalanuvchi aniqlashda xato: {e}"))
        print(f"[ADMIN] {cmd} failed - error resolving @{username}: {e}")
        return

    # Ensure it's a user (has id)
    try:
        target_id = target.id
    except Exception as e:
        await event.reply(format_reply("⚠️ Maqsadli foydalanuvchi haqida ma'lumot olinmadi."))
        print(f"[ADMIN] {cmd} failed - entity has no id (@{username}): {e}")
        return

    # Map the command to a mode
    if cmd == "start":
        mode = "normal"
    elif cmd == "stop":
        mode = "Turn Off"
    elif cmd == "rough":
        mode = "Mazgi qildin"
    elif cmd == "polite":
        mode = "friendly"
    else:
        await event.reply(format_reply("⚠️ Noma'lum buyruq."))
        return

    # Set the mode
    ACTIVE_MODES[target_id] = mode
    await asyncio.sleep(0.25)
    await event.reply(format_reply(f"Rejim: @{getattr(target, 'username', str(target_id))} uchun ** __ ✅ {mode} ✅ __ ** ga o'zgartirildi."))
    print(f"[ADMIN] Set mode for user_id={target_id} (@{getattr(target, 'username', None)}) -> {mode}")

# -------------------------
# === INCOMING MESSAGES HANDLER ===
# -------------------------
@client.on(events.NewMessage(incoming=True))
async def incoming_handler(event):
    """
    Handle incoming messages from other users (private 1:1 chats only).
    - Offensive detection & deletion (for messages from others only)
    - Per-user modes applied: normal / rough / polite / off
    """
    # Only private 1:1 chats
    if not event.is_private:
        return

    sender = await event.get_sender()
    if not sender:
        return

    sender_id = getattr(sender, "id", None)
    # ignore messages from bots
    if getattr(sender, "bot", False):
        return

    text = event.raw_text or ""
    # Offensive moderation: if message is offensive and sender is NOT the admin -> delete
    if sender_id != ADMIN_ID and is_offensive(text):
        try:
            # Delete other user's offending message (revoke=True to remove for both sides)
            await client.delete_messages(event.chat_id, [event.id], revoke=True)
            print(f"[🛡 Deleted offensive message] from user_id={sender_id} chat={event.chat_id} msg_id={event.id}")
        except Exception as e:
            print(f"[WARN] Could not delete offensive message from {sender_id}: {e}")
        # IMPORTANT: Do NOT send any warning messages when deleting other people's messages (per your request)
        return

    # If admin sent message to this private chat (rare incoming), skip handling
    if sender_id == ADMIN_ID:
        return

    # Determine active mode for this user (default "off")
    mode = ACTIVE_MODES.get(sender_id, "off")
    print(f"[📥 Incoming] from {getattr(sender,'first_name',None)} (id={sender_id}) mode={mode} text={repr(text)})")

    if mode == "off":
        # stay silent
        return

    # add human-like delay
    await human_delay(0.5, 3.0)

    try:
        if mode == "rough":
            reply_txt = random.choice(ROUGH_REPLIES)
            formatted = format_reply(reply_txt)
            await event.reply(formatted)
            print(f"[📩 Replied (rough)] to user_id={sender_id}: {formatted}")
            return

        if mode == "polite":
            reply_txt = random.choice(POLITE_REPLIES)
            formatted = format_reply(reply_txt)
            await event.reply(formatted)
            print(f"[📩 Replied (polite)] to user_id={sender_id}: {formatted}")
            return

        # mode == "normal": try pattern matching first
        for pattern, reply in RESPONSES.items():
            if re.search(pattern, text):
                formatted = format_reply(reply)
                await event.reply(formatted)
                print(f"[📩 Replied (normal-match)] to user_id={sender_id}: {formatted}")
                return

        # No matched pattern: fallback (70% chance)
        if random.random() < 0.7:
            fallback = random.choice(FALLBACKS)
            formatted = format_reply(fallback)
            await event.reply(formatted)
            print(f"[📩 Replied (normal-fallback)] to user_id={sender_id}: {formatted}")
        else:
            print(f"[🤫 No reply sent to user_id={sender_id} (normal fallback skipped)]")
    except Exception as e:
        print(f"[ERROR] Failed to send reply to user_id={sender_id}: {e}")

# -------------------------
# === EDITED MESSAGE HANDLER ===
# -------------------------
@client.on(events.MessageEdited(incoming=True))
async def edited_handler(event):
    """
    If an edited message becomes offensive (and is from someone other than admin), delete it.
    Do NOT send warnings in this case (per requirements).
    Edited messages do NOT trigger reply logic.
    """
    if not event.is_private:
        return

    sender = await event.get_sender()
    if not sender:
        return

    sender_id = getattr(sender, "id", None)
    # ignore bots
    if getattr(sender, "bot", False):
        return

    new_text = event.text or ""

    # If edited message is offensive and not from admin -> delete
    if sender_id != ADMIN_ID and is_offensive(new_text):
        try:
            await client.delete_messages(event.chat_id, [event.id], revoke=True)
            print(f"[🛡 Deleted offensive edited message] from user_id={sender_id} chat={event.chat_id} msg_id={event.id}")
        except Exception as e:
            print(f"[WARN] Could not delete offensive edited message from {sender_id}: {e}")
        # Do NOT send warnings
        return

    # If not offensive, do nothing for edits (no automatic replies)
    print(f"[✏️ Edited message] from user_id={sender_id} - not offensive; no reply.")

# -------------------------
# === ADDED MODULE-LIKE COMMANDS FOR ADMIN (MagicText, Magic hearts, Ovoz memlar) ===
# -------------------------

# --- MagicText letters dict (full) ---
# NOTE: This is a large mapping used by .mt command. It's taken from the module you provided.
letters = {
    " ": "000000000000\n000000000000\n000000000000\n000000000000\n000000000000\n000000000000\n000000000000\n000000000000\n000000000000\n000000000000\n000000000000\n000000000000",
    "a": "000000000000\n000001100000\n000011110000\n000111111000\n001110011100\n001100001100\n001100001100\n001111111100\n001111111100\n001100001100\n001100001100\n000000000000",
    "b": "000000000000\n001111111000\n001111111100\n001100001100\n001100001100\n001111111000\n001111111000\n001100001100\n001100001100\n001111111100\n001111111000\n000000000000",
    "c": "000000000000\n000111111000\n001111111100\n001100001100\n001100000000\n001100000000\n001100000000\n001100000000\n001100001100\n001111111100\n000111111000\n000000000000",
    "d": "000000000000\n001111111000\n001111111100\n000110001100\n000110001100\n000110001100\n000110001100\n000110001100\n000110001100\n001111111100\n001111111000\n000000000000",
    "e": "000000000000\n001111111000\n001111111000\n001100000000\n001100000000\n001111110000\n001111110000\n001100000000\n001100000000\n001111111000\n001111111000\n000000000000",
    "f": "000000000000\n000111111000\n001111111000\n001100000000\n001100000000\n001111110000\n001111110000\n001100000000\n001100000000\n001100000000\n001100000000\n000000000000",
    "g": "000000000000\n000111111000\n001111111100\n001100000000\n001100000000\n001100111100\n001100111100\n001100001100\n001100001100\n001111111100\n000111111000\n000000000000",
    "h": "000000000000\n001100001100\n001100001100\n001100001100\n001100001100\n001111111100\n001111111100\n001100001100\n001100001100\n001100001100\n001100001100\n000000000000",
    "i": "000000000000\n001111111100\n001111111100\n000001100000\n000001100000\n000001100000\n000001100000\n000001100000\n000001100000\n001111111100\n001111111100\n000000000000",
    "j": "000000000000\n000111111100\n000111111100\n000000011000\n000000011000\n000000011000\n000000011000\n001100011000\n001100011000\n001111111000\n000111110000\n000000000000",
    "k": "000000000000\n001100001100\n001100011100\n001100111000\n001101110000\n001111100000\n001111100000\n001101110000\n001100111000\n001100011100\n001100001100\n000000000000",
    "l": "000000000000\n001100000000\n001100000000\n001100000000\n001100000000\n001100000000\n001100000000\n001100000000\n001100000000\n001111111100\n001111111100\n000000000000",
    "m": "000000000000\n001100001100\n001110011100\n001111111100\n001111111100\n001101101100\n001100001100\n001100001100\n001100001100\n001100001100\n001100001100\n000000000000",
    "n": "000000000000\n001100001100\n001110001100\n001111001100\n001111101100\n001101111100\n001100111100\n001100011100\n001100001100\n001100001100\n001100001100\n000000000000",
    "o": "000000000000\n000111111000\n001111111100\n001100001100\n001100001100\n001100001100\n001100001100\n001100001100\n001100001100\n001111111100\n000111111000\n000000000000",
    "p": "000000000000\n001111111000\n001111111100\n001100001100\n001100001100\n001111111100\n001111111000\n001100000000\n001100000000\n001100000000\n001100000000\n000000000000",
    "q": "000000000000\n000111111000\n001111111100\n001100001100\n001100001100\n001100001100\n001101101100\n001101111100\n001100111000\n001111111100\n000111101100\n000000000000",
    "r": "000000000000\n001111111000\n001111111100\n001100001100\n001100001100\n001111111100\n001111111000\n001100011100\n001100001100\n001100001100\n001100001100\n000000000000",
    "s": "000000000000\n000111111000\n001111111100\n001100001100\n001100000000\n001111111000\n000111111100\n000000001100\n001100001100\n001111111100\n000111111000\n000000000000",
    "t": "000000000000\n001111111100\n001111111100\n000001100000\n000001100000\n000001100000\n000001100000\n000001100000\n000001100000\n000001100000\n000001100000\n000000000000",
    "u": "000000000000\n001100001100\n001100001100\n001100001100\n001100001100\n001100001100\n001100001100\n001100001100\n001100001100\n001111111100\n000111111000\n000000000000",
    "v": "000000000000\n001100001100\n001100001100\n001100001100\n001100001100\n001100001100\n001100001100\n001110011100\n000111111000\n000011110000\n000001100000\n000000000000",
    "w": "000000000000\n001100001100\n001100001100\n001100001100\n001100001100\n001100001100\n001101101100\n001111111100\n001111111100\n001110011100\n001100001100\n000000000000",
    "x": "000000000000\n001100001100\n001100001100\n001110011100\n000111011000\n000011110000\n000011110000\n000110111000\n001110011100\n001100001100\n001100001100\n000000000000",
    "y": "000000000000\n001100001100\n001100001100\n001100001100\n001100001100\n001111111100\n000111111100\n000000001100\n000000001100\n001111111100\n001111111000\n000000000000",
    "z": "000000000000\n001111111100\n001111111100\n000000011100\n000000111000\n000001110000\n000011100000\n000111000000\n001110000000\n001111111100\n001111111100\n000000000000",
    "а": "000000000000\n000001100000\n000011110000\n000111111000\n001110011100\n001100001100\n001100001100\n001111111100\n001111111100\n001100001100\n001100001100\n000000000000",
    "б": "000000000000\n001111111000\n001111111000\n001100000000\n001100000000\n001111111000\n001111111100\n001100001100\n001100001100\n001111111100\n001111111000\n000000000000",
    "в": "000000000000\n001111111000\n001111111100\n001100001100\n001100001100\n001111111000\n001111111000\n001100001100\n001100001100\n001111111100\n001111111000\n000000000000",
    "г": "000000000000\n000011111100\n000111111100\n000110000000\n000110000000\n000110000000\n000110000000\n000110000000\n000110000000\n000110000000\n000110000000\n000000000000",
    "д": "000000000000\n000001111000\n000011111100\n000111001100\n001110001100\n001100001100\n001111111100\n011111111110\n011100001110\n011000000110\n011000000110\n000000000000",
    "е": "000000000000\n001111111000\n001111111000\n001100000000\n001100000000\n001111110000\n001111110000\n001100000000\n001100000000\n001111111000\n001111111000\n000000000000",
    "ё": "000000000000\n001111111000\n001111111000\n001100000000\n001100000000\n001111110000\n001111110000\n001100000000\n001100000000\n001111111000\n001111111000\n000000000000",
    "ж": "000000000000\n001101101100\n001101101100\n001111111100\n000111111000\n000011110000\n000011110000\n000111111000\n001111111100\n001101101100\n001101101100\n000000000000",
    "з": "000000000000\n000111111000\n001111111100\n001100001100\n000000001100\n000001111000\n000001111000\n000000001100\n001100001100\n001111111100\n000111111000\n000000000000",
    "и": "000000000000\n001100001100\n001100001100\n001100011100\n001100111100\n001101111100\n001111101100\n001111001100\n001110001100\n001100001100\n001100001100\n000000000000",
    "й": "000000000000\n001101101100\n001100001100\n001100011100\n001100111100\n001101111100\n001111101100\n001111001100\n001110001100\n001100001100\n001100001100\n000000000000",
    "к": "000000000000\n001100001100\n001100011100\n001100111000\n001101110000\n001111100000\n001111100000\n001101110000\n001100111000\n001100011100\n001100001100\n000000000000",
    "л": "000000000000\n000001100000\n000011110000\n000111111000\n001110011100\n001100001100\n001100001100\n001100001100\n001100001100\n001100001100\n001100001100\n000000000000",
    "м": "000000000000\n001100001100\n001110011100\n001111111100\n001111111100\n001101101100\n001100001100\n001100001100\n001100001100\n001100001100\n001100001100\n000000000000",
    "н": "000000000000\n001100001100\n001100001100\n001100001100\n001100001100\n001111111100\n001111111100\n001100001100\n001100001100\n001100001100\n001100001100\n000000000000",
    "о": "000000000000\n000111111000\n001111111100\n001100001100\n001100001100\n001100001100\n001100001100\n001100001100\n001100001100\n001111111100\n000111111000\n000000000000",
    "п": "000000000000\n001111111100\n001111111100\n001100001100\n001100001100\n001100001100\n001100001100\n001100001100\n001100001100\n001100001100\n001100001100\n000000000000",
    "р": "000000000000\n001111111000\n001111111100\n001100001100\n001100001100\n001111111100\n001111111000\n001100000000\n001100000000\n001100000000\n001100000000\n000000000000",
    "с": "000000000000\n000111111000\n001111111100\n001100001100\n001100000000\n001100000000\n001100000000\n001100000000\n001100001100\n001111111100\n000111111000\n000000000000",
    "т": "000000000000\n001111111100\n001111111100\n000001100000\n000001100000\n000001100000\n000001100000\n000001100000\n000001100000\n000001100000\n000001100000\n000000000000",
    "у": "000000000000\n001100001100\n001100001100\n001100001100\n001100001100\n001111111100\n000111111100\n000000001100\n000000001100\n001111111100\n001111111000\n000000000000",
    "ф": "000000000000\n000111111000\n001111111100\n011001100110\n011001100110\n011001100110\n001111111100\n000111111000\n000001100000\n000001100000\n000001100000\n000000000000",
    "х": "000000000000\n001100001100\n001100001100\n001110011100\n000111011000\n000011110000\n000011110000\n000110111000\n001110011100\n001100001100\n001100001100\n000000000000",
    "ц": "000000000000\n001100001100\n001100001100\n001100001100\n001100001100\n001100001100\n001100001100\n001100001100\n001111111110\n000111111110\n000000000110\n000000000000",
    "ч": "000000000000\n001100001100\n001100001100\n001100001100\n001100001100\n001100001100\n001111111100\n000111111100\n000000001100\n000000001100\n000000001100\n000000000000",
    "ш": "000000000000\n001100001100\n001100001100\n001100001100\n001101101100\n001101101100\n001101101100\n001101101100\n001101101100\n001111111100\n001111111100\n000000000000",
    "щ": "000000000000\n001100001100\n001100001100\n001100001100\n001101101100\n001101101100\n001101101100\n001101101100\n001111111110\n001111111110\n000000000110\n000000000000",
    "ь": "000000000000\n001100000000\n001100000000\n001100000000\n001100000000\n001111111000\n001111111100\n001100001100\n001100001100\n001111111100\n001111111000\n000000000000",
    "ъ": "000000000000\n011100000000\n011100000000\n001100000000\n001100000000\n001111111000\n001111111100\n001100001100\n001100001100\n001111111100\n001111111000\n000000000000",
    "ы": "000000000000\n001100001100\n001100001100\n001100001100\n001100001100\n001111101100\n001111111100\n001100011100\n001100011100\n001111111100\n001111101100\n000000000000",
    "э": "000000000000\n000111111000\n001111111100\n001100001100\n000000001100\n000011111100\n000011111100\n000000001100\n001100001100\n001111111100\n000111111000\n000000000000",
    "ю": "000000000000\n011001111100\n011011111110\n011011000110\n011011000110\n011111000110\n011111000110\n011011000110\n011011000110\n011011111110\n011001111100\n000000000000",
    "я": "000000000000\n000111111100\n001111111100\n001100001100\n001100001100\n001111111100\n000111111100\n000000111100\n000001111100\n000011101100\n000111001100\n000000000000",
    ".": "000000000000\n000000000000\n000000000000\n000000000000\n000000000000\n000000000000\n000000000000\n000000000000\n000000000000\n000001100000\n000001100000\n000000000000",
    "!": "000000000000\n000001100000\n000001100000\n000001100000\n000001100000\n000001100000\n000001100000\n000000000000\n000000000000\n000001100000\n000001100000\n000000000000",
    "💖": "000000000000\n001110011100\n011🤍11111110\n01🤍111111110\n011111111110\n011111111110\n011111111110\n001111111100\n000111111000\n000011110000\n000001100000\n000000000000",
}

# Default symbols for MagicText
MAGIC_SYMBOLS = ["✨", "💖"]

# --- Magic / love animations helpers ---
async def do_magic_original(message):
    """Adapted from love.py — .magic command"""
    try:
        arr = ["❤️", "🧡", "💛", "💚", "💙", "💜", "🤎", "🖤", "💖"]
        h = "🤍"
        first = ""
        pattern_lines = "".join([h*9, "\n", h*2, arr[0]*2, h, arr[0]*2, h*2, "\n",
                                 h, arr[0]*7, h, "\n", h, arr[0]*7, h, "\n",
                                 h, arr[0]*7, h, "\n", h*2, arr[0]*5, h*2, "\n",
                                 h*3, arr[0]*3, h*3, "\n", h*4, arr[0], h*4]).split("\n")
        for i in pattern_lines:
            first += i + "\n"
            try:
                await message.edit(first)
            except Exception:
                pass
            await sleep(0.2)
        for i in arr:
            txt = "".join([h*9, "\n", h*2, i*2, h, i*2, h*2, "\n", h, i*7, h, "\n", h, i*7, h, "\n",
                           h, i*7, h, "\n", h*2, i*5, h*2, "\n", h*3, i*3, h*3, "\n", h*4, i, h*4, "\n", h*9])
            try:
                await message.edit(txt)
            except Exception:
                pass
            await sleep(0.3)
        for _ in range(8):
            rand = random.choices(arr, k=34)
            txt = "".join([h*9, "\n", h*2, rand[0], rand[1], h, rand[2], rand[3], h*2, "\n",
                           h, rand[4], rand[5], rand[6], rand[7], rand[8], rand[9], rand[10], h, "\n",
                           h, rand[11], rand[12], rand[13], rand[14], rand[15], rand[16], rand[17], h, "\n",
                           h, rand[18], rand[19], rand[20], rand[21], rand[22], rand[23], rand[24], h, "\n",
                           h*2, rand[25], rand[26], rand[27], rand[28], rand[29], h*2, "\n",
                           h*3, rand[30], rand[31], rand[32], h*3, "\n", h*4, rand[33], h*4, "\n", h*9])
            try:
                await message.edit(txt)
            except Exception:
                pass
            await sleep(0.3)
        fourth = "".join([h*9, "\n", h*2, arr[0]*2, h, arr[0]*2, h*2, "\n", h, arr[0]*7, h, "\n", h, arr[0]*7, h, "\n",
                          h, arr[0]*7, h, "\n", h*2, arr[0]*5, h*2, "\n", h*3, arr[0]*3, h*3, "\n", h*4, arr[0], h*4, "\n", h*9])
        try:
            await message.edit(fourth)
        except Exception:
            pass
        for _ in range(47):
            fourth = fourth.replace("🤍", "❤️", 1)
            try:
                await message.edit(fourth)
            except Exception:
                pass
            await sleep(0.1)
        for i in range(8):
            try:
                await message.edit((arr[0]*(8-i)+"\n")*(8-i))
            except Exception:
                pass
            await sleep(0.4)
        for i in ["MEN", "MEN ❤️", "MEN SIZNI ❤️", "MEN SIZNI ❤️ BOG'B OLDRAMAN🔥🖤!"]:
            try:
                await message.edit(f"**{i}**")
            except Exception:
                pass
            await sleep(0.5)
    except Exception as e:
        print(f"[WARN] do_magic_original error: {e}")

async def do_magic_emodji(message):
    """Adapted from AmMod — .magic2 command"""
    try:
        arr = ["🥰", "😚", "☺️", "😘", "🤭", "😍", "😙", "🙃", "🤗"]
        h = "◽"
        first = ""
        pattern_lines = "".join([h*9, "\n", h*2, arr[0]*2, h, arr[0]*2, h*2, "\n",
                                 h, arr[0]*7, h, "\n", h, arr[0]*7, h, "\n",
                                 h, arr[0]*7, h, "\n", h*2, arr[0]*5, h*2, "\n",
                                 h*3, arr[0]*3, h*3, "\n", h*4, arr[0], h*4]).split("\n")
        for i in pattern_lines:
            first += i + "\n"
            try:
                await message.edit(first)
            except Exception:
                pass
            await sleep(0.2)
        for i in arr:
            txt = "".join([h*9, "\n", h*2, i*2, h, i*2, h*2, "\n", h, i*7, h, "\n", h, i*7, h, "\n",
                           h, i*7, h, "\n", h*2, i*5, h*2, "\n", h*3, i*3, h*3, "\n", h*4, i, h*4, "\n", h*9])
            try:
                await message.edit(txt)
            except Exception:
                pass
            await sleep(0.3)
        for _ in range(8):
            rand = random.choices(arr, k=34)
            txt = "".join([h*9, "\n", h*2, rand[0], rand[1], h, rand[2], rand[3], h*2, "\n",
                           h, rand[4], rand[5], rand[6], rand[7], rand[8], rand[9], rand[10], h, "\n",
                           h, rand[11], rand[12], rand[13], rand[14], rand[15], rand[16], rand[17], h, "\n",
                           h, rand[18], rand[19], rand[20], rand[21], rand[22], rand[23], rand[24], h, "\n",
                           h*2, rand[25], rand[26], rand[27], rand[28], rand[29], h*2, "\n",
                           h*3, rand[30], rand[31], rand[32], h*3, "\n", h*4, rand[33], h*4, "\n", h*9])
            try:
                await message.edit(txt)
            except Exception:
                pass
            await sleep(0.3)
        fourth = "".join([h*9, "\n", h*2, arr[0]*2, h, arr[0]*2, h*2, "\n", h, arr[0]*7, h, "\n",
                          h, arr[0]*7, h, "\n", h, arr[0]*7, h, "\n", h*2, arr[0]*5, h*2, "\n",
                          h*3, arr[0]*3, h*3, "\n", h*4, arr[0], h*4, "\n", h*9])
        try:
            await message.edit(fourth)
        except Exception:
            pass
        for _ in range(47):
            fourth = fourth.replace(arr[0], "🥰", 1)  # gradually replace first placeholder with actual
            try:
                await message.edit(fourth)
            except Exception:
                pass
            await sleep(0.1)
        for i in range(8):
            try:
                await message.edit((arr[0]*(8-i)+"\n")*(8-i))
            except Exception:
                pass
            await sleep(0.4)
        for i in ["MEN", "MEN ❤️", "MEN SIZNI ❤️", "MEN SIZNI ❤️ ABJAGIZNI CHIQARAMAN🪨😅!"]:
            try:
                await message.edit(f"**{i}**")
            except Exception:
                pass
            await sleep(0.5)
    except Exception as e:
        print(f"[WARN] do_magic_emodji error: {e}")

# --- MagicText command handlers ---
@client.on(events.NewMessage(outgoing=True, pattern=r'^\.(?:mt|mtcmd)\s+(.+)', func=lambda e: True))
async def mt_handler(event):
    """
    .mt <text>  -> animate text using letters dict and MAGIC_SYMBOLS
    """
    try:
        sender = await event.get_sender()
        if not sender or getattr(sender, "id", None) != ADMIN_ID:
            return

        m = event.pattern_match
        text = m.group(1).strip()
        if not text:
            await event.reply(format_reply("⚠️ Iltimos, matn kiriting: .mt Sizning matningiz"))
            return

        text = text.replace("<3", "💖")
        # start with blank
        try:
            await event.edit(letters[" "].replace("0", MAGIC_SYMBOLS[0]))
        except Exception:
            pass

        _last = ""
        for letter in text:
            if _last and _last == letter:
                await sleep(0.7)
                continue

            if letter not in letters and _last not in letters:
                await sleep(0.7)
                continue

            frame = letters.get(letter.lower(), "**🚫 Not supported symbol**")
            frame = frame.replace("0", MAGIC_SYMBOLS[0]).replace("1", MAGIC_SYMBOLS[1])
            try:
                await event.edit(frame)
            except Exception:
                pass

            _last = letter
            await sleep(0.7)

        text = text.replace("💖", "<3")
        try:
            await event.edit(f"{MAGIC_SYMBOLS[0]}{MAGIC_SYMBOLS[1]}**{text}**{MAGIC_SYMBOLS[1]}{MAGIC_SYMBOLS[0]}")
        except Exception:
            try:
                await event.reply(f"{MAGIC_SYMBOLS[0]}{MAGIC_SYMBOLS[1]}{text}{MAGIC_SYMBOLS[1]}{MAGIC_SYMBOLS[0]}")
            except Exception:
                pass

    except Exception as e:
        print(f"[ERROR] mt_handler: {e}")
# --- Magic hearts commands ---
@client.on(events.NewMessage(outgoing=True, pattern=r'^\.magic$', func=lambda e: True))
async def magic_handler(event):
    try:
        sender = await event.get_sender()
        if not sender or getattr(sender, "id", None) != ADMIN_ID:
            return
        await do_magic_original(event)
    except Exception as e:
        print(f"[ERROR] magic_handler: {e}")

@client.on(events.NewMessage(outgoing=True, pattern=r'^\.magic2$', func=lambda e: True))
async def magic2_handler(event):
    try:
        sender = await event.get_sender()
        if not sender or getattr(sender, "id", None) != ADMIN_ID:
            return
        await do_magic_emodji(event)
    except Exception as e:
        print(f"[ERROR] magic2_handler: {e}")


# --- Ovoz memlar (example .ovoz hi.mp3) ---
@client.on(events.NewMessage(outgoing=True, pattern=r'^\.ovoz\s+(.+)', func=lambda e: True))
async def ovoz_handler(event):
    try:
        sender = await event.get_sender()
        if not sender or getattr(sender, "id", None) != ADMIN_ID:
            return
        m = event.pattern_match
        filename = m.group(1).strip()
        # bu yerda siz ovoz fayllaringiz papkasini ko‘rsatasiz:
        path = f"voices/{filename}"
        await event.respond(file=path)
        print(f"[ADMIN] Sent voice {path}")
    except Exception as e:
        print(f"[ERROR] ovoz_handler: {e}")


# === STARTUP / MAIN ===
async def main():
    await client.start(PHONE_NUMBER)
    me = await client.get_me()
    print(f"✅ Userbot running as {me.first_name} (@{getattr(me,'username',None)}) id={me.id}")
    print("Listening for private messages and .magic/.mt/.ovoz commands...")
    await client.run_until_disconnected()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print("Shutting down userbot.")
