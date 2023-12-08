# Tulk: A Python Script for Analyzing Transcripts

Tulk is a python script that can parse and analyze transcripted logs between multiple parties. It can handle different formats of transcripts, such as unorganized text or already formatted transcripts. It can also generate statistics and insights from the transcripts, such as word counts and hedging usage.

## Installation

To install Tulk, you need to have Python 3.6 or higher.

You can install Tulk by cloning this repository or downloading the source code as a zip file.

## Command-Line Usage

You can use Tulk as a command-line tool to process transcript files or unorganized files of strings. The basic usage is:

tulk [options] -f file1 file2(?) ...

where file1 file2(?) ... are the paths to the transcript files you want to analyze.

The options you can use are:

    -v or --verbose: Print verbose output, such as the parsed transcript and the analysis results.
    -c or --count_words_of: Specify the speaker name for which you want to get the word count. If not specified, the word count for all speakers will be shown.
    -p or --participants: Specify the names of the participants in the transcript. This is useful if the transcript does not have speaker labels or if you want to override them. The names should be separated by spaces.

For example, to analyze word count for Alice, from a transcript file called example.txt, you can run:

`tulk -c Alice -f example.txt`

## Documentation of Functions
Included types and datatypes are as follows:

- `Transcript`: a dataclass that contains a list of Element objects.
  - `Element`: is strictly either a TimeStamp or a Line type.
    - `TimeStamp`: a dataclass that contains a timestamp string that represents the moment-in-time of the transcript in hh:mm format.
    - `Line`: a dataclass that contains a speaker name and a list of strictly Utterance objects.
      - Utterance`: a dataclass that strictly is either a Word, Pause, or a Punctuation.
        - `Word`: a dataclass that contains a word string.
		- `Pause`: a dataclass that contains a duration float that represents the pause length in seconds.
        - `Punctuation`: a dataclass that is strictly either a PunctuationHard or a PunctuationSoft type.
		  - `PunctuationHard`: a dataclass that contains a symbol string that ends a sentence, such as “.”, “!”, or “?”.
		  - `PunctuationSoft`: a dataclass that contains a symbol string that does not end a sentence, such as “,”, “-”, or “'”.
	
The default regex pattern defaultPattern is defined in the module and can handle most common transcript formats.
You can also define your own regex pattern if you need to parse a different format.

If you want to use Tulk as a module in your own python code, you can import it and use its functions. The main functions are:

- `parse_transcript(inStr, regexPattern=DEFAULT_PATTERN)`: takes a string inStr that represents a transcript written in a defined grammar and a regex pattern regexPattern that defines how to parse it.

- `transcript_to_str(transcript: Transcript) -> str`: takes a Transcript object and returns a string that represents the transcript in a human-readable format.

- `count_words(transcript: Transcript, targetSpeaker: str) -> dict: takes a Transcript object and a string targetSpeaker that represents the name of a speaker. It returns a dictionary that maps each word used by the speaker to its frequency in the transcript.

- `raw_string_iter(inStr: str, participants: list[str], regexPattern=DEFAULT_PATTERN) -> Utterance`: takes a string inStr that represents a raw transcript, a list of strings participants that represents the names of the participants in the transcript, and a regex pattern regexPattern that defines how to parse the words and punctuation in the transcript. It returns a generator that yields Utterance objects. This function is useful if you want to process a transcript that does not have speaker labels.

- `construct_transcript(inStr: str, participants: list[str], regexPattern=DEFAULT_PATTERN) -> Transcript: takes a string inStr that represents an unorganized transcript, a list of strings participants that represents the names of the participants in the transcript, and a regex pattern regexPattern that defines how to parse the words and punctuation in the transcript. It returns a Transcript object that contains Line objects with speaker names assigned based on interactive user input.

## License Acknowledgement

Tulk is licensed under the MIT License. See the LICENSE file for more details.

## Badges for Useful Projects

[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
