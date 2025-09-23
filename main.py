import asyncio
import re
import random
from telethon import TelegramClient, events
from telethon.tl.types import PeerUser

# 🔐 YOUR CREDENTIALS — KEEP PRIVATE!
API_ID = 29593383
          # ❗ REPLACE WITH YOUR API ID
API_HASH = '1c9eb4e8d4e24039f501f553c0cd3f22'  # ❗ REPLACE WITH YOUR API HASH
PHONE_NUMBER = '+998950584595'   # Your phone with country code

# 🧠 Natural response mapping (regex-based, case-insensitive)
RESPONSES = {
        # Greetings
    r"(?i)^(salom|assalomu alaykum)$": "Va alaykum assalom! 🤲",
    r"(?i).*hey.*": "Hey! 😄 Qalaysiz?",
    r"(?i).*hi.*": "Hello! 🌸",
    r"(?i).*xayr.*": "Xayr! Yaxshi kunlar tilayman 🌞",
    r"(?i).*good morning.*": "Good morning! ☀️",
    r"(?i).*good night.*": "Good night! 🌙",
    r"(?i).*bonjour.*": "Bonjour! 🌸",
    
    # How are you / wellbeing
    r"(?i).*nima qalesan\?*": "Yaxshi, rahmat! Sizchi? 😊",
    r"(?i).*qancha\sbemalol\?*": "Hali ham yaxshi, rahmat! 🌿",
    r"(?i).*yaxshimisiz\?*": "Ha, rahmat! Sizchi? 😇",
    r"(?i).*qalaysiz\?*": "Zo‘r, rahmat! Sizchi? 😄",
    r"(?i).*ishlaring yaxshimi\?*": "Ha, hammasi joyida! 💼",
    r"(?i).*xo‘rsizmi\?*": "Yo‘q, hammasi joyida 😊",
    r"(?i).*xursand\?*": "Ha, juda xursandman! 😄 Sizchi?",
    r"(?i).*achchiq\?*": "Hm... ozgina, lekin yaxshilashga harakat qilayapman 😌",
    
    # Location / origin
    r"(?i).*qayerdansan\?*": "Men O‘zbekistondanman, sizchi? 🇺🇿",
    r"(?i).*tugilgan joy\?*": "Men Toshkentdanman 🏙️",
    r"(?i).*qayerda yashaysan\?*": "Hozir Toshkentda yashayapman 🌆",
    
    # Work / activity
    r"(?i).*qilayotgan ishing nima\?*": "Hozir biroz ishlayapman, sizchi? 💼",
    r"(?i).*ishlayapsan\?*": "Ha, biroz ishlayapman, dam olishga ham vaqt topaman 😌",
    r"(?i).*o‘qiyapsizmi\?*": "Ha, o‘qiyman, bilim olishni yaxshi ko‘raman 📚",
    r"(?i).*hobbying nima\?*": "Kitob o‘qish, musiqa tinglash va kod yozish 📖🎵💻",
    r"(?i).*kino ko‘rmoqchimisiz\?*": "Ha, kino yaxshi! Sizning tavsiyalaringiz bormi? 🎬",
    
    # Names / keywords
    r"(?i)^(abdullo|abdulloh)$": "Ha, qanday? 😄",
    r"(?i).*umarov.*": "✨ Umarov hozir band, pulin bosa 40k ✨💸",
    
    # Casual / friendly
    r"(?i).*qilasan\?*": "Hozir shu ish bilan bandman 😎",
    r"(?i).*ovqat yeding\?*": "Ha, endi biroz dam olaman 🍽️",
    r"(?i).*dam olayapsan\?*": "Ha, dam olaman, rahmat! 🌿",
    r"(?i).*kitob o‘qiyapsiz\?*": "Ha, so‘nggi o‘qigan kitobim juda qiziqarli 📚",
    r"(?i).*sport qilasizmi\?*": "Ha, yugurish va yoga bilan shug‘ullanaman 🏃‍♂️🧘‍♂️",
    r"(?i).*musiqa tinglaysiz\?*": "Ha, turli janrlarni tinglayman 🎵🎧",
    r"(?i).*ha ok\?*": "Ha, mayli bopti 🎵🎧",
    r"(?i).*Abdulo\?*": "nma? 🎵🎧",
    r"(?i).*ok\?*": "ok boldi uxla endi 🎵🧠",
    
    # Appreciation / thanks
    r"(?i).*rahmat.*": "Doimo mamnunman, xabar qilganingiz uchun ❤️",
    r"(?i).*xayrli kun.*": "Sizga ham xayrli kun! 🌞",
    r"(?i).*good job.*": "Thank you! 🙏",
    r"(?i).*tabrik.*": "Rahmat! 🎉 Sizni ham tabriklayman 🥳",
    
    # Fun / jokes
    r"(?i).*hazil qil.*": "Haha 😄 Haqiqatan ham qiziq! 😂",
    r"(?i).*manmi? | mami?.*": "Haha da san ukam .!. 😂",
    r"(?i).*mem.*": "Haha, memlar juda kulgili 😂📸",
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
    r"(?i).*soli|Soliha.*": "dilshodni kal rapunseli👸💀"
    

}

