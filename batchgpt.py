#!/usr/bin/env python3
import os
import sys
import time
import openai
import logging
import argparse
import itertools
import configparser

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s')

MODELS = [
    "gpt-4",
    "gpt-4-32k",
    "gpt-3.5-turbo",
    "text-davinci-003",
    "text-davinci-002",
    "code-davinci-002"
]

def get_max_lines(filename):
    with open(filename, 'r') as f:
        data = f.read().strip()
        segments = data.split('\n')
        return len(segments)


def read_file_in_chunks(file_path, chunk_size):
    with open(file_path, 'r') as file:
        while True:
            lines = list(itertools.islice(file, chunk_size))
            if not lines:
                break
            yield lines

def chunk_csv_file(filename, chunk_size, prompt_template, role, temperature, model_engine, new_filename):
    # Get the maximum number of segments in the SRT file
    max_segments = get_max_lines(filename)
    # Calculate the number of chunks
    num_chunks = (max_segments // chunk_size) + (1 if max_segments % chunk_size > 0 else 0)
    name, ext = os.path.splitext(filename)
    if new_filename == "":
      new_filename = f"{name}.out"
    # Loop through each chunk
    with open(new_filename, 'w') as srtfile:
      i = 0
      for chunk in read_file_in_chunks(filename, chunk_size):
        prompt = prompt_template
        logging.info(f"Chunk #{i}/{num_chunks}")
        prompt = prompt.format(chunk=chunk)

        message = [
          {"role": "system", "content": role},
          {"role": "user", "content": prompt}
        ]
        # Generate a response
        while True:
            try:
                completion = openai.ChatCompletion.create(
                  model=model_engine,
                  messages=message,
                  temperature=temperature,
                  #max_tokens=1024,
                  #n=1,
                  #stop=None,
                )
            except openai.error.APIError:
                logging.warning(f"API Error, retrying chunk #{i}")
                continue
            except openai.error.RateLimitError:
                logging.warning(f"API Rate Limit Error, retrying chunk #{i}")
                continue
            break
        response = completion.choices[0].message.content
        logging.debug(f"{response}")
        i = i + 1
        srtfile.write(response+"\n\n")
        srtfile.flush()
      srtfile.close()


chunks = 5
prompt = ""
prompt_file = ""
key = ""
role = ""
temperature = 0.0
model = MODELS[2]

config = configparser.ConfigParser()
config.read('config.ini')
chunks = int(config.getint('main', 'chunks'))
prompt = config.get('main', 'prompt').replace('\\n', '\n')
role = config.get('main', 'role')
temperature = float(config.get('main', 'temperature'))
key = config.get('main', 'key')
model = config.get('main', 'model')

# create the argument parser
parser = argparse.ArgumentParser(description='Process a file applying a prompt to batches of lines')

parser.add_argument('-i', dest='filename', help='input file name')
parser.add_argument('-c', dest='chunks', help='number of chunks', type=int, default=chunks)
parser.add_argument('-f', dest='prompt_file', help='path to the prompt file', default='default.pmt')
parser.add_argument('-k', dest='key', help='Openai Key', default=key)
parser.add_argument('-r', dest='role', help='the system role string', default=role)
parser.add_argument('-p', dest='prompt', help='the prompt for chatgpt', default=prompt)
parser.add_argument('-m', dest='model', help='the model used by chatgpt (default=gpt-3.5-turbo)', default=model)
parser.add_argument('-o', dest='new_filename', help='the output file (default: filename.out)', default='')
parser.add_argument('--list-models', help='list the supported models', action='store_true')
parser.add_argument('-t', dest='temperature', help='how deterministic will answers be, 0=max determinism', type=float, default=temperature)
args = parser.parse_args()

filename = args.filename
chunks = args.chunks
prompt_file = args.prompt_file
key = args.key
role = args.role
prompt = args.prompt
temperature = args.temperature
new_filename = args.new_filename
model = args.model

if model not in MODELS:
    print("This model is unknown/not supported. List supported ones with --list-models")
    sys.exit(0)

if args.list_models:
  print("Supported models:")
  for s in MODELS:
    if s == model:
      print("* " + s)
    else:
      print("  "+s)
  sys.exit(0)

if not filename:
    print("Specify a file with the -i /PATH/TO/FILE option")
    sys.exit(1)

if key == "":
    logging.error("Please set an OpenAI API key in config.ini (key =..) or with -k option")
    logging.error("Aborted.")
    sys.exit(1)

openai.api_key = key

if prompt == "":
  try:
    with open(prompt_file, 'r') as file:
      prompt = file.read()
  except Exception as e:
      logging.error("Please set a prompt in the config.ini (prompt =...), with -p option, in a default.pmt file or in a")
      logging.error("file specified with the -f option")
      logging.error("Aborted.")
      sys.exit(1)


csv_filename = args.filename

start_time = time.time()

# check if the command succeeded
logging.info("Translating CSV tickets from PT to EN and tagging them")
chunk_csv_file(csv_filename, chunks, prompt, role, temperature, model, new_filename)
end_time = time.time()
elapsed_time = end_time - start_time
logging.info(f"Operation completed in {elapsed_time} seconds.")
