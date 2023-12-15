# Importing the required modules
from dataclasses import dataclass
from typing import Union, List, Optional, Generator, Sequence, assert_never
from collections import defaultdict
import os
import sys
import re
import argparse


# Defining the Utterance Union type
@dataclass
class Word:
    word: str

    def __repr__(self):
        return f"{self.word}"


@dataclass
class Pause:
    duration: float

    def __repr__(self):
        return f"<{self.duration}>"


# If symbol ends a sentence: ! or ? or .
@dataclass
class PunctuationHard:
    symbol: str

    def __repr__(self):
        return f"{self.symbol}"


@dataclass
class PunctuationSoft:
    symbol: str

    def __repr__(self):
        return f"{self.symbol}"


Punctuation = Union[PunctuationHard, PunctuationSoft]

# An Utterance can either be a Word OR Punctuation OR Pause
Utterance = Union[Word, Punctuation, Pause]


# Defining the Line dataclass
@dataclass
class Line:
    speaker: str
    utterances: List[Utterance]

    def copy(self):
        return Line(self.speaker, self.utterances.copy())


@dataclass
class Time:
    time: str


Element = Union[Line, Time]


@dataclass
class Transcript:
    elements: List[Element]


# Define a regex pattern to parse transcriptions
defaultPattern = re.compile(
    r"""
    (?P<speaker>^[a-zA-Z]+)   # Match the speaker name at the beginning of a line (named group)
    (?=:)                     # Followed by a colon (positive lookahead)
    |                         # OR (alternation)
    (?P<time>\d{1,2}:\d{1,2}) # Match the time in hh:mm format (named group)
    |                         # OR (alternation)
    (?<=<)                    # Preceded by a left angle bracket '<' (positive lookbehind)
    (?P<pause>\d\.?\d*)       # Match the pause duration in seconds (named group)
    (?=>)                     # Followed by a right angle bracket '>' (positive lookahead)
    |                         # OR (alternation)
    (?P<word>\w+[-'’:+]?\w*)  # Match a word with optional dash, hyphen, apostrophe, colon, or plus (named group)
    |                         # OR (alternation)
    (?P<puncHard>[.?!])       # Match a hard punctuation mark (named group)
    |                         # OR (alternation)
    (?P<puncSoft>[’'\-\",])   # Match a soft punctuation mark (named group)
    """,
    re.VERBOSE | re.MULTILINE,  # Use verbose and multiline flags (flags)
)
# The verbose flag lets us use whitespace and comments inside of our pattern.
# The multiline flag lets us match multiline strings. For example, the '^' char is used to match at the beginning of a line.


def parse_transcript(inStr: str, regexPattern=defaultPattern) -> Transcript:
    # default verbose
    # check if running from main or import
    if "args" not in globals():
        verbose = False
    else:
        verbose = args.verbose

    # Defining the regex pattern for tokenizing the transcript
    pattern = re.compile(regexPattern)

    # Initialize empty transcript object that should contain only Element types (either Line or Time)
    transcript = Transcript([])

    # Iterate over the matches of the pattern in the transcript
    # for match in pattern.finditer(transcript):
    speaker: str = ""
    utteranceList = []
    matches = pattern.finditer(inStr)
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
                    transcript.elements.append(aLine)
                    speaker = m.group()
            case "time":
                if verbose:
                    print(f"Appending {m.group()} to {speaker}")
                aTime = Time(m.group())
                transcript.elements.append(aTime)
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

    # Check if the Transcript is empty (if guard)
    if len(transcript.elements) == 0:
        # Return an error message in a Err wrapper
        raise Exception("No subjects found in the transcript.")
    # Return the subjects list in an Ok wrapper
    # Flush last line
    aLine = Line(speaker, utteranceList.copy())
    transcript.elements.append(aLine)
    return transcript


def transcript_to_str(transcript: Transcript) -> str:
    # Initialize an empty string to store the text
    outText: str = ""
    lastUtter: Optional[Utterance] = None

    for ele in transcript.elements:
        match ele:
            case Time(time):
                outText += f"{time}\n"
            case Line(speaker, utterances):
                outText += f"{speaker}: "
                for utterance in utterances:
                    match utterance:
                        case Word(word):
                            # If hard punc before word, add a space before this word
                            if isinstance(lastUtter, PunctuationHard):
                                outText += f"{word}"
                            # If comma before word, add a space before this word
                            elif (
                                isinstance(lastUtter, PunctuationSoft)
                                and lastUtter.symbol == ","
                            ):
                                outText += f" {word}"
                            # If word before this word, add a space before this word
                            elif isinstance(lastUtter, Word):
                                outText += f" {word}"
                            # Otherwise do nothing
                            else:
                                outText += f"{word}"
                        case PunctuationHard(symbol):
                            outText += f"{symbol} "
                        case PunctuationSoft(symbol):
                            outText += f"{symbol}"
                        case Pause(duration):
                            outText += f" <{duration}> "
                    lastUtter = utterance
                outText += "\n\n"
                # lastUtter = line
    return outText


def count_words(transcript: Transcript, targetSpeaker: str) -> dict:
    # Define function to return a dict of wordCounts for a specific speaker, given a transcript with the respective speaker
    wordCount = defaultdict(int)
    for ele in transcript.elements:
        # if guards
        if not isinstance(ele, Line):
            continue
        if ele.speaker != targetSpeaker:
            continue

        for utterance in ele.utterances:
            match utterance:
                case Word(word):
                    # convert word to lower-case and inc word counter
                    wordCount[(word.lower())] += 1
    # cast back to dict
    return dict(wordCount)


