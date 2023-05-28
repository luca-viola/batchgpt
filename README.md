# BATCHGPT

BATCHGPT is a quick and easy command line utility to use chatgpt in scripts, mainly for text transformationtask, or for 
applying prompts to groups of line in a file for batch processing avoid context token limitations.
```
$ batchgpt.py -h
usage: batchgpt.py [-h] [-i FILENAME] [-l LINES] [-1] [-f PROMPT_FILE] [-k KEY] [-r ROLE]
                   [-p PROMPT] [-m MODEL] [-o NEW_FILENAME] [--list-models] [-t TEMPERATURE]

Process a file applying a prompt to batches of lines

options:
  -h, --help       show this help message and exit
  -i FILENAME      input file name
  -l LINES         number of lines in a chunk
  -1               Read the whole file in one go
  -f PROMPT_FILE   path to the prompt file
  -k KEY           Openai Key
  -r ROLE          the system role string
  -p PROMPT        the prompt for chatgpt
  -m MODEL         the model used by chatgpt (default=gpt-3.5-turbo)
  -o NEW_FILENAME  the output file (default: filename.out)
  --list-models    list the supported models
  -t TEMPERATURE   how deterministic will answers be, 0=max determinism
```

The script supports different models for the engine:
```
$ batchgpt.py --list-models
Supported models:
  gpt-4
  gpt-4-32k
* gpt-3.5-turbo
  text-davinci-003
  text-davinci-002
  code-davinci-002
```

As an example. running it like:

```
batchgpt.py -i myfile.csv 
     -l 5 
     -p "Hey Chatgpt, I have here some lines of text, each line is terminated by a new 
         line and may or may be not enclosed in double quotes. Find a categorization for 
         each line so I will be able to cluster them, use 3 words max in english for the
         category, do not add any explanation and PROCESS ALL THE LINES. Output will be
         in csv format with two fields: 
           <category> TAB CHARACTER <line translated in english>. 
         Here are the lines:"
     -m gpt-4    
     -r "you are a helpful assistant that translates sentences in english and classifies
         them"
```
will produce a CSV file with an inferred categorization and a translation of the sentences
in english, in groups of 5 lines at a time.

You can specify the prompt externally and make it operate on a file, you can basically craft
whatever text transformation you want in natural language.

the parameter `-l LINES` specifies how many lines of text you can process from the file at a time,
more than 5-6 sometimes breaks the number of maximum tokens allowed (4096 with gpt-3.5-turbo model).

This could be less of a problem wih the model gpt4, that can support up to 8k tokens, or gpt-4-32k 
which can support up to 32k token. 

There is a file called `config.ini` where you can put the prompt, the api key, the number of lines,
and how random you want the model to be (temperature: at 0 it means multiple requests will most
likely give the same answers).
The config.ini allows you to fix some parameters to avoid having to repeat them in the command line.

```
[main]
lines = 5
key =
model = gpt-3.5-turbo
prompt = 
role = 
temperature = 0.2
```

If you specify any parameter on the command line (-p, -k, -t etc) it will **always override** the
config file values.

You can put prompts in a file and pass that file to batchgpt (so you can create different prompts
for different use cases), using the `-f PROMPT_FILE` option.

The output will be in a file called filename.out, or you can specify it with the `-o NEW_FILENAME`
option 