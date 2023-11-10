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

Result = Union[Ok, Err]

# Defining the Utterance Union type
@dataclass
class Word:
    word: str

@dataclass
class Punctuation:
    symbol: str

@dataclass
class Pause:
    duration: float

# An Utterance can either be a Word OR Punctuation OR Pause
Utterance = Union[Word, Punctuation, Pause]

# Defining the Subject dataclass
@dataclass
class Subject:
    speaker: str
    utterances: List[Utterance]
    next: Optional['Subject']

# Defining the transcript
transcript = """
            A: Hello! Hello! Who is this? Nice, it's nice to see you.

            B: And who are you? and -

            F: What? <2> What did you say?? Hello??

            ALPH: Back to me!!

            B: Where??
"""

# Defining the regex pattern for tokenizing the transcript
pattern = re.compile(r"""
(?P<speaker>[A-Z]+)(?=:)|(?P<word>\w+)(?!:)|(?P<punctuation>[.,?!'\-\"])|(?P<pause><\d+\.?\d*>)
""", re.VERBOSE)

# Defining the function that returns a linked-list of Subject types
def parse_transcript(transcript: str) -> Result:
    # Initialize an empty list to store the subjects
    subjects = []

    # Iterate over the matches of the pattern in the transcript
    # for match in pattern.finditer(transcript):
    speaker = None
    utterance_list = []
    matches = pattern.finditer(transcript)
    for m in matches:
        match m.lastgroup:
            case "speaker":
                if args.verbose:
                    print(f"Speaker found: {m.group()}")
                # Set first speaker
                if not speaker:
                    speaker = m.group()
                # Flush otherwise
                else:
                    # Create a Subject instance with the speaker and the utterance list
                    subject = Subject(speaker, utterance_list.copy(), None)
                    utterance_list.clear()

                    # Check if the subjects list is empty
                    if not subjects:
                        # Append the subject to the subjects list
                        subjects.append(subject)
                    else:
                        # Set the next attribute of the last subject in the subjects list to the current subject
                        subjects[-1].next = subject
                        # Append the subject to the subjects list
                        subjects.append(subject)
                    speaker = m.group()
            case "word":
                if args.verbose:
                    print(f"Appending {m.group()} to {speaker}")
                utterance_list.append(Word(m.group()))
            case "punctuation":
                if args.verbose:
                    print(f"Appending {m.group()} to {speaker}")
                utterance_list.append(Punctuation(m.group()))
            
    # Check if the subjects list is not empty
    if subjects:
        # Return the first subject in the subjects list as the head of the linked-list
        return Ok(subjects[0])
    else:
        # Return an error message
        return Err("No subjects found in the transcript.")

# Defining the function that prints the Subject linked-list to human-readable text
def print_subjects(subject: Subject) -> None:
    # Initialize an empty string to store the text
    text = ""

    # Loop until the subject is None
    while subject:
        # Append the speaker name and a colon to the text
        text += subject.speaker + ": "
        # Iterate over the utterances in the subject
        for utterance in subject.utterances:
            # Check if the utterance is a Word instance
            if isinstance(utterance, Word):
                # Append the word text to the text
                text += utterance.word 
            # Check if the utterance is a Punctuation instance
            elif isinstance(utterance, Punctuation):
                # Append the punctuation symbol to the text
                text += utterance.symbol
            # Check if the utterance is a Pause instance
            elif isinstance(utterance, Pause):
                # Append the pause duration in angle brackets to the text
                text += f"<{utterance.duration}>"
        # Append a newline character to the text
        text += "\n"
        # Set the subject to the next subject in the linked-list
        subject = subject.next
    
    # Print the text
    print(text)

parser = argparse.ArgumentParser(
    prog="tulk.py",
    description="Interprets transcripted logs between multiple parties!",
)

#parser.add_argument('filename(s)')# positional argument
parser.add_argument('-v', '--verbose', action='store_true')# on/off flag
args = parser.parse_args()

# Testing the functions
result = parse_transcript(transcript)
if isinstance(result, Ok):
    print_subjects(result.value)
else:
    print(result)
