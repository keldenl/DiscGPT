def get_prompt(input: str) -> str:
    return f"""Convert normal messages to "DEEZ NUTS" jokes. 
All "DEEZ NUTS" jokes follow the following rules:
- "DEEZ" is used instead of "these", or "my", or "those"
- "NUTS" refer to male testicles in a humorous tone. "that" can be referring to nuts
- A DEEZ NUTS joke is a rephrasing of a sentence to include the phrase "DEEZ NUTS", followed by laughing
- Not all inputs work, when they don't, preempt your out: with "this is a stretch, but"

in: Something came in the mail today
||explanation: male tesitcles can *cum*, so DEEZ NUTS could *come* in your mailbox!||
out: DEEZ NUTS *came* in your mailbox!!!!! AHHAHHA GOTTTEM!!!! GOTTEM!! Get it? *CAME*

in: I can't wait to get home and play some video games.
||explanation: "Video games" is a noun that can be replaced and make sense with the noun nuts||
out:I bet you can't wait to get home and play with DEEZ NUTS!! AHAAA GOTTTTTTTTTEM!!!

in: can you hold this for me
||explanation: what's something you can hold? nuts are something you can hold||
out: can you hold DEEZ NUTS for me? ROFFLllLLMAO XD GOTTTEM

in: life is lonely, that's what makes it hard, I just realized this.
||explanation: nuts are also tough, so lets replace life with nuts||
out: Life is tough? What about DEEZ NUtS then? LMAOOOO GOTTEMMMMM HAHHHHHH!!!!!

in: i like banking with bofa
||explanation: bofa sounds like "both of". males have 2 nuts/tesicles, and so this can be rephrased with a play-on with "both of these nuts"||
out: more like you like BOFA DEEZ NUTS ALL OVER YOU! LOOOOL GOTTTTEM

in: {input}"""

# plugin_data = {
#     'preprompt': 'Convert messages to DEEZ NUTS jokes. \nDEEZ NUTS jokes rephrase messages to containt the phrase "DEEZ NUTS" and make contextual sense. Contextual sense is when either an object in the original message is replaced with "deez nuts" or a word in the original message that sounds like "deez" is replaced with "deez nuts". You may also rephrase other words to make the response mildy sexual, like suck resulting in "suck on deez nuts" or goblin resulting in "gobbling deez nuts" or pudding resulting in "pudding deez nuts in your mouth".\nYou run in a loop of in (for input), explain (explanation of conversion) and out (wrapped in ** **). Use explain to describe your thoughts about the in input youve been given. Use out (** **) to output the conversion:',
#     'examples': [
#         {
#             'in': 'can you hold this for me',
#             'explain': 'nuts are something you can hold',
#             'out': 'can you hold DEEZ NUTS for me',
#         },
#         {
#             'in': 'something came in the mail today',
#             'explain': 'nuts can be something that comes in the mail',
#             'out': 'deez nuts came in the mail today',
#         },
#         {
#             'in': 'to indicate it should always refer to "you"',
#             'explain': 'this isnt really convertable..',
#             'out': 'not sure how to :peanuts: this...',
#         },
#         {
#             'in': 'have you seen wendy around?',
#             'explain': 'the "dy" in wendy is pronounced like "dee", which sounds like "deez nuts"',
#             'out': 'ive seen deez nuts hit your face',
#         },
#         {
#             'in': 'i like banking with bofa',
#             'explain': 'bofa sounds like "both of". males have 2 nuts, and this is mildly sexual we can rephrase with a play-on with "both of these nuts"',
#             'out': 'more like you like bofa deez nuts all over you!',
#         },
#         {
#             'in': 'i honestly cant wait to eat my pudding',
#             'explain': 'pudding sounds like "putting", and putting nuts in mouths is mildy sexual',
#             'out': 'pudding deez nuts in your mouth?',
#         },
#         {
#             'in': 'what happened at kenya?',
#             'explain': 'kenya sounds like "can ya", and asking user if they can fit these nuts in their mouth is mildy sexual',
#             'out': 'kenya fit deez nuts in your mouth?!',
#         }
#     ],
# }
