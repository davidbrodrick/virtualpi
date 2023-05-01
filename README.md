# Virtual PI

This script reads all of the PDFs in a directory, and uses a Large Language Model to make the document content available for answering natural language prompts, via Slack.

The script is trivial.. it just stands on the shoulders of giants such as [PaperQA](https://github.com/whitead/paper-qa/), [OpenAI Embeddings](https://platform.openai.com/docs/guides/embeddings), [FAISS](https://github.com/facebookresearch/faiss), [langchain](https://github.com/hwchase17/langchain), and [Slack Bolt](https://slack.dev/bolt-python/concepts).

Why the name? When your Principal Investigator goes on holidays, you need a *Virtual PI* to answer your difficult questions!

## Configuration

To run the script, you require:
  * A directory with the PDFs you wish the expert system to ingest;
  * A working Python3 environment with the following packages available:
    * `pip3 install slack_bolt paper-qa==1.2`
    * NB: At the time of writing the default pip version of paper-qa and its langchain dependency are out of sync, hence requesting version 1.2.
  * An OpenAI [API key](https://help.openai.com/en/articles/4936850-where-do-i-find-my-secret-api-key).
  * You'll need to [create a new Slack app](https://api.slack.com/authentication/basics) to generate the API keys needed for Slack:
    * Click 'Create New App'.
    * Select 'From Scratch'.
    * Assign a name and select the Slack workspace you will use the app with.
    * Select the 'Enable Socket Mode' option and enable this feature via the permissions slider.
    * It only needs the 'connections:write' and 'app_mentions:read' permission scopes, then you can 'Generate' the token.   
    * Save this token - you'll need it in the environment at runtime.
    * NB: You'll also need to go to the 'Event Subscriptions' page and enable events using the permissions slider.
    * Under 'Subscribe to Bot Events' heading add the 'app_mention' permission.
    * Then you need a 'Bot Token' with scope to read and write messages - click on the 'OAuth & Permissions' button on the left of the Slack app website.
    * Under 'Bot Token Scopes' add `chat::write` and `app_mention` permission.
    * Then at the top of the page select the green 'Install to Workspace' button.
    * After you approve the installation, you will be given a 'Bot User OAuth Token', which you will also need in the environment at runtime.

The three API tokens you have generated should be exported to your shell environment at runtime:

```
export OPENAI_API_KEY="sk-M...M"
export SLACK_APP_TOKEN="xapp-1...d"
export SLACK_BOT_TOKEN="xoxb-2...C"
```

Then you can start the app as follows.

`python3 virtualpi.py /path/to/your/PDF/directory/`

## Saving State

When the script starts it will check if a pickled version of the dense vector containing the documents is already available in the PDF directory. If found it will use that existing state (which saves time and the cost of API calls), otherwise it will parse the PDFs, embed them into the FAISS dense vector and then save this state for next time.

NB: If you add/remove PDFs you will need to remove the state file!

`rm /path/to/your/PDF/directory/docs.pkl`

## Add to Slack Workspace

By now your app should be happily running. The final step is to actually add it to your Slack workspace.

  * In Slack, Click the '... More' on the top left.
  * Select 'Apps'.
  * Select the new app you created above.
  * Then go to a Slack channel and tag the app with a question e.g. `@WhatYouCalledYourApp what is the meaning of this?`
