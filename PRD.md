**Functional Requirements:**
- The user can set and watch a debate between two sides, overseen by a moderator/judge.
- The user can select from a list of available models what model to use for the debaters and the judge.
- The user is able to set a custom topic for the debate like “Will AI replace human jobs?” or “Is the penetration of technology into daily life affecting human relationships negatively?” - this can be typed up from scratch or chosen from a list of sample topics (may be hardcoded, or generated on the fly using the moderator/judge model.)
- The user can set how long the debate should continue (in terms of numbers of back and forth responses before the moderator has to declare a winner)
- The user can see the responses from the two sides and the moderator as they happen in real time.
- The conversation and the result should be saved in an output file.
- There should be an indicator indicating each model is thinking.

**Non-functional requirements:**
- Each response turn should not take more than 10 seconds to generate.

**Implementation Requirements:**
- All three roles (debater 1 - the proposition, debater 2 - the opposition, and the moderator/judge) will be played by LLMs, accessed via Ollama. For this first version we will default to Gemma3 1b for both debaters and the moderator which is available locally.
- For the first version of the app, these models will be stored locally. For future versions we could support online models so let’s make sure the implementation is done in a way that abstracts these away and can be easily extended.
- The UI can be simple but it needs to show the current issue being discussed up at top (with an option for choosing a predetermined item or typing in a question to be the topic of the debate), number of back and forths desired, a button to start the debate. The conversation is shown below in a scrollable window, as a dialogue between the actors.
- As a part of writing the code and designing the system, we need to write down behavior definitions for each participant. These can be stored in .md files, one for each agent instance (moderator, proposition, opposition) and will be fed to the agent instances.
