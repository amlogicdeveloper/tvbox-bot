import os

BOT_TOKEN = os.environ.get("8587107531:AAE0uHpYweTxwJF0zDOJV4iwIicKRGyqPls")

BRAND_NAME = "Android Assistant"
BRAND_TAGLINE = "Your Smart TvBox Companion"

WELCOME_MESSAGE = """🤖 *Android Assistant*
✦ Smart Bot untuk Komunitas TvBox ✦

Halo {mention}, selamat datang! 👋

Kamu baru saja bergabung di:

┏━━━━━━━━━━━━━━━━━━━━┓
┃  📺 *KOMUNITAS TVBOX ANDROID*  ┃
┗━━━━━━━━━━━━━━━━━━━━┛

Grup silaturahmi & diskusi sesama pengguna Android TV Box. Semua tipe boleh sharing — newbie atau master, semua welcome!

┌───── 🛡️ *RULES SINGKAT* ─────┐

▪️ Hormati sesama anggota
▪️ No spam, no hoax, no drama
▪️ Belajar bareng, no judge
▪️ Ada masalah? Kasih screenshot + detail

└───────────────────────┘

📌 *Info penting*: Cek pesan tersemat di atas ⏫
📥 Link download, tutorial & FAQ ada di situ

━━━━━━━━━━━━━━━━━━━━━

Selamat ngobrol & semoga betah! ✨

*Android Assistant* 🤖
_Powered by Komunitas TvBox Android_

•══════◎❅◎❦۩❁۩❦◎❅◎═════•"""

RULES_MESSAGE = """📜 *ATURAN KOMUNITAS TVBOX ANDROID*

Dikelola oleh *Android Assistant*

1️⃣ 🤝 Saling menghargai sesama anggota
2️⃣ 📚 Tidak ada nubi atau yang paling jago — belajar bareng
3️⃣ 🚫 No spam, hoax, atau link aneh
4️⃣ 🐛 Ada masalah? Kasih detail + screenshot
5️⃣ 💾 Share ROM/APK cuma dari sumber terpercaya
6️⃣ 🔞 Dilarang share konten dewasa & judi

Pelanggaran = mute/ban tanpa peringatan.

Salam,
*Android Assistant*"""

BANNED_WORDS = {
    "judi", "slot", "togel", "pinjol", "pinjaman online",
    "bokep", "porno", "xxx", "18+",
    "investasi", "crypto", "bitcoin", "scam", "penipuan",
    "obat kuat", "viagra", "forex"
}

ALLOWED_DOMAINS = {
    "https://t.me/komunitas_tvbox_android",
    "tvbox-android.com"
}

MAX_SAME_MESSAGE_PER_MINUTE = 3
MAX_LINKS_PER_MESSAGE = 2
MUTE_DURATION_SECONDS = 300
WARN_LIMIT = 3
