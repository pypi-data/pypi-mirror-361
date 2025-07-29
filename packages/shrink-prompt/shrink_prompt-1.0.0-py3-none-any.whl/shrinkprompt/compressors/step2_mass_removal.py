"""Step 2: Mass Removal - Comprehensive removal of safe-to-remove words and phrases."""

import re


# CONTEXT-AWARE REMOVAL - Smart patterns that protect proper nouns and technical terms

# Filler words and hedging language with context-aware patterns (expanded)
_FILLER_WORDS = {
    "actually", "really", "quite", "very", "just", "simply", "basically", 
    "literally", "essentially", "generally", "typically", "usually", 
    "probably", "possibly", "perhaps", "maybe", "might", "could", 
    "rather", "somewhat", "fairly", "pretty", "kind", "sort", "obviously",
    "clearly", "certainly", "definitely", "absolutely", "totally", "completely",
    "entirely", "exactly", "precisely", "specifically", "particularly",
    "especially", "notably", "remarkably", "significantly", "considerably",
    "substantially", "extremely", "incredibly", "tremendously", "enormously",
    "vastly", "hugely", "massively", "utterly", "thoroughly", "fully",
    "truly", "genuinely", "honestly", "frankly", "seriously", "naturally",
    "obviously", "of course", "needless to say", "it goes without saying",
    "undoubtedly", "unquestionably", "indubitably", "invariably", "consistently",
    "constantly", "continually", "repeatedly", "frequently", "occasionally",
    "sometimes", "often", "rarely", "seldom", "hardly", "barely", "scarcely",
    "merely", "solely", "purely", "exclusively", "primarily", "mainly",
    "chiefly", "largely", "mostly", "predominantly", "principally", "fundamentally",
    "inherently", "intrinsically", "essentially", "effectively", "practically",
    "virtually", "relatively", "comparatively", "proportionally", "accordingly"
}

# Hedge words and uncertainty markers (expanded)
_HEDGE_WORDS = {
    "apparently", "seemingly", "supposedly", "allegedly", "presumably",
    "conceivably", "potentially", "theoretically", "hypothetically",
    "arguably", "ostensibly", "purportedly", "reportedly", "evidently",
    "presumably", "likely", "unlikely", "tends to", "appears to",
    "seems to", "looks like", "sounds like", "feels like", "sort of",
    "kind of", "more or less", "roughly", "approximately", "around",
    "about", "nearly", "almost", "virtually", "practically", "effectively",
    "supposedly", "allegedly", "presumably", "conceivably", "potentially",
    "theoretically", "hypothetically", "arguably", "ostensibly", "purportedly",
    "reportedly", "evidently", "manifestly", "demonstrably", "verifiably",
    "undeniably", "irrefutably", "incontrovertibly", "conclusively", "definitively",
    "categorically", "unequivocally", "emphatically", "decisively", "resolutely",
    "firmly", "strongly", "powerfully", "forcefully", "vigorously", "intensely"
}

# Intensifiers and emphasis words (expanded)
_INTENSIFIERS = {
    "super", "ultra", "mega", "hyper", "extra", "so", "such", "too",
    "way", "well", "much", "far", "quite", "rather", "pretty", "fairly",
    "really", "truly", "genuinely", "seriously", "honestly", "literally",
    "actually", "definitely", "certainly", "absolutely", "totally",
    "completely", "entirely", "fully", "thoroughly", "utterly",
    "exceptionally", "extraordinarily", "remarkably", "unusually", "uncommonly",
    "surprisingly", "astonishingly", "amazingly", "incredibly", "unbelievably",
    "phenomenally", "tremendously", "enormously", "immensely", "vastly",
    "hugely", "massively", "monumentally", "colossally", "astronomically",
    "infinitely", "boundlessly", "limitlessly", "endlessly", "eternally"
}

