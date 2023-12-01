# Importing the required modules
from dataclasses import dataclass
from typing import Union, List, Optional, assert_never
from collections import defaultdict
import os
import re
import argparse


# Defining the Utterance Union type
@dataclass
class Word:
    word: str

    def __str__(self):
        return f"{self.word}"


@dataclass
class Pause:
    duration: float


# If symbol ends a sentence: ! or ? or .
@dataclass
class PunctuationHard:
    symbol: str

    def __str__(self):
        return f"{self.symbol}"


@dataclass
class PunctuationSoft:
    symbol: str

    def __str__(self):
        return f"{self.symbol}"


Punctuation = Union[PunctuationHard, PunctuationSoft]

# An Utterance can either be a Word OR Punctuation OR Pause
Utterance = Union[Word, Punctuation, Pause]


# Defining the Subject dataclass
@dataclass
class Line:
    speaker: str
    utterances: List[Utterance]


# Defining the function that returns a linked-list of Subject types
def parse_transcript(transcript: str) -> List[Line]:
    # default verbose
    # check if running from main or import
    if "args" not in globals():
        verbose = False
    else:
        verbose = args.verbose
    # Defining the regex pattern for tokenizing the transcript
    # https://regex101.com/r/gs5Y38/1
    pattern = re.compile(
        r"""
    (?P<speaker>^[a-zA-Z]+)(?=:)|
    (?P<time>\d{1,2}:\d{1,2})|
    (?<=<)(?P<pause>\d\.?\d*)(?=>)|
    (?P<word>\w+[-'’:+]?\w*)|
    (?P<puncHard>[.?!])|
    (?P<puncSoft>[’'\-\",])
        """,
        re.VERBOSE | re.MULTILINE,
    )

    # Initialize an empty list that should contain only Subject types
    lineList = []

    # Iterate over the matches of the pattern in the transcript
    # for match in pattern.finditer(transcript):
    speaker: str = None
    utteranceList = []
    matches = pattern.finditer(transcript)
    for m in matches:
        match m.lastgroup:
            case "speaker":
                if verbose:
                    print(f"\nSpeaker found: {m.group()}")
                # Set first speaker
                if not speaker:
                    speaker = m.group()
                # Flush otherwise
                else:
                    # Create a Subject instance with the speaker and the utterance list
                    aLine = Line(speaker, utteranceList.copy())
                    utteranceList.clear()

                    # Append the subject to the subjects list
                    lineList.append(aLine)
                    speaker = m.group()
            case "time":
                if verbose:
                    print(f"Appending {m.group()} to {speaker}")

            case "word":
                if verbose:
                    print(f"Appending {m.group()} to {speaker}")
                utteranceList.append(Word(m.group()))
            case "puncHard":
                if verbose:
                    print(f"Appending {m.group()} to {speaker}")
                utteranceList.append(PunctuationHard(m.group()))
            case "puncSoft":
                if verbose:
                    print(f"Appending {m.group()} to {speaker}")
                utteranceList.append(PunctuationSoft(m.group()))
            case "pause":
                if verbose:
                    print(f"Appending {m.group()} to {speaker}")
                utteranceList.append(Pause(float(m.group())))

    # Check if the subjects list is not empty
    if len(lineList) != 0:
        # Return the subjects list in an Ok wrapper
        # Flush last line
        aLine = Line(speaker, utteranceList.copy())
        lineList.append(aLine)
        return lineList
    else:
        # Return an error message in a Err wrapper
        raise Exception("No subjects found in the transcript.")


# Defining the function that prints the Subject linked-list to human-readable text
def subjects_to_str(lines: List) -> str:
    # Initialize an empty string to store the text
    text: str = ""
    lastUtter: Utterance = None

    for line in lines:
        text += f"{line.speaker}: "
        for utterance in line.utterances:
            match utterance:
                case Word(word):
                    # If hard punc before word, add a space before this word
                    if isinstance(lastUtter, PunctuationHard):
                        text += f"{word}"
                    # If comma before word, add a space before this word
                    elif (
                        isinstance(lastUtter, PunctuationSoft)
                        and lastUtter.symbol == ","
                    ):
                        text += f" {word}"
                    # If word before this word, add a space before this word
                    elif isinstance(lastUtter, Word):
                        text += f" {word}"
                    # Otherwise do nothing
                    else:
                        text += f"{word}"
                case PunctuationHard(symbol):
                    text += f"{symbol} "
                case PunctuationSoft(symbol):
                    text += f"{symbol}"
                case Pause(duration):
                    text += f" <{duration}> "
            lastUtter = utterance
        text += "\n"
        lastUtter = line
    return text


# Define function to return a dict of wordCounts, given a speaker
def count_words(lines: Line, targetSpeaker: str) -> dict:
    wordCount = defaultdict(int)
    for line in lines:
        # if guard
        if line.speaker != targetSpeaker:
            continue
        for utterance in line.utterances:
            match utterance:
                case Word(word):
                    # convert word to lower-case and inc word counter
                    wordCount[(word.lower())] += 1
    # cast back to dict
    return dict(wordCount)


if __name__ == "__main__":
    # parse args
    parser = argparse.ArgumentParser(
        prog="tulk.py",
        description="Interprets transcripted logs between multiple parties!",
    )

    # parser.add_argument('filename(s)')# positional argument
    parser.add_argument("-v", "--verbose", action="store_true")  # on/off flag
    parser.add_argument("-c", "--count_words_of", type=str)  # pass in speaker name here
    parser.add_argument("file", type=argparse.FileType("r"), nargs="+")
    args = parser.parse_args()

    # open file(s)
    for infile in args.file:
        # f, e = os.path.splitext(infile)
        # outfile = f + "_formatted" + e
        data = infile.read()
        transcript = parse_transcript(data)
        print(subjects_to_str(transcript))
        s = args.count_words_of
        if s:
            print(count_words(transcript, s))
