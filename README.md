# 🎙️ صانع الفويس أوفر الاحترافي — لغز وحقيقة (`@لغزوحقيقه`)

تطبيق ويب مبني باستخدام **Streamlit** ومحرك **Google Gemini 3.1 Flash TTS**، مخصص لإنتاج تعليق صوتي سينمائي بلهجة المقاهي المصرية الشعبية (Persona: سامح سند / حكاوي الشارع)، مع نظام تقسيم ذكي للنصوص الطويلة وماسترينج صوتي احترافي بمعيار **EBU R128** (-16 LUFS / True Peak -1.5 dBTP).

---

## 🚀 التشغيل المحلي (Local Run)

1. افتح المجلد في Terminal أو PowerShell:
   ```powershell
   cd streamlit_vo_creator
   ```
2. شغل التطبيق مباشرة عبر دبل كليك على `run_streamlit.bat` أو عبر الأمر:
   ```bash
   streamlit run app.py
   ```
3. سيفتح التطبيق تلقائياً في متصفحك على: `http://localhost:8501`.

---

## ☁️ خطوات الرفع والاستضافة السحابية مجاناً 24/7 (Streamlit Cloud)

يمكنك استضافة هذا التطبيق مجاناً وبشكل دائم عبر **Streamlit Community Cloud** لتتمكن من فتحه من هاتفك أو أي جهاز دون الحاجة لتشغيل حاسوبك:

### 1. رفع المشروع على GitHub
1. أنشئ مستودعاً جديداً (New Repository) على [GitHub](https://github.com/) (يمكنك اختياره Private للحفاظ على خصوصية عملك).
2. ارفع محتويات مجلد `streamlit_vo_creator`:
   - `app.py`
   - `requirements.txt`
   - `packages.txt` (يحتوي على `ffmpeg` ليتم تثبيته تلقائياً على نظام Debian في السحابة)
   - `.streamlit/config.toml`

### 2. الربط مع Streamlit Cloud
1. توجه إلى [share.streamlit.io](https://share.streamlit.io) وسجل الدخول بحساب GitHub.
2. اضغط على **"Create app"** ثم اختر المستودع الخاص بك.
3. اكتب مسار الملف الرئيسي: `app.py`.
4. اضغط **Deploy!**.

### 3. ضبط مفاتيح الـ API في الأسرار (Secrets)
1. من لوحة تحكم التطبيق على Streamlit Cloud، اذهب إلى:
   `Settings` ➔ `Secrets`
2. أضف المفاتيح بالشكل التالي:
   ```toml
   GEMINI_API_KEYS = [
       "YOUR_GEMINI_API_KEY_1",
       "YOUR_GEMINI_API_KEY_2"
   ]
   ```
3. اضغط **Save**، وسيقوم التطبيق بإعادة التشغيل تلقائياً ومتاح على رابط دائم!

---

## 🎛️ المواصفات الفنية المعتمدة
- **الموديل الصوتي:** `gemini-3.1-flash-tts-preview`
- **الصوت:** `Charon`
- **البرومبت الصوتي:** Sameh Sanad Cairo Street Storyteller Persona
- **فترات السكون:** 0.5 ثانية بين المشاهد الدرامية
- **معيار الماسترينج:** EBU R128 Dual-Pass Linear (-16.0 LUFS, -1.5 dBTP)
- **صيغ التصدير:** 320 kbps CBR MP3 + 44.1kHz 16-bit PCM WAV