# Business and corporate jargon (NEW)
_BUSINESS_JARGON = {
    "leverage", "synergize", "optimize", "maximize", "minimize", "streamline",
    "enhance", "facilitate", "implement", "initiate", "terminate", "utilize",
    "demonstrate", "accomplish", "assist", "obtain", "acquire", "purchase",
    "procure", "request", "inquire", "examine", "investigate", "analyze",
    "evaluate", "determine", "ascertain", "strategize", "conceptualize",
    "operationalize", "contextualize", "compartmentalize", "prioritize",
    "categorize", "customize", "personalize", "standardize", "systematize",
    "modernize", "revolutionize", "materialize", "crystallize", "synthesize",
    "visualize", "actualize", "realize", "capitalize", "monetize", "digitize",
    "automate", "integrate", "consolidate", "collaborate", "coordinate",
    "communicate", "articulate", "disseminate", "proliferate", "perpetuate"
}

# Academic writing fluff (NEW)
_ACADEMIC_FLUFF = {
    "in the context of", "within the framework of", "in the realm of",
    "in the domain of", "in the sphere of", "in the field of", "in the area of",
    "with respect to", "with regard to", "in relation to", "in connection with",
    "in association with", "in conjunction with", "in collaboration with",
    "in cooperation with", "in partnership with", "in accordance with",
    "in compliance with", "in conformity with", "in harmony with",
    "in alignment with", "in keeping with", "in line with", "consistent with",
    "compatible with", "congruent with", "commensurate with", "proportionate to",
    "relative to", "pertaining to", "relating to", "concerning", "regarding",
    "touching on", "bearing on", "relevant to", "applicable to", "germane to"
}

# Discourse markers and transitional fillers (expanded)
_DISCOURSE_MARKERS = {
    "you know", "you see", "you understand", "you realize", "you get it",
    "like I said", "as I mentioned", "as I noted", "as I stated",
    "in other words", "to put it simply", "to be clear", "to clarify",
    "that is to say", "in essence", "essentially", "basically",
    "fundamentally", "at the end of the day", "when all is said and done",
    "the bottom line is", "the point is", "the thing is", "the fact is",
    "the truth is", "the reality is", "believe it or not", "as it turns out",
    "as a matter of fact", "for that matter", "in any case", "in any event",
    "be that as it may", "having said that", "that said", "that being said",
    "with that in mind", "given that", "considering that", "seeing as",
    "since we're on the topic", "while we're at it", "speaking of which",
    "by the way", "incidentally", "as an aside", "parenthetically",
    "to wrap up", "in conclusion", "to conclude", "to summarize",
    "to sum up", "in summary", "all in all", "overall", "on the whole",
    "by and large", "for the most part", "generally speaking", "broadly speaking",
    "strictly speaking", "technically speaking", "practically speaking",
    "realistically speaking", "honestly speaking", "truthfully speaking"
}

# Polite language and social pleasantries (expanded)
_POLITE_LANGUAGE = {
    "please", "kindly", "thanks", "thank", "sorry", "excuse", "pardon",
    "appreciate", "grateful", "wonderful", "great", "fantastic", "amazing",
    "awesome", "brilliant", "excellent", "perfect", "ideal", "nice",
    "lovely", "marvelous", "superb", "outstanding", "exceptional",
    "remarkable", "incredible", "magnificent", "splendid", "terrific",
    "fabulous", "divine", "heavenly", "delightful", "charming",
    "gracious", "courteous", "polite", "respectful", "considerate",
    "thoughtful", "kind", "gentle", "warm", "friendly", "pleasant",
    "agreeable", "amiable", "cordial", "welcoming", "hospitable",
    "accommodating", "obliging", "helpful", "supportive", "encouraging",
    "understanding", "patient", "tolerant", "forgiving", "compassionate"
}

# Social fluff and greetings (expanded)
_SOCIAL_FLUFF = {
    "hello", "hi", "greetings", "good morning", "good afternoon", "good evening",
    "hope you're well", "hope this finds you well", "I hope", "I trust",
    "how are you", "how's it going", "what's up", "hey there", "howdy",
    "salutations", "good day", "pleasant day", "nice to meet you",
    "pleasure to meet you", "how do you do", "lovely weather",
    "have a great day", "have a nice day", "take care", "see you later",
    "until next time", "catch you later", "talk soon", "best wishes",
    "warm regards", "kind regards", "sincerely", "yours truly",
    "respectfully", "cordially", "faithfully", "devotedly", "affectionately",
    "fondly", "lovingly", "tenderly", "gently", "softly", "quietly",
    "peacefully", "calmly", "serenely", "tranquilly", "blissfully"
}

