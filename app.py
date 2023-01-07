import copy
from flask import Flask, render_template, request
from summarizer.sbert import SBertSummarizer
from summarizer import Summarizer
from parrot import Parrot
from flask import Flask, request, render_template, json
from paraphraser import *
import re
import random
from pywsd.similarity import max_similarity
from pywsd.lesk import adapted_lesk
from pywsd.lesk import simple_lesk
from pywsd.lesk import cosine_lesk
from nltk.corpus import wordnet as wn
import re
from nltk.corpus import stopwords
from summarizer import Summarizer
from nltk.tokenize import sent_tokenize
from flashtext import KeywordProcessor
from mcq_gen import mcq_gen
from flask import Flask, render_template, request, redirect, url_for, session, Response, flash, jsonify
from difflib import SequenceMatcher
from werkzeug.utils import secure_filename
import random
import requests


app = Flask(__name__)
app.secret_key = "var2112"


@app.route('/')
def index():
    return render_template('landingPage.html')


@app.route('/function')
def function():
    return render_template('function.html')


@app.route('/question')
def question():
    return render_template('question.html')


@app.route('/quest_gen', methods=['POST', 'GET'])
def quest_gen():
    full_text = request.form['quest_data']
    model = Summarizer()
    result = model(full_text, min_length=60, max_length=500, ratio=0.4)
    summarized_text = ''.join(result)
    mcq_gen_1 = mcq_gen()
    keywords = mcq_gen_1.get_nouns_multipartite(full_text)
    # print(keywords)
    filtered_keys = []
    for keyword in keywords:
        if keyword.lower() in summarized_text.lower():
            filtered_keys.append(keyword)
    sentences = mcq_gen_1.tokenize_sentences(summarized_text)
    keyword_sentence_mapping = mcq_gen_1.get_sentences_for_keyword(
        filtered_keys, sentences)
    key_distractor_list = {}

    for keyword in keyword_sentence_mapping:
        wordsense = mcq_gen_1.get_wordsense(
            keyword_sentence_mapping[keyword][0], keyword)
        if wordsense:
            distractors = mcq_gen_1.get_distractors_wordnet(wordsense, keyword)
            if len(distractors) == 0:
                distractors = mcq_gen_1.get_distractors_conceptnet(keyword)
            if len(distractors) != 0:
                key_distractor_list[keyword] = distractors
        else:

            distractors = mcq_gen_1.get_distractors_conceptnet(keyword)
            if len(distractors) != 0:
                key_distractor_list[keyword] = distractors
    index = 1
    question = []
    question_opt = []
    for each in key_distractor_list:
        sentence = keyword_sentence_mapping[each][0]
        pattern = re.compile(each, re.IGNORECASE)
        output = pattern.sub(" _______ ", sentence)
        question.append(output)

        print("%s)" % (index), output)

        choices = [each.capitalize()] + key_distractor_list[each]
        top4choices = choices[:4]
        random.shuffle(top4choices)
        optionchoices = ['a', 'b', 'c', 'd']
        temp = []

        for idx, choice in enumerate(top4choices):
            print("\t", optionchoices[idx], ")", " ", choice)
            temp.append("{0}".format(choice))
            # temp.append("  {0} ) {1}".format(
            #     optionchoices[idx], choice))
        # temp.append("Answer: {0}".format(each))
        temp.append(each)
        # print(temp)
        question_opt.append(temp)

        index = index + 1

    print(question)
    print(question_opt)

    res = {}
    for key in question:
        for value in question_opt:
            res[key] = value
            question_opt.remove(value)
            break
    print("=========== from mcq_gen")
    print(res)
    res_copy = res
    session['mcq'] = res_copy

    return render_template('generatedQuestion.html', result=res)


@app.route('/citigen')
def citigen():
    return render_template('citation.html')


@app.route('/mcq')
def mcq():
    return render_template('mcq.html')


model = SBertSummarizer('paraphrase-MiniLM-L6-v2')


@app.route('/parphrase')
def para():
    return render_template('paraphrase.html')


@app.route('/gen_parphrase', methods=['POST', 'GET'])
def para_gen():
    body = request.form['para']
    result = " ".join([get_paraphrased_sentences(sent)
                      for sent in sent_tokenize(body)])
    return render_template('gen_paraphrase.html', result=result)


