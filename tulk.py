# Importing the required modules
from dataclasses import dataclass
from typing import Union, List, Optional
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
    text: str

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

            A: Back to me!!
"""

# Defining the regex pattern for tokenizing the transcript
pattern = re.compile(r"""
    (?P<speaker>[A-Z]):\s+ # Match the speaker name followed by a colon and whitespace
    (?P<utterances>        # Match the utterances group
        (?:                # Start a non-capturing group
            \w+            # Match one or more word characters
            |              # Or
            [.,?!]         # Match one punctuation character
            |              # Or
            <\d+\.?\d*>    # Match a pause in angle brackets
        )+                 # Repeat the non-capturing group one or more times
    )                      # End the utterances group
    \s*                    # Match zero or more whitespace characters
    (?P<punctuation>)[.,?!]
    (?P<)
""", re.VERBOSE)

# Defining the function that returns a linked-list of Subject types
def parse_transcript(transcript: str) -> Result:
    # Initialize an empty list to store the subjects
    subjects = []

    # Iterate over the matches of the pattern in the transcript
    for match in pattern.finditer(transcript):
        # Extract the speaker and the utterances from the match
        speaker = match.group("speaker")
        utterances = match.group("utterances")

        # Initialize an empty list to store the utterances
        utterance_list = []

        # Iterate over the characters in the utterances
        for char in utterances:
            # Check if the character is alphanumerical character
            if char.isalnum():
                # Append a Word instance to the utterance list
                utterance_list.append(Word(char))
            # Check if the character is a punctuation character
            elif char in [".", ",", "?", "!"]:
                # Append a Punctuation instance to the utterance list
                utterance_list.append(Punctuation(char))
            # Check if the character is an opening angle bracket
            elif char == "<":
                # Initialize an empty string to store the pause duration
                pause = ""
                # Increment the index to skip the opening angle bracket
                index = utterances.index(char) + 1
                # Loop until the closing angle bracket is found
                while utterances[index] != ">":
                    # Append the character to the pause string
                    pause += utterances[index]
                    # Increment the index
                    index += 1
                # Convert the pause string to a float
                pause = float(pause)
                # Append a Pause instance to the utterance list
                utterance_list.append(Pause(pause))

        # Create a Subject instance with the speaker and the utterance list
        subject = Subject(speaker, utterance_list, None)

        # Check if the subjects list is empty
        if not subjects:
            # Append the subject to the subjects list
            subjects.append(subject)
        else:
            # Set the next attribute of the last subject in the subjects list to the current subject
            subjects[-1].next = subject
            # Append the subject to the subjects list
            subjects.append(subject)

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
                text += utterance.text
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

# Testing the functions
result = parse_transcript(transcript)
if isinstance(result, Ok):
    print_subjects(result.value)
else:
    print(result.error)