# Question starters that can be completely removed (expanded)
_QUESTION_STARTERS = {
    "can you", "could you", "would you", "will you", "do you", 
    "are you able to", "is it possible to", "can you help me", 
    "could you help me", "would you mind", "i was wondering if",
    "could you please", "would you please", "can you please",
    "would it be possible", "is there any way", "do you think you could",
    "might you be able to", "would you be willing to", "could you possibly",
    "would you consider", "is there a chance", "any chance you could",
    "would you happen to", "do you happen to", "by any chance could you",
    "if you don't mind", "if it's not too much trouble", "if you have time",
    "when you have a moment", "at your convenience", "if you're available",
    "if you're free", "if you're not busy", "when you get a chance",
    "would you be so kind as to", "could you be so kind as to",
    "might I ask you to", "may I request that you", "could I trouble you to"
}

# Verbose phrases that can be shortened (dramatically expanded)
_VERBOSE_PHRASES = {
    # Request and information phrases
    "give me": "return",
    "provide me with": "return", 
    "show me": "return",
    "tell me": "return",
    "let me know": "tell me",
    "inform me": "tell me",
    "enlighten me": "explain",
    "educate me": "explain",
    "brief me": "explain",
    "fill me in": "explain",
    "bring me up to speed": "explain",
    "walk me through": "explain",
    "run me through": "explain",
    "guide me through": "explain",
    "take me through": "explain",
    "lead me through": "explain",
    "help me understand": "explain",
    "help me grasp": "explain",
    "help me comprehend": "explain",
    "make it clear": "explain",
    "clarify for me": "explain",
    "spell it out": "explain",
    "break it down": "explain",
    "elaborate on": "explain",
    "expand on": "explain",
    "detail": "explain",
    "describe in detail": "explain",
    "go into detail": "explain",
    "provide details": "explain",
    "give me the details": "explain",
    "share the details": "explain",
    
    # Connecting phrases
    "in order to": "to",
    "so as to": "to",
    "with the purpose of": "to",
    "with the intention of": "to",
    "with the goal of": "to",
    "with the aim of": "to",
    "for the purpose of": "to",
    "for the sake of": "to",
    "in an effort to": "to",
    "in an attempt to": "to",
    "with a view to": "to",
    "as well as": "and",
    "along with": "and",
    "together with": "and",
    "in addition to": "and",
    "not to mention": "and",
    "not only that but": "and",
    "on top of that": "and",
    "furthermore": "and",
    "moreover": "and",
    "besides": "and",
    "plus": "and",
    "such as": "like",
    "for example": "eg",
    "for instance": "eg",
    "to illustrate": "eg",
    "as an example": "eg",
    "case in point": "eg",
    "namely": "eg",
    "specifically": "eg",
    "that is": "ie",
    "in other words": "ie",
    "to put it differently": "ie",
    "to rephrase": "ie",
    "to put it another way": "ie",
    "what I mean is": "ie",
    "that is to say": "ie",
    
    # Relationship phrases
    "with regard to": "about",
    "with respect to": "about",
    "in relation to": "about",
    "concerning": "about",
    "regarding": "about",
    "pertaining to": "about",
    "relating to": "about",
    "in connection with": "about",
    "in reference to": "about",
    "with reference to": "about",
    "as regards": "about",
    "as concerns": "about",
    "touching on": "about",
    "bearing on": "about",
    "in terms of": "for",
    "as far as": "for",
    "when it comes to": "for",
    "in the context of": "for",
    "within the context of": "for",
    "in the case of": "for",
    "in the matter of": "for",
    "on the subject of": "about",
    "on the topic of": "about",
    "on the question of": "about",
    
    # Time expressions
    "at this point in time": "now",
    "at the present time": "now",
    "at this moment in time": "now",
    "at the present moment": "now",
    "at this juncture": "now",
    "as of now": "now",
    "as we speak": "now",
    "at present": "now",
    "presently": "now",
    "currently": "now",
    "right now": "now",
    "at this time": "now",
    "in the near future": "soon",
    "in the not too distant future": "soon",
    "before too long": "soon",
    "in the coming days": "soon",
    "in the coming weeks": "soon",
    "in the immediate future": "soon",
    "shortly": "soon",
    "in a short while": "soon",
    "in a little while": "soon",
    "before long": "soon",
    "ere long": "soon",
    
    # Causal relationships
    "due to the fact that": "because",
    "for the reason that": "because",
    "on account of": "because",
    "as a result of": "because",
    "owing to": "because",
    "by reason of": "because",
    "by virtue of": "because",
    "in view of": "because",
    "in light of": "because",
    "considering": "because",
    "given that": "because",
    "seeing that": "because",
    "inasmuch as": "because",
    "insofar as": "because",
    "in that": "because",
    "for": "because",
    "since": "because",
    "in spite of": "despite",
    "regardless of": "despite",
    "notwithstanding": "despite",
    "irrespective of": "despite",
    "without regard to": "despite",
    "in the face of": "despite",
    
    # Contrast and comparison
    "on the other hand": "however",
    "by contrast": "however",
    "conversely": "however",
    "on the contrary": "however",
    "in contrast": "however",
    "by way of contrast": "however",
    "alternatively": "however",
    "instead": "however",
    "rather": "however",
    "as opposed to": "vs",
    "in opposition to": "vs",
    "contrary to": "vs",
    "unlike": "vs",
    "as against": "vs",
    "versus": "vs",
    "compared to": "vs",
    "compared with": "vs",
    "in comparison to": "vs",
    "in comparison with": "vs",
    "relative to": "vs",
    
    # Result and consequence
    "as a result": "so",
    "as a consequence": "so",
    "consequently": "so",
    "therefore": "so",
    "thus": "so",
    "hence": "so",
    "accordingly": "so",
    "for this reason": "so",
    "for that reason": "so",
    "on this account": "so",
    "on that account": "so",
    "in consequence": "so",
    "as a follow-up": "so",
    "following from this": "so",
    "it follows that": "so",
    "the result is": "so",
    "the outcome is": "so",
    "the upshot is": "so",
    
    # Consideration and thinking
    "take into account": "consider",
    "take into consideration": "consider",
    "bear in mind": "consider",
    "keep in mind": "consider",
    "take note of": "consider",
    "pay attention to": "consider",
    "give thought to": "consider",
    "give consideration to": "consider",
    "think about": "consider",
    "reflect on": "consider",
    "ponder": "consider",
    "contemplate": "consider",
    "deliberate on": "consider",
    "mull over": "consider",
    "weigh up": "consider",
    "evaluate": "consider",
    "assess": "consider",
    "examine": "consider",
    "analyze": "consider",
    "study": "consider",
    "review": "consider",
    "look at": "consider",
    "look into": "consider",
    "investigate": "consider",
    "explore": "consider",
    
    # Assurance and verification
    "make sure": "ensure",
    "make certain": "ensure",
    "see to it that": "ensure",
    "verify that": "ensure",
    "confirm that": "ensure",
    "check that": "ensure",
    "ascertain that": "ensure",
    "establish that": "ensure",
    "determine that": "ensure",
    "guarantee that": "ensure",
    "warrant that": "ensure",
    "certify that": "ensure",
    "validate that": "ensure",
    "substantiate that": "ensure",
    "corroborate that": "ensure",
    
    # Knowledge and understanding  
    "i would like to know": "explain",
    "i need to understand": "explain", 
    "i want to learn": "explain",
    "i'd like to learn": "explain",
    "help me understand": "explain",
    "explain to me": "explain",
    "tell me about": "explain",
    "describe": "explain",
    "clarify": "explain",
    "elucidate": "explain",
    "illuminate": "explain",
    "shed light on": "explain",
    "throw light on": "explain",
    "make clear": "explain",
    "make plain": "explain",
    "spell out": "explain",
    "set forth": "explain",
    "lay out": "explain",
    "outline": "explain",
    "detail": "explain",
    "expound": "explain",
    "elaborate": "explain",
    "expand on": "explain",
    "develop": "explain",
    "unfold": "explain",
    "reveal": "explain",
    "disclose": "explain",
    "divulge": "explain",
    "impart": "explain",
    "convey": "explain",
    "communicate": "explain",
    "transmit": "explain",
    "relay": "explain",
    "pass on": "explain",
    "share": "explain"
}

