import os
from google import genai
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

BOT_TOKEN = "8844929282:AAHN3lg7Xfqtyyora4tNrYrKDX_YUCxBltg"
GEMINI_API_KEY = "AQ.Ab8RN6JHLPFvTTv56N3o4Ist1mSepfIGyaCc9kMbW6GpmScaeQ"
ALLOWED_USER_ID = 5986210641

client = genai.Client(api_key=GEMINI_API_KEY)

async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    
    if user_id != ALLOWED_USER_ID:
        await update.message.reply_text("ခွင့်ပြုချက်မရှိပါ။ ဒီ Bot ကို ပိုင်ရှင်တစ်ဦးတည်းသာ အသုံးပြုနိုင်ပါသည်။")
        return

    status_msg = await update.message.reply_text("ဗီဒီယိုကို လက်ခံရရှိပါပြီ။ Gemini AI ဖြင့် စာသားပြောင်းနေပါသည်...")
    
    file_unique_id = update.message.video.file_unique_id
    video_path = f"temp_{file_unique_id}.mp4"
    txt_path = f"transcript_{file_unique_id}.txt"

    try:
        video_file = await update.message.video.get_file()
        await video_file.download_to_drive(video_path)

        uploaded_file = client.files.upload(file=video_path)

        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=[
                uploaded_file,
                "Transcribe the spoken language in this video completely and accurately. Return only the transcript text without extra markdown codeblocks or conversational response."
            ]
        )

        transcript_text = response.text.strip()
        client.files.delete(name=uploaded_file.name)

        if len(transcript_text) <= 4000:
            await update.message.reply_text(f"**Transcript:**\n\n{transcript_text}")
        else:
            with open(txt_path, "w", encoding="utf-8") as f:
                f.write(transcript_text)

            await update.message.reply_document(
                document=open(txt_path, "rb"),
                filename="transcript.txt",
                caption="စာသား ရှည်လျားသောကြောင့် .txt ဖိုင်အဖြစ် ပို့ပေးထားပါသည်။"
            )

    except Exception as e:
        await update.message.reply_text(f"အမှားအယွင်း ဖြစ်ပေါ်ခဲ့သည်: {str(e)}")

    finally:
        await status_msg.delete()
        if os.path.exists(video_path):
            os.remove(video_path)
        if os.path.exists(txt_path):
            os.remove(txt_path)

if __name__ == '__main__':
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.VIDEO, handle_video))
    app.run_polling()

