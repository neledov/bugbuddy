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
    def get(self, input_search_string):
        input_sanitized = list(dict.fromkeys(get_google_results(input_search_string.replace('%20', '* '))))
        list_final = [
            '[' + x + "](" + "https://quickview.cloudapps.cisco.com/quickview/bug/" + x + ") : " + get_defect_title(
                x) + '&#13;'
            for x in input_sanitized]
        return jsonify(list_final)


class InfoResource(Resource):
    def get(self, defect_id):
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


def get_defect_title(defect_id):
    page_load_result = requests.get("https://quickview.cloudapps.cisco.com/quickview/bug/" + defect_id)

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
    result_search = search("""Cisco Bug """ + user_input, num_results=100)
    result_final = re.findall(regexp_search, list_to_lines(result_search))
    if not result_final:
        result_final.insert(0, "Nothing found, please be more exact")
    return result_final[:50]


api.add_resource(DefectResource, "/defect/<string:input_search_string>")
api.add_resource(InfoResource, "/defect/info/<string:defect_id>")
app.run(host='0.0.0.0', debug=True)