# Phrases that can be completely removed (add no meaning) - expanded
_REMOVABLE_PHRASES = {
    "it should be noted", "it is important to", "it is worth noting",
    "it is worth mentioning", "it should be mentioned", "it must be said",
    "it goes without saying", "needless to say", "obviously",
    "please note that", "keep in mind", "bear in mind", "furthermore",
    "moreover", "additionally", "what is more", "not only", "but also",
    "as well", "also", "too", "in addition", "besides", "plus",
    "i would appreciate", "i would really appreciate", "as soon as possible",
    "i was wondering", "if you don't mind", "if it's possible", 
    "if you could", "would you be so kind", "if it's not too much trouble",
    "at your convenience", "when you have a moment", "when you get a chance",
    "if you have the time", "whenever you're free", "no rush", "no hurry",
    "take your time", "in your own time", "as you see fit",
    "as you deem appropriate", "as you think best", "as you prefer",
    "however you'd like", "whatever works for you", "whatever suits you",
    "i realize", "i understand", "i know", "i'm aware", "i recognize",
    "it's clear that", "it's obvious that", "it's evident that",
    "there's no doubt that", "without a doubt", "undoubtedly", "certainly",
    "definitely", "absolutely", "surely", "of course", "naturally",
    "as you know", "as you're aware", "as you might know", "as you probably know",
    "as you can see", "as you might expect", "as you would expect",
    "as you might imagine", "as you can imagine", "as you might guess",
    "as is well known", "as is commonly known", "as everyone knows",
    "it is well established", "it is widely recognized", "it is generally accepted",
    "it is universally acknowledged", "it is commonly understood",
    "it is broadly agreed", "it is widely believed", "it is generally thought"
}

