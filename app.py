
from flask import Flask
from flask import request
from flask import json

import processor

app = Flask(__name__)

"""
URI scheme:
ex:http://localhost:5000/get_tel?auth=gUbVdmDVN5fwuZxHQmVK&string=C1|C43|C23|A-&user_id=0&surveySessionID=0&currentScreen&mrn=0
string(required) = Tell string to be evaluated
user_id(optional) = optional user_id to be evaluated. If None send '0' or leave out.
surveysession_id(optional) = optional surveysession_id to be avaluated. If None send '0' or leave out.
currentScreen = optional currentScreen to be avaluated. If None send '0' or leave out.
mrn = optional medical record number to be avaluated. If None send '0' or leave out.
Error: 1 = Invalid Tel string format
"""


@app.route('/get_tel', methods=['GET'])
def tel_API(
        auth="",
        string="",
        user_id="",
        surveySessionID="",
        surveyScreenID="",
        currentScreen="",
        mrn="",
        varName="",
        database_name="",
        param=""):
    auth = request.args.get('auth', auth)
    if auth != 'gUbVdmDVN5fwuZxHQmVK':
        return 'URI must contain valid authorization key'
    else:
        tel_string = request.args.get(
            'string',
            string
            )
        user_id = request.args.get(
            'user_id',
            user_id
            )
        surveySessionID = request.args.get(
            'surveySessionID',
            surveySessionID
            )
        surveyScreenID = request.args.get(
            'surveyScreenID',
            surveyScreenID
            )
        currentScreen = request.args.get(
            'currentScreen',
            currentScreen
            )
        mrn = request.args.get(
            'mrn',
            mrn
            )
        varName = request.args.get(
            'varName',
            varName
            )
        database_name = request.args.get(
            'database_name',
            database_name
            )
        param = request.args.get(
            'param',
            param
            )
        tel_string_evaluated = processor.tel_evaluate(tel_string)
        if tel_string.startswith("C"):
            return json.dumps(tel_string_evaluated)
        if tel_string.startswith('['):
            tel_string_evaluated = processor.is_simple_tel(tel_string)
            return json.dumps(tel_string_evaluated)
        else:
            return 'Error: 1 (string)'


def user_id(user_id=""):
    user_id = request.args.get(
                    'user_id',
                    user_id
                    )
    return user_id


def surveySessionID(surveySessionID=""):
    surveySessionID = request.args.get(
                    'surveySessionID',
                    surveySessionID
                    )
    return surveySessionID


def surveyScreenID(surveyScreenID=""):
    surveyScreenID = request.args.get(
                    'surveyScreenID',
                    surveyScreenID
                    )
    return surveyScreenID


def currentScreen(currentScreen=""):
    currentScreen = request.args.get(
            'currentScreen',
            currentScreen
            )
    return currentScreen


def mrn(mrn=""):
    varName = request.args.get(
        'mrn',
        mrn
        )
    return mrn


def varName(varName=""):
    varName = request.args.get(
        'varName',
        varName
        )
    return varName


def database_name(database_name=""):
    database_name = request.args.get(
        'database_name',
        database_name
        )
    return database_name


def param(param=""):
    param = request.args.get(
        'param',
        param
        )
    return param


if __name__ == '__main__':
    app.run(debug=True)