# Define methods for arbitrary input


def raw_string_iter(
    inStr, participants, regexPattern=defaultPattern
) -> Generator[Utterance, None, None]:
    # Define a generator function to iterate through the words of an arbitrary string
    # For ex: whisperAI output

    # Defining the regex pattern for tokenizing the transcript
    pattern = re.compile(regexPattern)

    # Iterate over the matches of the pattern in the transcript
    # for match in pattern.finditer(transcript):
    matches = pattern.finditer(inStr)
    for m in matches:
        match m.lastgroup:
            case "word":
                yield Word(m.group())
            case "puncHard":
                yield PunctuationHard(m.group())
            case "puncSoft":
                yield PunctuationSoft(m.group())


def construct_transcript(inStr, participants, regexPattern=defaultPattern):
    if "args" not in globals():
        verbose = False
    else:
        verbose = args.verbose
    # Defining the regex pattern for tokenizing the transcript
    pattern = re.compile(regexPattern)

    # Initialize empty transcript object that should contain only Element types (either Line or Time)
    transcript = Transcript([])

    # Iterate over the matches of the pattern in the transcript
    # for match in pattern.finditer(transcript):
    # speaker: str = None
    utteranceList: List[Utterance] = []

    prevSpeaker: str = ""
    count: int = 0

    # Init currentLine with empty speaker and empty list of Utterance objects
    currentLine = Line("", [])
    # Build a sentence, ending when we find a PunctuationHard Object
    for utter in raw_string_iter(inStr, participants, pattern):
        match utter:
            case Word(m):
                # if verbose:
                #    print(f"Appending {m} to {utteranceList}")
                utteranceList.append(Word(m))
            case PunctuationHard(m):
                # if verbose:
                #    print(f"Appending {m} to {utteranceList}")
                utteranceList.append(PunctuationHard(m))
                # end the utteranceList, ask user to input speaker
                speaker = ""
                while speaker not in participants:
                    print("Sentence found, who is the speaker?")
                    print(f"Available speakers: {participants}")
                    print(utteranceList)
                    speaker = input(">").upper()
                    if speaker not in participants:
                        print("Invalid input!")

                # should run once
                # 2nd line speaker is not same as 1st, then flush 1st line
                if speaker != prevSpeaker and count == 1:
                    # Init currentLine with empty speaker and empty list of Utterance objects
                    currentLine = Line("", [])

                    currentLine.speaker = prevSpeaker
                    transcript.elements.append(currentLine.copy())
                    currentLine.utterances.clear()
                    if verbose:
                        print(transcript.elements)
                        print(f"SPEAKER {speaker} -> transcript")

                currentLine.utterances += utteranceList.copy()
                utteranceList.clear()

                # if current speaker is not same as last speaker, do not append to transcript
                # if current speaker is the same as last speaker, merge lines
                if speaker != prevSpeaker and count != 0:
                    # edit currentLine then append Transcript
                    currentLine.speaker = speaker
                    transcript.elements.append(currentLine.copy())
                    currentLine.utterances.clear()
                    if verbose:
                        print(transcript.elements)
                        print(f"SPEAKER {speaker} -> transcript")
                prevSpeaker = speaker
                if verbose:
                    print(f"count = {count}")
                    print(f"prevSpeaker = {speaker}")
                count += 1
            case PunctuationSoft(m):
                # if verbose:
                #    print(f"Appending {m} to {utteranceList}")
                utteranceList.append(PunctuationSoft(m))
            case Pause(m):
                # if verbose:
                #    print(f"Appending {m} to {utteranceList}")
                utteranceList.append(Pause(m))

    # Check if the Transcript is empty
    if len(transcript.elements) == 0:
        # Return an error message in a Err wrapper
        raise Exception("No lines found in input.")
    return transcript


if __name__ == "__main__":
    # parse args
    parser = argparse.ArgumentParser(
        prog="tulk.py",
        description="Interprets transcripted logs between multiple parties!",
    )

    # parser.add_argument('filename(s)')# positional argument
    parser.add_argument("-v", "--verbose", action="store_true")  # on/off flag
    parser.add_argument("-c", "--count_words_of", type=str)  # pass in speaker name here
    parser.add_argument("-p", "--participants", nargs="*", type=str)
    parser.add_argument("-o", "--output", type=argparse.FileType("a"))
    parser.add_argument(
        "-f", "--file", type=argparse.FileType("r"), nargs="+", required=True
    )
    args = parser.parse_args()

    if args.output:
        out = args.output
    else:
        out = sys.stdout

    # open file(s)
    for infile in args.file:
        # f, e = os.path.splitext(infile)
        # outfile = f + "_formatted" + e
        data = infile.read()
        s = args.count_words_of
        if s:
            transcript = parse_transcript(data)
            out.write(transcript_to_str(transcript))
            out.write(count_words(transcript, s))
        p = args.participants
        # capitalize all letters of participants
        p = [name.upper() for name in p]
        if p:
            transcript = construct_transcript(data, p, defaultPattern)
            # print(transcript)
            out.write(transcript_to_str(transcript))
