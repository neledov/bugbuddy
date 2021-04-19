#!/usr/bin/env python
# -*- coding: utf8 -*-

import re
import requests
from googlesearch import search
from flask import Flask, jsonify
from flask_restful import Api, Resource

app = Flask(__name__)
api = Api(app)


class DefectResource(Resource):
    def get(self, description_text):
        description_text = description_text.replace('description_text=', '')
        input_sanitized = list(dict.fromkeys(get_google_results(description_text.replace('%20', '* '))))
        list_final = [
            '[' + x + "](" + "https://quickview.cloudapps.cisco.com/quickview/bug/" + x + ") : " + get_defect_title(
                x) + '&#13;'
            for x in input_sanitized]
        return jsonify(list_final)


def get_defect_title(bugid):
    page_load_result = requests.get("https://quickview.cloudapps.cisco.com/quickview/bug/" + bugid)

    regexp_title = re.compile(r'<title>Cisco Bug: .{13}([\S\s]*?)</title>', re.MULTILINE)
    result_title = re.findall(regexp_title, page_load_result.text)
    final = []
    if not result_title:
        final.insert(0, " - No information available externally")
    else:
        final = list(filter(None, result_title))
    return final[0]


def list_to_lines(list_source):
    return '\n'.join(str(p) for p in list_source)


def get_google_results(user_input):
    regexp_search = re.compile(r'(?=CSC[\S\s]).{10}', re.MULTILINE)
    a = search("""Cisco Bug """ + user_input, num_results=100)
    answer = re.findall(regexp_search, list_to_lines(a))
    if answer:
        # answer.insert(0, "*Possible bugs for your request* : ")
        print(answer)  # for debugging purposes #TODO:remove
    else:
        answer.insert(0, "Nothing found, please be more exact")
    return answer[:20]


def get_defect_full_description(defect_id):
    page = requests.get("https://quickview.cloudapps.cisco.com/quickview/bug/" + defect_id)
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
    return result_full


api.add_resource(DefectResource, "/bug/<string:description_text>")
app.run(host='0.0.0.0', debug=True)
