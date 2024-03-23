

from flask import Flask,render_template,request
from bs4 import BeautifulSoup
from flask import session
import requests
import gspread
from flask import request
import pandas as pd
import random
from markupsafe import escape
app = Flask(__name__)
@app.before_request
def setup():
    global word_list, chinese, English,getHTML
    wordUrl = "https://wecan.tw/index.php/2018-12-02-08-34-31/2019-01-03-18-18-31/2000-basic-vocabulary"
    response = requests.get(wordUrl)
    response.encoding = 'utf-8'
    soup = BeautifulSoup(response.text, 'html.parser')
    table = soup.select_one('table')
    wordlist = table.select('tr')
    word_list = []

    for word_row in wordlist:
        cleaned_word = word_row.text.replace(u'\xa0', u'')
        word_list.append(cleaned_word)

    del word_list[0]
    import re
    chinese=[]
    chinese_0=[]

    for k in range (len(word_list)):
        word_list[k] = word_list[k].replace('[', '【')
        word_list[k] = word_list[k].replace(']', '】')

    for k in range (len(word_list)):
        a=str(word_list[k])
        en_letter = '[\u0041-\u005a|\u0061-\u007a]+' 
        zh_char = '[\u4e00-\u9fa5\u3000-\u303F]+' 
        chinese.append(re.findall(zh_char,a))
        English=[]
        for k in range (len(word_list)):
            a=str(word_list[k])
            en_letter = '[\u0041-\u005a|\u0061-\u007a]+' 
            English.append(re.findall(en_letter,a))

    def getHTML(url):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36'
        }
        req = requests.get(url, headers=headers)
        return req.content
        
    
       
@app.route("/")
def index():  
    return render_template('index.html')
           


@app.route("/win")
def win():
    
    return render_template('win.html',English_example=English_example)


@app.route("/lose")
def lose():
    
    return render_template('lose.html',English_example=English_example)

@app.route("/English_Test")
def English_Test():
    global word_list, chinese, English ,English_example
    English_example = ""
    number = random.randint(0, len(word_list) - 1)
    Ques = f"{English[number][0]}?"
    options = [chinese[number][0:]]
    while len(options) < 4:
        random_option = random.choice(chinese)
        if random_option not in options:
            options.append(random_option)
            random.shuffle(options)
    output_string = options
    An = str(chinese[number][0])
    a = str(output_string[0][0])
    b = str(output_string[1][0])
    c = str(output_string[2][0])
    d = str(output_string[3][0])
    Score = 0
    soup = BeautifulSoup(
        getHTML("https://dictionary.cambridge.org/zht/%E8%A9%9E%E5%85%B8/%E8%8B%B1%E8%AA%9E-%E6%BC%A2%E8%AA%9E-%E7%B9%81%E9%AB%94/" + Ques))
    if soup.select('.def.ddef_d.db'):
        example = soup.select_one('.examp.dexamp')
        if example:
            English_example = example.text
        else:
            print("No example found for the word.")
    else:
        print("No definition found for the word.")
    return render_template('English_Test.html', a=a, b=b, c=c, d=d, Ques=Ques, An=An, Score=Score)

    

@app.route("/Game")
def Game():
    global data, Explaination
    client = gspread.service_account(filename='prefixsuffix.json')
    working_sheet = client.open('prefixsuffix')
    if data is None:
        return "Data not provided"
    else:
        sheet = working_sheet.worksheet(data)
    records = list(sheet.get_all_records())
    Queslist = []  
    for i in records:
        Queslist.append(i)  
    prefix_list = [record['字首/字根'] for record in Queslist]
    chinese2 = [record['中文'] for record in Queslist]
    explain2 = [record['意義'] for record in Queslist]
    question2 = [record['例字'] for record in Queslist]
    number = random.randint(0, len(prefix_list) - 1)
    Ques2 = f"{question2[number]}?"
    options = [chinese2[number]]
    while len(options) < 4:
        random_option = random.choice(chinese2)
        if random_option not in options:
            options.append(random_option)
            random.shuffle(options)
    output_string = options
    Explaination = str(prefix_list[number] + explain2[number])
    An = str(chinese2[number])
    a = str(output_string[0])
    b = str(output_string[1])
    c = str(output_string[2])
    d = str(output_string[3])
    
    return render_template("Game.html", a=a, b=b, c=c, d=d, Ques2=Ques2, An=An)


@app.route("/choosetopic", methods=["GET", "POST"])
def choosetopic():
    global data, score
    data = None
    score = None
    if request.method == "POST":
        data = request.form.get("data")
        score = request.form.get("score") 
    else:
        print("Not found")
    return render_template('choosetopic.html', data=data, score=score)



@app.route("/winGame")
def winGame():
    return render_template('winGame.html', Explaination=Explaination)


@app.route("/loseGame", methods=["GET", "POST"])
def loseGame():
    if request.method == "POST":
        data = request.form.get("data")
        score = request.form.get("score") 
        return render_template('loseGame.html', Explaination=Explaination, data=data, score=score)
    else:
        print("Not found")
        return render_template('loseGame.html', Explaination=Explaination,data=None,score=None)




if __name__=='__main__':
    app.run(debug=True,host='0.0.0.0',port=3000)