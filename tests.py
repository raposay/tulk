from tulk import parse_transcript, subjects_to_str, count_words
from tulk import Result, Ok, Err

# Test the functions
# Defining the transcript
transcript = """
            A: Hello! Hello! Who is this? Nice, it's nice to see you.

            B: And who are you? and -

            F: What? <2.5> What did you say?? Hello??

            ALPH: Back to me!!

            B: Where?? Egg-salad and ham!!
"""
result = parse_transcript(transcript)
if isinstance(result, Ok):
    print(subjects_to_str(result.value))
else:
    print(result)
print(count_words(result.value, "A"))
print(count_words(result.value, "B"))