# Meta-commentary that adds no value (expanded)
_META_COMMENTARY = {
    "let me start by saying", "first of all", "to begin with", "initially",
    "at the outset", "from the start", "right off the bat", "straight away",
    "before we begin", "before we start", "before I continue",
    "moving on", "let's move on", "next", "now", "so", "well", "anyway",
    "in any case", "be that as it may", "having said that", "that said",
    "with that in mind", "given that", "considering that", "seeing as",
    "since we're on the topic", "while we're at it", "speaking of which",
    "by the way", "incidentally", "as an aside", "parenthetically",
    "to wrap up", "in conclusion", "to conclude", "to summarize",
    "to sum up", "in summary", "all in all", "overall", "on the whole",
    "by and large", "for the most part", "generally speaking",
    "first and foremost", "last but not least", "above all", "most importantly",
    "it should be emphasized", "it should be stressed", "it should be highlighted",
    "it cannot be overstated", "it bears repeating", "it's worth reiterating",
    "let me emphasize", "let me stress", "let me highlight", "let me point out",
    "let me clarify", "let me explain", "let me elaborate", "allow me to say",
    "permit me to say", "if I may say", "if I might add", "if I could add",
    "on a related note", "in a similar vein", "along the same lines",
    "in the same spirit", "with this in mind", "bearing this in mind"
}

# Time and urgency expressions that can be simplified (expanded)
_TIME_EXPRESSIONS = {
    "as soon as possible": "ASAP",
    "at your earliest convenience": "soon",
    "when you have a moment": "soon",
    "when you get a chance": "soon",
    "at the earliest opportunity": "ASAP",
    "without delay": "now",
    "immediately": "now",
    "right away": "now",
    "straight away": "now",
    "as quickly as possible": "ASAP",
    "with urgency": "urgently",
    "in a timely manner": "quickly",
    "in due course": "later",
    "in the fullness of time": "eventually",
    "sooner or later": "eventually",
    "at some point": "later",
    "down the road": "later",
    "down the line": "later",
    "in the long run": "eventually",
    "in the long term": "eventually",
    "over time": "eventually",
    "over the long haul": "eventually",
    "in the course of time": "eventually",
    "with the passage of time": "eventually",
    "as time goes by": "eventually",
    "as time passes": "eventually",
    "in time": "eventually",
    "at some future date": "later",
    "at some future time": "later",
    "at a later date": "later",
    "at a later time": "later",
    "on a future occasion": "later",
    "on some future occasion": "later",
    "sometime in the future": "later",
    "sometime down the road": "later"
}

