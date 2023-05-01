# Virtual PI

This script reads all of the PDFs in a directory, and uses a Large Language Model to make the document content available for answering natural language prompts provided via Slack.

The script is trivial as it stands on the shoulders of giants such as [PaperQA](https://github.com/whitead/paper-qa/), [OpenAI Embeddings](https://platform.openai.com/docs/guides/embeddings), [FAISS](https://github.com/facebookresearch/faiss), [langchain](https://github.com/hwchase17/langchain), and [Slack Bolt](https://slack.dev/bolt-python/concepts).

Why the name? When your Principal Investigator goes on holidays, you need a Virtual PI!

## Configuration

To run the script, you require:
  * A directory with the PDFs you wish the expert system to ingest;
  * A working Python3 environment with the following packages available:
    * pip3 install slack_bolt paperqa
  * An OpenAI [API key](https://help.openai.com/en/articles/4936850-where-do-i-find-my-secret-api-key)
  * TBC.. maybe you need to [create a new Slack app](https://api.slack.com/authentication/basics) rather than use mine..

These tokens should be exported to your shell environment:

{{{
    export OPENAI_API_KEY="sk-M...M"
    export SLACK_APP_TOKEN="xapp-1...d"
    export SLACK_BOT_TOKEN="xoxb-2...C"
}}}

Then you can start the app as follows.

{{{
    python3 virtualpi.py /path/to/your/PDF/directory/
}}}

## Saving State

When the script starts it will check if a pickled version of the dense vector containing the documents is already available. If found it will use that existing state (which saves time and the cost of API calls), otherwise it will parse the PDFs, embed them into the FAISS dense vector and then save this state for next time.

NB: If you add/remove PDFs you will need to remove the state file!

{{{
    rm fsdsddfs
}}}

## Add to Slack Workspace