import tulk

# Test the functions
# Defining the transcript
transcript = """
            A: Hello! Hello! Who is this? Nice, it's nice to see you.

            B: And who are you? and -

            F: What? <2.5> What did you say?? Hello??

            ALPH: Back to me!!

            B: Where?? Egg-salad and ham!!
"""
t = tulk.parse_transcript(transcript)
print(tulk.transcript_to_str(t))
print(tulk.count_words(t, "A"))
print(tulk.count_words(t, "B"))
