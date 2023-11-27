# Importing the required modules
from dataclasses import dataclass
from typing import Union, List, Optional, assert_never
import re
import argparse


# Defining the Result Union type
@dataclass
class Ok:
    value: any

    def __repr__(self):
        return self.value


@dataclass
class Err:
    error: str

    def __str__(self):
        return "ERROR: " + self.error


# What? - An object of type Result can either be an Ok or Err type.
# Why? - I like to define a Result type to handle
# whether a function returns a value or an error.
Result = Union[Ok, Err]


# Defining the Utterance Union type
@dataclass
class Word:
    word: str

    def __str__(self):
        return f"{self.word}"


@dataclass
class Punctuation:
    symbol: str
    # Is . or ! or ? or ,
    isHard: bool

    def __str__(self):
        return f"{self.symbol}"


@dataclass
class Pause:
    duration: float


# An Utterance can either be a Word OR Punctuation OR Pause
Utterance = Union[Word, Punctuation, Pause]


# Defining the Subject dataclass
@dataclass
class Line:
    speaker: str
    utterances: List[Utterance]


# Defining the transcript
transcript = """
            A: Hello! Hello! Who is this? Nice, it's nice to see you.

            B: And who are you? and -

            F: What? <2.5> What did you say?? Hello??

            ALPH: Back to me!!

            B: Where??
"""

# Defining the regex pattern for tokenizing the transcript
# https://regex101.com/r/gs5Y38/1
pattern = re.compile(
    r"""
(?P<speaker>[a-zA-Z]+)(?=:)|
(?<=<)(?P<pause>\d\.?\d*)(?=>)|
(?P<word>\w+)(?!:)|
(?P<puncHard>[.?!,])|
(?P<puncSoft>['\-\"])
    """,
    re.VERBOSE,
)


# Defining the function that returns a linked-list of Subject types
def parse_transcript(transcript: str) -> Result:
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
                if args.verbose:
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

            case "word":
                if args.verbose:
                    print(f"Appending {m.group()} to {speaker}")
                utteranceList.append(Word(m.group()))
            case "puncHard":
                if args.verbose:
                    print(f"Appending {m.group()} to {speaker}")
                utteranceList.append(Punctuation(m.group(), True))
            case "puncSoft":
                if args.verbose:
                    print(f"Appending {m.group()} to {speaker}")
                utteranceList.append(Punctuation(m.group(), False))
            case "pause":
                if args.verbose:
                    print(f"Appending {m.group()} to {speaker}")
                utteranceList.append(Pause(float(m.group())))

    # Check if the subjects list is not empty
    if len(lineList) != 0:
        # Return the subjects list in an Ok wrapper
        # Flush last line
        aLine = Line(speaker, utteranceList.copy())
        lineList.append(aLine)
        return Ok(lineList)
    else:
        # Return an error message in a Err wrapper
        return Err("No subjects found in the transcript.")


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
                    # If hard punc before word, add a space before word
                    if isinstance(lastUtter, Punctuation) and lastUtter.isHard:
                        text += f" {word}"
                    # If word before this word, add a space before this word
                    elif isinstance(lastUtter, Word):
                        text += f" {word}"
                    # Otherwise do nothing
                    else:
                        text += f"{word}"
                case Punctuation(symbol):
                    text += f"{symbol}"
                case Pause(duration):
                    text += f" <{duration}> "
            lastUtter = utterance
        text += "\n"
        lastUtter = line
    return text


parser = argparse.ArgumentParser(
    prog="tulk.py",
    description="Interprets transcripted logs between multiple parties!",
)

# parser.add_argument('filename(s)')# positional argument
parser.add_argument("-v", "--verbose", action="store_true")  # on/off flag
parser.add_argument("-t", "--tests", action="store_true")  # test all methods and exit
args = parser.parse_args()

if __name__ == "__main__":
    if args.tests:
        # Test the functions
        result = parse_transcript(transcript)
        if isinstance(result, Ok):
            print(subjects_to_str(result.value))
        else:
            print(result)
        exit()
