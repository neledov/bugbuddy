#!/usr/bin/env python
# -*- coding: utf8 -*-

import re
from requests import get
from bs4 import BeautifulSoup
from flask import Flask, jsonify, request
from flask_restful import Api

app = Flask(__name__)
api = Api(app)


def google_search(term, num_results=10, lang="en"):
    usr_agent = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/61.0.3163.100 Safari/537.36'}
    usr_agent_list = {}  # TODO: add user agent randomization to avoid to be google blocked

    def fetch_results(search_term, number_results, language_code):
        escaped_search_term = search_term.replace(' ', '+')

        google_url = 'https://www.google.com/search?q={}&num={}&hl={}'.format(escaped_search_term, number_results + 1,
                                                                              language_code)
        response = get(google_url, headers=usr_agent)
        response.raise_for_status()
        print(response.text)
        return response.text

    def parse_results(raw_html):
        soup = BeautifulSoup(raw_html, 'html.parser')
        result_block = soup.find_all('div', attrs={'class': 'g'})
        for result in result_block:
            link = result.find('a', href=True)
            title = result.find('h3')
            if link and title:
                yield link['href']

    html = fetch_results(term, num_results, lang)
    return list(parse_results(html))


@app.route('/defect/', methods=['GET'])
def get_defects():
    input_search_string = request.args.get('err_msg')
    input_sanitized = list(dict.fromkeys(get_google_results(input_search_string.replace('%20', '* '))))
    list_final = [
        '[{}]("https://quickview.cloudapps.cisco.com/quickview/bug/{}) : {}&#13;'.format(x, x, get_defect_title(x)) for
        x in input_sanitized]
    return jsonify(list_final)


@app.route('/defect/description ', methods=['GET'])
def get_defect_description():
    defect_id = request.args.get('defect_id')
    page = get("https://quickview.cloudapps.cisco.com/quickview/bug/{}".format(defect_id),
               headers={'User-agent': 'Chrome/90.0.4430.72'})
    regexp_title = re.compile(r'<title>Cisco Bug: ([\S\s]*?)</title>', re.MULTILINE)
    regexp_symptom = re.compile(r'<B>Symptom:</B>([\S\s]*?)<B>Conditions:</B>', re.MULTILINE)
    regexp_condition = re.compile(r'<B>Conditions:</B>([\S\s]*?)</pre>', re.MULTILINE)
    ##########################################################
    result_title = re.findall(regexp_title, page.text)
    result_symptom = re.findall(regexp_symptom, page.text)
    result_condition = re.findall(regexp_condition, page.text)
    result_full = []
    if not result_symptom:
        result_full.insert(0, "No information available")
    else:
        result_symptom.insert(0, "Title : " + result_title[0])
        result_symptom.insert(1, "Quickview URL : https://quickview.cloudapps.cisco.com/quickview/bug/" + defect_id)
        result_symptom.insert(2,
                              "Symptoms of " + defect_id + " :")

        result_condition.insert(0, "Condition :")
        result = result_symptom + result_condition
        result_full = list(filter(None, result))
    return jsonify(result_full)


def get_defect_title(defect_id):
    page_load_result = get("https://quickview.cloudapps.cisco.com/quickview/bug/" + defect_id,
                           headers={'User-agent': 'Chrome/90.0.4430.72'})

    regexp_title = re.compile(r'<title>Cisco Bug: .{13}([\S\s]*?)</title>', re.MULTILINE)
    result_title = re.findall(regexp_title, page_load_result.text)
    result_final = []
    if not result_title:
        result_final.insert(0, " - No information available externally")
    else:
        result_final = list(filter(None, result_title))
    return result_final[0]


def list_to_lines(list_source):
    return '\n'.join(str(p) for p in list_source)


def get_google_results(user_input):
    regexp_search = re.compile(r'(?=CSC[\S\s]).{10}', re.MULTILINE)
    result_search = google_search("""Cisco Defect """ + user_input, num_results=100)
    result_final = re.findall(regexp_search, list_to_lines(result_search))
    if not result_final:
        result_final.insert(0, "Nothing found, please be more exact")
    print(result_final)
    return result_final[:50]


app.run(host='0.0.0.0', debug=True)
