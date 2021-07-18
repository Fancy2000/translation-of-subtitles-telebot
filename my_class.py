from youtube_transcript_api._errors import TranscriptsDisabled
from youtube_transcript_api import YouTubeTranscriptApi


# ------------CLASS----------------------------
class YoutubeSubsTranslate:
    no_subs_message = "Это видео не содержит субтитров."
    no_transl_message = "Не возможно перевести на ваш язык. Пожалуйста проверьте правильность ввода."

    def __init__(self, video_url):
        self.error_type = []
        self.video_id = video_url.split('=')[-1]
        if len(video_url) > 10:
            if video_url.split('=')[-2][-2:] == '&t':
                self.video_id = video_url.split('=')[-2][:-2]
        try:
            self.subs_list = YouTubeTranscriptApi().list_transcripts(self.video_id)
        except TranscriptsDisabled as td:
            print(self.no_subs_message.format(td))
            self.error_type.append("no_subs")
        self.error_type.append("no_errors")

    def __call__(self, need_lang):
        self.need_lang = need_lang
        subs_info = self._subs_info()
        opportunity_to_translate = self._opportunity_to_translate(self.need_lang)
        translated_transcript = self._get_translated_transcript(subs_info, opportunity_to_translate)
        final_file = self._creat_file_with_translate(translated_transcript)
        return final_file

# ----information about the type of subtitles that are in the video------------------
    def _subs_info(self):
        manual = True
        generate = True
        if not bool(self.subs_list._manually_created_transcripts):
            manual = False
        if not bool(self.subs_list._generated_transcripts):
            generate = False
        return {'manual': manual,
                'generate': generate}

# ---the ability to translate into a given language--------------------------
    def _opportunity_to_translate(self, lang_need):
        for language in self.subs_list._translation_languages:
            if lang_need == language['language']:
                lang_to_translate = language['language_code']
                return ["YES", lang_to_translate]
        return ["NO"]

# --translate the transcription------------------------------------------------
    def _get_translated_transcript(self, subs_info, opportunity_to_translate):
        find_manually = find_generated = ""
        if opportunity_to_translate[0] == "NO":
            print(self.no_transl_message)
            exit(1)
        lang_to_translate = opportunity_to_translate[1]
        if subs_info['manual']:
            for lang in self.subs_list._manually_created_transcripts:
                find_manually = lang
            transcript = self.subs_list.find_manually_created_transcript([find_manually])
        else:
            for lang in self.subs_list._generated_transcripts:
                find_generated = lang
            transcript = self.subs_list.find_generated_transcript([find_generated])
        return transcript.translate(lang_to_translate)

# ------make a .txt file with translation-----------------
    def _creat_file_with_translate(self, translated_transcript):
        h = False
        with open('translate.txt', 'w', encoding='utf-8') as txt_file:
            for line in translated_transcript.fetch():
                time = int(line['start'])
                if time < 60:
                    minute = 0
                    sec = time
                elif time >= 60:
                    minute, sec = divmod(time, 60)
                    if minute >= 60:
                        h = True
                        hours, minute = divmod(minute, 60)
                if h:
                    write_line = str(hours) + ":" + str(minute) + ":" + str(sec) + " " + line['text'] + '\n'
                else:
                    write_line = str(minute) + ":" + str(sec) + " " + line['text'] + '\n'
                txt_file.write(write_line)
            return txt_file
