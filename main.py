import boto3
from botocore.exceptions import BotoCoreError, ClientError
from contextlib import closing
import os
import sys
import subprocess
from tempfile import gettempdir
from PyPDF2 import PdfReader

# creating a pdf reader
reader = PdfReader('text.pdf')

first_page = reader.pages[0]

text = first_page.extract_text()

print(f"Text length is {len(text)}")

if len(text) > 1500:
    text = text[:1500]

polly = boto3.client('polly')

try:
    response = polly.synthesize_speech(Text=text, Engine="neural", OutputFormat="mp3", VoiceId="Olivia")
except (BotoCoreError, ClientError) as error:
    print(error)
    sys.exit(-1)

if "AudioStream" in response:
    with closing(response["AudioStream"]) as stream:
        output = os.path.join(gettempdir(), "speech.mp3")
        try:
            with open(output, "wb") as file:
                file.write(stream.read())
        except IOError as error:
            print(error)
            sys.exit(-1)
else:
    print("Could not stream audio")
    sys.exit(-1)

if sys.platform == "win32":
    os.startfile(output)
else:
    opener = "open" if sys.platform == "darwin" else "xg-open"
    subprocess.call([opener, output])