# 🚫 Offensive keyword patterns (add more as needed)
OFFENSIVE_PATTERNS = [
    r"\b(sex|porn|jinsiy|amorat|badword1|sh*t|f\*ck)\b|dabba|dnx|wtf|skaman|skama|yba|🦒|📮|📬|🖕|hentai|qoto|tasho|yban|abl|Abl|nx|soska|pashol|wth|seks|am|bruh|u bla|gandon|gey|jala|jalab|wttttffff|xD|ble|blaa|bla|qutoq|xuy|xy|tutaq",  # Customize with your own
]

# 🌸 Aesthetic reply formatter
def format_reply(text: str) -> str:
    decorations = ["💬", "🌿", "🫧", "🕊️", "🫶", "🫀", "😇",
    "✨", "🌸", "🌈", "🔥", "💖", "🍀", "🌺",   
    "🌼", "🌻", "🎉", "🪷", "💫", "🪐", "🎈",
    "🌟", "💎", "🧿", "🍄", "🪴", "☀️", "🌙",
    "⭐", "🌹", "🥰", "😊", "😌", "🤍", "🌊",
    "🍃", "🕯️", "🎶", "🧸", "💐", "🌷", "🍁","🍓","🗿","🧠","💀","✅"]
    return f"{random.choice(decorations)} {text} {random.choice(decorations)}"

# ⚠️ Check if message is offensive
def is_offensive(text: str) -> bool:
    text_lower = text.lower()
    for pattern in OFFENSIVE_PATTERNS:
        if re.search(pattern, text_lower):
            return True
    return False

# 🤖 Initialize client
client = TelegramClient('autoreply_session', API_ID, API_HASH)

@client.on(events.NewMessage(incoming=True))
async def handle_private_message(event):
    # ✅ Only respond in private 1:1 chats
    if not event.is_private:
        return

    sender = await event.get_sender()
    if sender.bot:  # ignore bots
        return

    message_text = event.raw_text or ""

    # 🚫 If offensive, delete message and DO NOT reply
    if is_offensive(message_text):
        try:
            await event.delete()
            print(f"[🛡️ Deleted offensive message from {sender.first_name}]")
        except Exception as e:
            print(f"[⚠️ Could not delete message]: {e}")
        return

    # 💬 Match natural conversation triggers
    for pattern, reply in RESPONSES.items():
        if re.search(pattern, message_text):
            # 🧍 Add human-like delay (0.5 to 3 seconds)
            await asyncio.sleep(random.uniform(0.5, 3.0))

            # ✍️ Send aesthetic reply
            formatted_reply = format_reply(reply)
            await event.reply(formatted_reply)
            print(f"[📩 Replied to {sender.first_name}]: {formatted_reply}")
            return

    # 🔄 Optional: Friendly fallback for unmatched messages
    fallbacks = [
    "vay kuk",
    "Ha, eshitdim 😊",
    "Qiziq, davom et 😄",
    "Gapir, tinglayman 🌼",
    "Rahmat, xabar qilganing uchun ❤️",
    "Hm... qanday fikrdasiz? 🤔",
    "Ajoyib, shunday davom eting ✨",
    "Ha, tushundim 😌",
    "Qiziqarli, batafsilroq aytib bera olasizmi? 📝",
    "Hmm… menimcha bu juda muhim 😎",
    "Rahmat, eshitib quvonib ketdim 😇",
    "Ha, shuni oldindan bilganim yaxshi bo‘lar edi 🌟",
    "Haqiqatan ham? Qanday qilib? 🤩",
    "To‘g‘ri, bu fikr juda qiziq 😏",
    "Menimcha, davom etishimiz kerak 😌",
    "Wow, shuni eshitib hayron bo‘ldim 😲",
    "Ajoyib fikr, boshqalar bilan ham bo‘lishsak bo‘ladi 🔥",
    "Ha, tushundim, rahmat tushuntirgani uchun 🙏",
    "tilin chqb qobdimi",
    "kotini yoraman",
    "Haha, bu juda kulgili 😂" ,
    "Hmm… buni yanada batafsilroq tushuntirib bera olasizmi? 🧐",
    "Qiziq, davom eting, men tinglayapman 👂",
    "Wow, ajoyib xabar! 🌈"
    ]
    if random.random() < 0.7:  # 70% chance to reply to unknown messages
        await asyncio.sleep(random.uniform(1.0, 2.5))
        await event.reply(format_reply(random.choice(fallbacks)))

# 🚀 Start the client
async def main():
    await client.start(PHONE_NUMBER)
    print("✅ Userbot is running... Listening for private messages.")
    print("⚠️ Remember: Using userbots violates Telegram ToS. Use at your own risk.")
    await client.run_until_disconnected()

# ▶️ Run
if __name__ == '__main__':
    asyncio.run(main())