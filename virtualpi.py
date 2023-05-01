#!/usr/bin/python3

#The following environment variables need to be set:
#
#

#Imports - pip3 install paper
import sys, os, pickle
from paperqa import Docs
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

############################################################
#This function is called when a Slack user mentions the bot
@app.event("app_mention")
def event_test(say, body):
    try:
        #This gets the question text from the user
        user_question=body["event"]["blocks"][0]["elements"][0]["elements"][1]["text"]
        if user_question:
            #Do the paper-qa query and get the answer to the question
            answer = docs.query(user_question, k=30, max_sources=10)
            #Print some stuff locally
            print(answer.formatted_answer)
            for p in answer.passages:
                print("* %s: %s\n"%(p, answer.passages[p]))
            print("\n\n\n")
            #Send the answer to Slack
            say(answer.formatted_answer)
    except Exception as e:
        print("Error: %s"%e)

############################################################
#Main/program start point

#We require a directory containing PDFs as an argument
if len(sys.argv)!=2:
    raise ValueError("Requires the path to a repository of PDFs as an argument.")
PAPERDIR=sys.argv[1]

try:
    # load
    with open("my_docs.pkl", "rb") as f:
        docs = pickle.load(f)    
except:
    #save    
    docs = Docs(llm='gpt-3.5-turbo', summary_llm="davinci")
    for p in papers:
        docs.add(PAPERDIR+p, citation=p, key=p) #, chunk_chars=2500)
    with open("my_docs.pkl", "wb") as f:
        pickle.dump(docs, f)

# Install the Slack app and get xoxb- token in advance
app = App(token=os.environ["SLACK_BOT_TOKEN"])

SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"]).start()