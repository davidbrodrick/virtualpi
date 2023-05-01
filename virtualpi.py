#!/usr/bin/python3

#NB: The following environment variables need to be set:
# export OPENAI_API_KEY="sk-M...M"
# export SLACK_APP_TOKEN="xapp-1...d"
# export SLACK_BOT_TOKEN="xoxb-2...C"
#See the README for more information: 

import sys, os, pickle, glob
from paperqa import Docs
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

#Create Slack app handle
app = App(token=os.environ["SLACK_BOT_TOKEN"])

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
    print("Requires the path to a repository of PDFs as an argument.")
    sys.exit(1)
PAPERDIR=sys.argv[1]
if not os.path.exists(PAPERDIR):
    print("The specified directory does not exist.")
    sys.exit(1)

try:
    #Load the pre-pickled document vector if it exists
    with open("%s/docs.pkl"%PAPERDIR, "rb") as f:
        docs = pickle.load(f)
    print("Loaded previous state from %s/docs.pkl"%PAPERDIR)
    print(" - remove this file if you change the set of PDFs\n")
except:
    #Couldn't load a pre-picked version
    papers=[]
    filesfound=glob.glob("%s/*"%PAPERDIR)
    for p in filesfound:
        if p.lower().endswith(".pdf"):
            papers.append(p)

    if not papers:
        print("No PDFs were found in the specified directory.")
        sys.exit(1)

    print("Found %d PDFs in %s"%(len(papers),PAPERDIR))

    #Add each paper in turn to paper-qa/FAISS     
    docs = Docs(llm='gpt-3.5-turbo', summary_llm="davinci")
    for p in papers:
        print("Embedding %s .."%p)
        docs.add(p, citation=p, key=p)
    try:
        with open("%s/docs.pkl"%PAPERDIR, "wb") as f:
            #Save this state for next time
            pickle.dump(docs, f)
    except:
        Print("Couldn't save state into %s - is it writeable?"%PAPERDIR)

#Set up the Slack interface to start servicing requests
print("Starting Slack handler - bot is ready to answer your questions!")
SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"]).start()