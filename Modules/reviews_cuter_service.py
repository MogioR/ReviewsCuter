import re
import json

import pandas as pd
from google.cloud import language_v1
from natasha import Segmenter, MorphVocab, NewsEmbedding, NewsMorphTagger, NewsNERTagger, Doc, NewsSyntaxParser
from nltk.corpus import stopwords

from Modules.google_sheets_api import GoogleSheetsApi

ALPHABET = ["а", "б", "в", "г", "д", "е", "ё", "ж", "з", "и", "й", "к", "л", "м", "н", "о", " ",
            "п", "р", "с", "т", "у", "ф", "х", "ц", "ч", "ш", "щ", "ъ", "ы", "ь", "э", "ю", "я",
            "a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q",
            "r", "s", "t", "u", "v", "w", "x", "y", "z"]
ALPHABET = list(map(lambda x: x.upper(), ALPHABET)) + ALPHABET


class ReviewsCuterService:
    def __init__(self):
        self.black_words = []
        self.data = pd.DataFrame()

        self.natasha_emb = NewsEmbedding()
        self.natasha_syntax_parser = NewsSyntaxParser(self.natasha_emb)
        self.natasha_ner_tagger = NewsNERTagger(self.natasha_emb)
        self.natasha_segmenter = Segmenter()
        self.natasha_morph_vocab = MorphVocab()
        self.natasha_morph_tagger = NewsMorphTagger(self.natasha_emb)
        self.stop_words = stopwords.words('russian')

    # Download reviews from google sheets
    def download_reviews(self, token, document_id, list_name):
        service = GoogleSheetsApi(token)
        raw_data = service.get_data_from_sheets(document_id, list_name, 'A2', 'B' +
                                                str(service.get_list_size(document_id, list_name)[1]), 'ROWS')
        i = 0
        for row in raw_data:
            self.data = self.data.append({'comment_id': row[0], 'review_text': row[1]}, ignore_index=True)

            if i == 99:
               break
            i += 1

        print(sum(list(map(len, list(self.data['review_text'].values)))))

    # Download black words from google sheets
    def download_black_words(self, token, document_id, list_name):
        service = GoogleSheetsApi(token)
        data = service.get_data_from_sheets(document_id, list_name, 'A1', 'A' +
                                            str(service.get_list_size(document_id, list_name)[1]), 'COLUMNS')
        self.black_words = data[0]

    def clear_text(self, text):
        # Del stop_words and non letter symbols
        cleared_text = ''.join([letter if letter in ALPHABET else ' ' for letter in text])
        cleared_text = ' '.join([word for word in cleared_text.split() if word not in self.stop_words])

        # Segmentation
        doc = Doc(cleared_text)
        doc.segment(self.natasha_segmenter)
        doc.tag_morph(self.natasha_morph_tagger)

        # Del black words
        words = []
        for token in doc.tokens:
            token.lemmatize(self.natasha_morph_vocab)
            # print(token.text, ' - ', token.lemma)
            if token.lemma not in self.black_words:
                words.append(token.text)
            else:
                pass
                # print('Del ', token.text)

        cleared_text = ' '.join(words)
        # print(text)
        # print(cleared_text)
        return cleared_text

    def tokenize(self):
        self.data['review_clear'] = list(map(self.clear_text, self.data['review_text']))
        print(sum(list(map(len, list(self.data['review_clear'].values)))))
        print(self.data['review_text'].values[1])
        print(self.data['review_clear'].values[1])

    def get_google_analysis(self):
        reports = []
        data = self.data['review_clear'].values
        buf_block = ''
        buf_reviews = []

        for i in range(len(data)):
            if len(buf_block) + len(data[i]) <= 1000:
                buf_block += data[i]
                buf_reviews.append(i)
            else:
                reports.append([self.get_list_entities(buf_block), buf_reviews])
                buf_block = ''
                buf_reviews = []
                buf_block += data[i]
                buf_reviews.append(i)

        reports.append([self.get_list_entities(buf_block), buf_reviews])

        return reports

    def shortening_reviews(self, export_file):
        reports = self.get_google_analysis()
        data = self.data['review_text'].values

        all_new_reviews = []
        all_skipped_parts = []
        all_deleted_sentences = []

        export_items = []

        for report in reports:
            for review_index in report[1]:
                new_review, skipped_part, deleted_sentences = self.shortening_review(data[review_index], report[0])
                all_new_reviews.append(new_review)
                all_skipped_parts.append(skipped_part)
                all_deleted_sentences.append(deleted_sentences)
                export_items.append({'input_review': data[review_index], 'output_review': new_review,
                                     'deleted_words': skipped_part, 'deleted_sentences': deleted_sentences})

        with open(export_file, 'w', encoding='utf-8') as f:
            json.dump(export_items, f, ensure_ascii=False)

        return all_new_reviews, all_skipped_parts, all_deleted_sentences

    def shortening_review(self, review, entities):
        doc = Doc(review)
        doc.segment(self.natasha_segmenter)
        doc.parse_syntax(self.natasha_syntax_parser)

        # Delete sentences without entities
        deleted_sentences = []
        for sentence in doc.sents:
            if self.regularity_check(sentence.text, entities):
                pass
            else:
                # print('Del ', sentence.text)
                deleted_sentences.append(sentence.text)
                sentence.text = ''
                sentence.tokens = []

        # Delete start of first sentence
        skipped_part = ''
        stop_flag = False
        for sentence in doc.sents:
            if sentence.text != '':
                for token in sentence.tokens:
                    if token.rel == 'root':
                        if not self.regularity_check(sentence.text[:token.start-sentence.start], entities):
                            skipped_part = sentence.text[:token.start - sentence.start]
                            sentence.text = sentence.text[token.start-sentence.start:]
                            # print(sentence.text)
                        stop_flag = True
                        break
            if stop_flag:
                break

        # Build shorted review
        sentences = []
        for sentence in doc.sents:
            if sentence.text != '':
                sentences.append(sentence.text)

        # print(review)
        # print(' '.join(sentences))

        return ' '.join(sentences), skipped_part, deleted_sentences

    @staticmethod
    def regularity_check(data: str, dictionary: list):
        including = False
        data_str = str(data).lower()

        for word in dictionary:
            including = including or (
                        re.search(r'^' + word + '[^A-Za-zА-ЯЁа-яё]|[^A-Za-zА-ЯЁа-яё]' + word +
                                  '[^A-Za-zА-ЯЁа-яё]|[^A-Za-zА-ЯЁа-яё]' + word + '$'
                                  , data_str) is not None)
            if including is True:
                break

        return including


    @staticmethod
    def get_list_entities(text_block):
        client = language_v1.LanguageServiceClient()
        type_ = language_v1.Document.Type.PLAIN_TEXT
        language = "ru"

        document = {"content": text_block, "type_": type_, "language": language}
        encoding_type = language_v1.EncodingType.UTF8
        response = client.analyze_entities(request={'document': document, 'encoding_type': encoding_type})

        detected_entities = []
        for entity in response.entities:
            detected_entities.append(entity.name)

        return detected_entities