# Redundant expressions (NEW)
_REDUNDANT_EXPRESSIONS = {
    "absolutely essential": "essential",
    "absolutely necessary": "necessary",
    "absolutely perfect": "perfect",
    "advance planning": "planning",
    "basic fundamentals": "fundamentals",
    "brief summary": "summary",
    "close proximity": "proximity",
    "completely eliminated": "eliminated",
    "completely finished": "finished",
    "current status": "status",
    "different varieties": "varieties",
    "each individual": "each",
    "end result": "result",
    "exact same": "same",
    "false pretense": "pretense",
    "final outcome": "outcome",
    "free gift": "gift",
    "future plans": "plans",
    "general consensus": "consensus",
    "honest truth": "truth",
    "important essentials": "essentials",
    "necessary requirements": "requirements",
    "new innovation": "innovation",
    "past history": "history",
    "personal opinion": "opinion",
    "serious crisis": "crisis",
    "successful achievement": "achievement",
    "sufficient enough": "sufficient",
    "true facts": "facts",
    "unexpected surprise": "surprise",
    "unique difference": "difference",
    "usual custom": "custom",
    "various different": "various"
}


def mass_removal(text: str) -> str:
    """Step 2: Remove all safe-to-remove words and phrases.
    
    Args:
        text: Input text to process
        
    Returns:
        Text with comprehensive mass removals applied
    """
    # Remove redundant expressions first
    for redundant, clean in _REDUNDANT_EXPRESSIONS.items():
        pattern = rf'\b{re.escape(redundant)}\b'
        text = re.sub(pattern, clean, text, flags=re.IGNORECASE)
    
    # Remove meta-commentary (complete removal)
    for meta in _META_COMMENTARY:
        pattern = rf'\b{re.escape(meta)}\b'
        text = re.sub(pattern, '', text, flags=re.IGNORECASE)
    
    # Remove academic fluff
    for fluff in _ACADEMIC_FLUFF:
        pattern = rf'\b{re.escape(fluff)}\b'
        text = re.sub(pattern, '', text, flags=re.IGNORECASE)
    
    # Remove business jargon with context-awareness (replace with simpler terms)
    business_replacements = {
        "leverage": "use", "synergize": "combine", "optimize": "improve",
        "streamline": "simplify", "enhance": "improve", "facilitate": "help",
        "utilize": "use", "implement": "do", "strategize": "plan"
    }
    for jargon, simple in business_replacements.items():
        if jargon in _BUSINESS_JARGON:
            # Don't replace when part of technical terms or proper business phrases
            pattern = rf'\b{re.escape(jargon)}\b(?!\s+(?:performance|efficiency|solutions|systems|architecture|infrastructure|processes|workflows|strategies|methodologies))'
            text = re.sub(pattern, simple, text, flags=re.IGNORECASE)
    
    # Remove other business jargon with context-awareness
    for jargon in _BUSINESS_JARGON:
        if jargon not in business_replacements:
            # Preserve when followed by technical or business-specific terms
            pattern = rf'\b{re.escape(jargon)}\b(?!\s+(?:[A-Z][a-z]+|solutions|systems|processes|methodologies|frameworks|platforms|applications|services))'
            text = re.sub(pattern, '', text, flags=re.IGNORECASE)
    
    # Remove removable phrases (complete removal)
    for phrase in _REMOVABLE_PHRASES:
        pattern = rf'\b{re.escape(phrase)}\b'
        text = re.sub(pattern, '', text, flags=re.IGNORECASE)
    
    # Replace time expressions
    for time_expr, replacement in _TIME_EXPRESSIONS.items():
        pattern = rf'\b{re.escape(time_expr)}\b'
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    
    # Replace verbose phrases with shorter alternatives
    for verbose, short in _VERBOSE_PHRASES.items():
        pattern = rf'\b{re.escape(verbose)}\b'
        text = re.sub(pattern, short, text, flags=re.IGNORECASE)
    
    # Remove question starters
    for starter in _QUESTION_STARTERS:
        pattern = rf'\b{re.escape(starter)}\b'
        text = re.sub(pattern, '', text, flags=re.IGNORECASE)
    
    # Remove discourse markers
    for marker in _DISCOURSE_MARKERS:
        pattern = rf'\b{re.escape(marker)}\b'
        text = re.sub(pattern, '', text, flags=re.IGNORECASE)
    
    # Remove hedge words with context-awareness - preserve when expressing technical uncertainty
    for hedge in _HEDGE_WORDS:
        # Don't remove when followed by technical terms or specific claims
        pattern = rf'\b{re.escape(hedge)}\b(?!\s+(?:[A-Z][a-z]+|this|the|that|performance|efficiency|accuracy|results|findings|data))'
        text = re.sub(pattern, '', text, flags=re.IGNORECASE)
    
    # Remove intensifiers with enhanced context-awareness
    for intensifier in _INTENSIFIERS:
        # Only remove if not modifying important technical adjectives or proper nouns
        pattern = rf'\b{re.escape(intensifier)}\b(?!\s+(?:[A-Z][a-z]+|important|critical|essential|significant|complex|advanced|sophisticated|high|low|fast|slow|large|small|secure|accurate|efficient|reliable|scalable))'
        text = re.sub(pattern, '', text, flags=re.IGNORECASE)
    
    # Remove filler words with context-awareness - DON'T remove if followed by proper nouns or technical terms
    for filler in _FILLER_WORDS:
        # Use negative lookahead to protect proper nouns and technical terms
        pattern = rf'\b{re.escape(filler)}\b(?!\s+(?:[A-Z][a-z]+|Data|Learning|Performance|Security|System|Network|Algorithm|Model|Analysis|Research|Study))'
        text = re.sub(pattern, '', text, flags=re.IGNORECASE)
    
    # Remove polite language with context-awareness
    for polite in _POLITE_LANGUAGE:
        # Protect when followed by technical terms or formal titles
        pattern = rf'\b{re.escape(polite)}\b(?!\s+(?:[A-Z][a-z]+|you|Mr|Mrs|Dr|Professor|Director|Manager|Engineer|Analyst))'
        text = re.sub(pattern, '', text, flags=re.IGNORECASE)
    
    # Remove social fluff with context-awareness
    for fluff in _SOCIAL_FLUFF:
        # Protect proper greetings and formal phrases
        pattern = rf'\b{re.escape(fluff)}\b(?!\s+(?:[A-Z][a-z]+|to|from|with))'
        text = re.sub(pattern, '', text, flags=re.IGNORECASE)
    
    # Advanced cleanup for artifacts
    
    # Remove redundant conjunctions and prepositions
    text = re.sub(r'\band\s+and\b', 'and', text, flags=re.IGNORECASE)
    text = re.sub(r'\bor\s+or\b', 'or', text, flags=re.IGNORECASE)
    text = re.sub(r'\bto\s+to\b', 'to', text, flags=re.IGNORECASE)
    text = re.sub(r'\bfor\s+for\b', 'for', text, flags=re.IGNORECASE)
    
    # Clean up multiple spaces and punctuation artifacts
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'\s*,\s*,', ',', text)
    text = re.sub(r'\s*\.\s*\.', '.', text)
    text = re.sub(r'^\s*[,.]', '', text)  # Remove leading punct
    text = re.sub(r'\s*[,;]\s*$', '', text)  # Remove trailing punct
    
    # Fix spacing around remaining punctuation
    text = re.sub(r'\s*([.!?])\s*', r'\1 ', text)
    text = re.sub(r'\s*,\s*', ', ', text)
    
    return text.strip() 