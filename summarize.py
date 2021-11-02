import docx2txt
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import re
from open_files.clean_html import open_html
from open_files.clean_pdf import open_pdf
from open_files.clean_text import clean_text


def summary_length(text, percentage=15):
    # count words in string
    res = len(re.findall(r'\w+', text))
    # return min words in summary
    res = res * percentage * (1 / 100)

    return int(res)


def word_in_summary_fun(percentage, min_words, text):
    if isinstance(percentage, int):
        words_in_summary = summary_length(text, percentage)
    elif isinstance(min_words, int):
        words_in_summary = min_words
    else:
        words_in_summary = summary_length(text, 10)

    return words_in_summary


def bart_model(text, words_in_summary):
    tokenizer = AutoTokenizer.from_pretrained("facebook/bart-large-cnn")
    model = AutoModelForSeq2SeqLM.from_pretrained("facebook/bart-large-cnn")

    article_input_ids = \
        tokenizer.encode(text, return_tensors='pt', truncation=True)
    outputs = model.generate(article_input_ids,
                             num_beams=4,
                             length_penalty=2.0,
                             min_length=words_in_summary,
                             max_length=words_in_summary + 50,
                             no_repeat_ngram_size=3)

    summary = tokenizer.decode(outputs[0])
    summary = summary[7:-4]

    return summary


def summarize(filename, percentage, min_words):
    if filename[-4:] == "docx":
        text = docx2txt.process(filename)
    elif filename[-4:] == "html":
        text = open_html(filename)
    elif filename[-3:] == "pdf":
        text = open_pdf(filename)
    else:
        with open(filename, 'r') as file:
            text = file.read()
    print("working")
    # remove links, specials signs, emails...
    text = clean_text(text)
    # calculate how many words user want's in his summary
    words_in_summary = word_in_summary_fun(percentage, min_words, text)

    return bart_model(text, words_in_summary)


def summarize_from_web(url, percentage, min_words):
    text = open_html(url)
    # remove links, specials signs, emails...
    text = clean_text(text)
    # calculate how many words user want's in his summary
    words_in_summary = word_in_summary_fun(percentage, min_words, text)

    return bart_model(text, words_in_summary)
