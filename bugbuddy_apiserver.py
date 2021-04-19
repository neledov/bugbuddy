#!/usr/bin/env python
# -*- coding: utf8 -*-

import re
import requests
from google import google
from flask import Flask, jsonify
from flask_restful import Api, Resource, reqparse

app = Flask(__name__)
api = Api(app)


class bug(Resource):
    def get(self, description_text):
        description_text = description_text.replace('description_text=', '')
        a = findingoogle(description_text.replace('%20', '* '))
        a = list(dict.fromkeys(a))
        my_new_list = [
            '[' + x + "](" + "https://quickview.cloudapps.cisco.com/quickview/bug/" + x + ") : " + gettitle(x) + '&#13;'
            for x in a]
        return jsonify(my_new_list)


def gettitle(bugid):
    page = requests.get("https://quickview.cloudapps.cisco.com/quickview/bug/" + bugid)

    retitle = re.compile(r'<title>Cisco Bug: .{13}([\S\s]*?)</title>', re.MULTILINE)
    title = re.findall(retitle, page.text)
    final = []
    if not title:
        final.insert(0, " - No information avaliable externally")
    else:
        final = list(filter(None, title))
    return final[0]


def fstr(sourcelist):
    return '\n'.join(str(p) for p in sourcelist)


def findingoogle(usertext):
    search = re.compile(r'(?=CSC[\S\s]).{10}', re.MULTILINE)
    a = google.search("""Cisco Bug """ + usertext, 5)
    answer = re.findall(search, fstr(a))
    if answer:
        ##answer.insert(0, "*Possible bugs for your request* : ")
        print(answer)
    else:
        answer.insert(0, "Nothing found, please be more exact")
    return answer[:10]


def getdescr(bugid):
    page = requests.get("https://quickview.cloudapps.cisco.com/quickview/bug/" + bugid)
    retitle = re.compile(r'<title>Cisco Bug: ([\S\s]*?)</title>', re.MULTILINE)
    resymptom = re.compile(r'<B>Symptom:</B>([\S\s]*?)<B>Conditions:</B>', re.MULTILINE)
    recondition = re.compile(r'<B>Conditions:</B>([\S\s]*?)</pre>', re.MULTILINE)
    symptom = re.findall(resymptom, page.text)
    condition = re.findall(recondition, page.text)
    title = re.findall(retitle, page.text)
    final = []
    if not symptom:
        final.insert(0, "No information avaliable")
    else:
        symptom.insert(0, "Title : " + title[0])
        symptom.insert(1, "Quickview URL : https://quickview.cloudapps.cisco.com/quickview/bug/" + bugid)
        symptom.insert(2,
                       "Symptoms of " + bugid + " :")

        condition.insert(0, "Condition :")
        result = symptom + condition
        final = list(filter(None, result))
    return final


api.add_resource(bug, "/bug/<string:description_text>")
app.run(host='0.0.0.0', debug=True)