@app.route("/mcq_gen_1", methods=['POST', 'GET'])
def mcq_gen_1():
    full_text = request.form['mcq_data']
    model = Summarizer()
    result = model(full_text, min_length=60, max_length=500, ratio=0.4)
    summarized_text = ''.join(result)
    mcq_gen_1 = mcq_gen()
    keywords = mcq_gen_1.get_nouns_multipartite(full_text)
    # print(keywords)
    filtered_keys = []
    for keyword in keywords:
        if keyword.lower() in summarized_text.lower():
            filtered_keys.append(keyword)
    sentences = mcq_gen_1.tokenize_sentences(summarized_text)
    keyword_sentence_mapping = mcq_gen_1.get_sentences_for_keyword(
        filtered_keys, sentences)
    key_distractor_list = {}

    for keyword in keyword_sentence_mapping:
        wordsense = mcq_gen_1.get_wordsense(
            keyword_sentence_mapping[keyword][0], keyword)
        if wordsense:
            distractors = mcq_gen_1.get_distractors_wordnet(wordsense, keyword)
            if len(distractors) == 0:
                distractors = mcq_gen_1.get_distractors_conceptnet(keyword)
            if len(distractors) != 0:
                key_distractor_list[keyword] = distractors
        else:

            distractors = mcq_gen_1.get_distractors_conceptnet(keyword)
            if len(distractors) != 0:
                key_distractor_list[keyword] = distractors
    index = 1
    question = []
    question_opt = []
    for each in key_distractor_list:
        sentence = keyword_sentence_mapping[each][0]
        pattern = re.compile(each, re.IGNORECASE)
        output = pattern.sub(" _______ ", sentence)
        question.append(output)

        print("%s)" % (index), output)

        choices = [each.capitalize()] + key_distractor_list[each]
        top4choices = choices[:4]
        random.shuffle(top4choices)
        optionchoices = ['a', 'b', 'c', 'd']
        temp = []

        for idx, choice in enumerate(top4choices):
            print("\t", optionchoices[idx], ")", " ", choice)
            temp.append("{0}".format(choice))
            # temp.append("  {0} ) {1}".format(
            #     optionchoices[idx], choice))
        # temp.append("Answer: {0}".format(each))
        temp.append(each)
        # print(temp)
        question_opt.append(temp)

        index = index + 1

    print(question)
    print(question_opt)

    res = {}
    for key in question:
        for value in question_opt:
            res[key] = value
            question_opt.remove(value)
            break
    print("=========== from mcq_gen")
    print(res)
    res_copy = res
    session['mcq'] = res_copy

    return render_template('gen_mcq.html', result=res)


@app.route("/quiz")
def quiz():
    questions = session['mcq']
    quiz_questions = copy.deepcopy(questions)
    qts = []
    opts = []
    ans = []
    items = quiz_questions.items()
    for item in items:
        qts.append(item[0]), opts.append(item[1])

    for ans_ls in opts:
        temp = ans_ls.pop()
        ans.append(temp.title())

    opts_len = []
    for opt in opts:
        temp = {}
        for index in range(len(opt)):
            temp[str(index)] = opt[index]
        opts_len.append(temp)

    return render_template('quiz.html', result=questions, questions=qts, options=opts_len, answers=ans)


@app.route("/summarize", methods=['POST', 'GET'])
def getSummary():
    body = request.form['data']
    length = request.form['slider']

    length = int(length)
    result = model(body, num_sentences=length)
    return render_template('summary.html', result=result)


@app.route('/plagarism')
def plagarism():
    return render_template('plag.html')


@app.route("/plag", methods=['POST'])
def plag():
    try:
        content = request.get_json()
        # data processing code
        # content['p'] -> textarea 1 content
        # content['q'] -> textarea 2 content
        similarity = SequenceMatcher(None, content['p'], content['q']).ratio()
        similarity = similarity * 100
        similarity = int(similarity)
        sim = str(similarity)
        return jsonify({
            'status': True,
            'percentage': similarity,
            'result': "Your data is measured to be nearly " + sim + "% matchably"
        })

    except Exception as e:
        print(e)
        return jsonify({
            'status': False,
            'result': "Error in processing"
        })


if __name__ == "__main__":
    app.run(debug=True, port=8080, use_reloader=False)
    # app.run(host="0.0.0.0", port=5001, debug=True)
