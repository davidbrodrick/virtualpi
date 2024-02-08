#!/usr/bin/python3
#
#NB: The following environment variables need to be set:
# export OPENAI_API_KEY="sk-M...M"
# export SLACK_APP_TOKEN="xapp-1...d"
# export SLACK_BOT_TOKEN="xoxb-2...C"
#See the README for more information:
#https://github.com/davidbrodrick/virtualpi/blob/main/README.md
#
#David Brodrick, 2023

import sys, os, pickle, glob
from paperqa import Docs
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from openai import AsyncOpenAI
from tqdm import tqdm
chat = AsyncOpenAI()

#Create handle to Slack
app = App(token=os.environ["SLACK_BOT_TOKEN"])

############################################################
#This function is called when a Slack user mentions the bot
@app.event("app_mention")
def event_test(say, body):
    print("received question, working on answer.")
    try:
        #This gets the question text from the user
        user_question=body["event"]["blocks"][0]["elements"][0]["elements"][1]["text"]
        if user_question:
            #Do the paper-qa query and get the answer to the question
            answer = docs.query(user_question, k=30, max_sources=10)
            #Print some stuff locally
            print(answer.formatted_answer)
            print("\n\n\n")
            #Send the (minimal) answer to Slack
            say(answer.answer)
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
        docs = pickle.loads(pickle.load(f))
    docs.set_client(chat)
    print("Loaded previous state from %s/docs.pkl"%PAPERDIR)
    print(" - remove this file if you change the set of PDFs\n")
except FileNotFoundError:
    docs = None

if docs is None:
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

    #Add each paper in turn to paper-qa/FAISS/OpenAI embedding     
    docs = Docs(llm="gpt-3.5-turbo",client=chat)
    print("Embedding documents")
    pbar = tqdm(papers,leave=True,desc="")
    for p in pbar:
        try:
            #Get the base file name to use as the citation
            citation=os.path.split(p)[-1]
            citation=citation[0:citation.rfind(".")]
            #Embed this doc
            pbar.set_description(f"doc={citation:s}")
            docs.add(p,docname=citation,citation=citation)
        except Exception as e:
            print("Error processing %s: %s"%(p,e))
    try:
        with open("%s/docs.pkl"%PAPERDIR, "wb") as f:
            #Save this state for next time
            print("\nSaving state to file %s/docs.pkl - this may take some time."%PAPERDIR)
            pickle.dump(pickle.dumps(docs), f)
    except Exception as e:
        print("Couldn't save state into %s - is it writeable?"%PAPERDIR)
        print("Error was: %s"%e)
        sys.exit(2)

docs.prompts.qa = ("Write an answer ({answer_length}) "
    "for the question below based on the provided context. "
    "If the context provides insufficient information, "
    'reply "I cannot answer". '
    "For each part of your answer, indicate which sources most support it "
    "via valid citation markers at the end of sentences, like (Example2012). "
    "Answer in an unbiased, comprehensive, and scholarly tone. "
    "If the question is subjective, provide an opinionated answer in the concluding 1-2 sentences. "
    "Use Markdown for formatting code or text, and try to use direct quotes to support arguments.\n\n"
    "{context}\n"
    "Question: {question}\n"
    "Answer: ")

#Set up the Slack interface to start servicing requests
print("Starting Slack handler - bot is ready to answer your questions!")
SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"]).start()
