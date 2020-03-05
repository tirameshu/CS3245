This is the README file for A0180257E's submission.
Email: e0273834@u.nus.edu

== Python Version ==

I'm using Python Version 3.7 for this assignment.

== General Notes about this assignment ==

Give an overview of your program, describe the important algorithms/steps 
in your program, and discuss your experiments in general.  A few paragraphs 
are usually sufficient.

Program did not use nltk tokeniser, and instead sliced given sentence directly into 4-grams (tokens) using python's string slicing.
Algorithm is as follows:
1) In the training function, two 2-d dictionaries are maintained. One for every language (lang_tokens), where the key is the language, and the values are dictionaries of tokens and their counts (based on training input sentences). The other is for every token (token_langs), where the key is the token, and the values are dictionaries of languages and the token counts. Token counts in both dictionaries are the same. The reason for both dictionaries to exist is for easy access of values when calculating probability later on.
2) Additionally, two lists are also maintained, one to keep track of all languages encountered, and one for all tokens encountered. These are used mainly for smoothing.
3) When a new line is encountered, the first word is taken to be the language of the following words. The words are then slices repeatedly into tokens.
4) When a new token is first encountered, it is added to the list of tokens and its nested dictionary initialised. The token_langs and lang_tokens are also initialised for the token, and smoothing is immediately applied. token_langs and lang_tokens both loop through all known languages and add 1 to the token's count in every language.
5) Then the token's actual count is added to the language stated for the words, obtained in step 3.
6) Token and words are updated.
7) This continues for every line. When tokens encountered before re-appear, they still have to check whether new languages have been encountered. If yes, 1 count will be added to the token for the new language, for smoothing. Both dictionaries are updated.
8) To handle the situation where a token does not re-appear, but a new language does, all tokens check for new languages when calculating the probability.
9) To calculate probability, two new dictionaries are maintained, p_lang_tokens and p_token_langs. They are of the same nature as the aforementioned dictionaries, and only differ in that the values stored are no longer counts but probabilities.
10) All languages and all tokens are looped through to ensure smoothing has been done for all encounters.
11) Once all tokens are accounted for, the probability of encountering a particular token for a particular language is calculated with token_count / total_encounters_of_tokens for every language.
12) The two probability dictionaries are then updated for every token and the corresponding language.
13) The p_token_langs dictionary is specifically returned as the Language Model, as the testing phase involves retrieving probability based on token encounter, and not language encounter.
14) Testing phase is conducted by adding the log of the probability of encountering every token, for each language. Then the maximum is taken, and the corresponding language is returned.

== Files included with this submission ==

List the files in your submission here and provide a short 1 line
description of each file.  Make sure your submission's files are named
and formatted correctly.

build_test_LM.py: source code for the training and testing algorithm.

== Statement of individual work ==

Please put a "x" (without the double quotes) into the bracket of the appropriate statement.

[x] I, A0180257E, certify that I have followed the CS 3245 Information
Retrieval class guidelines for homework assignments.  In particular, I
expressly vow that I have followed the Facebook rule in discussing
with others in doing the assignment and did not take notes (digital or
printed) from the discussions.  

[ ] I, A0000000X, did not follow the class rules regarding homework
assignment, because of the following reason:

<Please fill in>

I suggest that I should be graded as follows:

<Please fill in>

== References ==

Atharv suggested that I add log of the probability instead of doing direct multiplication, as some of the probabilities can be too small to multiply.
