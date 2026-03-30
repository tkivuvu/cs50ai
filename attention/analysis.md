# Analysis

## Layer 1, Head 4

This particular attention head seems to be paying close attention to the token that comes right before the current token. Having used three different sentences, words pay close attention to those that are coming right before them, this suggests that the head helps local sequence order and close dependencies between neighboring tokens.

Example Sentences:
- The dog chased the [MASK].
- The quick brown fox jumps over the [MASK].

## Layer 3, Head 7

This attention head appears to be capturing sentence structure. This especially seems to happen in relationships between verbs and their ojects or object positions. For example, in the sentence "The dog chased the [MASK].", the verb "chased" pays close attention to the masked object. In another example the sentence "She read the book in the [MASK]", the word "read" pays close attention to the word "book", and finally, in the sentence "The quick brown fox jumps over the [MASK].", the verb phrase attends stronly to the following object position.

Example Sentences:
- The dog chased the [MASK].
- She read the book in the [MASK].

