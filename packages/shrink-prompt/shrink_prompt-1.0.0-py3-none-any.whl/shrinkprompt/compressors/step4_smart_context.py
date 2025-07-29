"""Step 4: Smart Context Removal - Advanced linguistic analysis and context-aware compression."""

import re
from typing import List, Set


# Articles and determiners (safe to remove in most contexts)
_ARTICLES = {"the", "a", "an", "that", "this", "these", "those"}

# Qualifiers that can often be removed without loss of meaning (expanded)
_QUALIFIERS = {
    "detailed", "comprehensive", "complete", "specific", "particular",
    "various", "different", "certain", "some", "any", "all", "every",
    "most", "many", "several", "few", "little", "much", "more", "less",
    "entire", "whole", "full", "partial", "total", "overall", "general",
    "main", "primary", "secondary", "additional", "extra", "further",
    "other", "another", "similar", "same", "different", "unique", "special",
    "normal", "regular", "standard", "typical", "common", "usual", "ordinary",
    "basic", "simple", "complex", "advanced", "sophisticated", "elaborate",
    "extensive", "broad", "wide", "narrow", "limited", "restricted",
    "appropriate", "suitable", "relevant", "applicable", "related", "associated",
    "corresponding", "respective", "individual", "personal", "specific",
    "particular", "exact", "precise", "accurate", "correct", "proper",
    "adequate", "sufficient", "enough", "necessary", "required", "essential",
    "important", "significant", "major", "minor", "slight", "small", "large",
    "huge", "enormous", "massive", "tiny", "minimal", "maximum", "minimum",
    "optimal", "best", "worst", "better", "worse", "good", "bad", "excellent",
    "poor", "high", "low", "top", "bottom", "first", "last", "initial", "final"
}

# Context-aware article removal patterns using lookaheads/lookbehinds
_CONTEXT_AWARE_ARTICLE_PATTERNS = {
    # Remove "a" but NOT if:
    # - Followed by capitalized word (proper noun/title): "A Star is Born"
    # - Part of technical terms: "A* algorithm", "A priori"
    # - At sentence start: "A new approach..."
    "a": r'\ba\b(?!\s+[A-Z*]|(?:\s+priori|\s+posteriori|\s+lot\s+of|\s+number\s+of))',
    
    # Remove "an" but NOT if:
    # - Followed by capitalized word
    # - Part of technical terms
    "an": r'\ban\b(?!\s+[A-Z]|(?:\s+algorithm|\s+approach|\s+analysis|\s+application))',
    
    # Remove "the" but NOT if:
    # - Followed by capitalized word (proper noun): "The Matrix", "The Beatles"
    # - Part of technical terms: "The Algorithm", "The Internet"
    # - Part of superlatives: "the best", "the most"
    # - At sentence start
    "the": r'(?<!^)\bthe\b(?!\s+[A-Z]|(?:\s+(?:best|worst|most|least|first|last|only|same|following|above|below|next|previous|main|primary|key|core|central)(?:\s|$)))',
}

# Context-aware qualifier removal patterns
_CONTEXT_AWARE_QUALIFIER_PATTERNS = {
    # Remove qualifiers but NOT if:
    # - Part of proper nouns: "Big Data", "Deep Learning", "New York"
    # - Part of technical terms: "high performance", "low latency"
    # - Before important technical words
    qualifier: rf'\b{re.escape(qualifier)}\b(?!\s+(?:[A-Z][a-z]+|Data|Learning|York|Performance|Latency|Quality|Security|System|Network|Database|Algorithm|Model|Analysis|Research|Study|Method|Approach))'
    for qualifier in _QUALIFIERS
}

# Advanced template patterns for common prompt structures
_TEMPLATE_PATTERNS = {
    # Polite request templates (expanded) - with negative lookaheads to preserve important phrases
    r"I would (?:really )?(?:appreciate|like|love|prefer) (?:it )?if you (?:could|would|might)(?!\s+(?:explain|clarify|help\s+me\s+understand))": "",
    r"(?:Could|Would|Might) you (?:be so kind as to|kindly|please|possibly)(?!\s+(?:explain|clarify|help))": "",
    r"I (?:was )?(?:hoping|wondering) (?:if )?you (?:could|would|might)(?!\s+(?:explain|clarify|help))": "",
    r"(?:Would it be possible|Is it possible|Could it be possible) (?:for you )?to(?!\s+(?:explain|clarify|understand))": "",
    r"(?:Do you think|Would you say) (?:it's possible|you could)(?!\s+(?:explain|help))": "",
    r"I was (?:hoping|wondering) (?:if )?(?:you could|it would be possible)(?!\s+(?:explain|help))": "",
    
    # Background/context introductions (expanded) - preserve when followed by technical terms
    r"(?:Let me|Allow me to) (?:give you|provide|offer) (?:some )?(?:background|context|information)(?!\s+(?:about|on|regarding))": "",
    r"(?:For|To give you) (?:some )?(?:context|background|perspective)(?!\s+(?:about|on|regarding))": "",
    r"(?:In order to|To|So as to) (?:better )?(?:understand|comprehend|grasp)": "To understand",
    r"(?:Before (?:we|I) (?:begin|start|continue)|To start with|First)(?!\s+(?:let|you))": "",
    r"(?:Let me (?:start by|begin by)|I'll start by|I'll begin by)(?!\s+(?:explaining|saying))": "",
    
    # Redundant emphasis (expanded) - preserve when emphasizing technical concepts
    r"It is (?:very |quite |extremely )?(?:important|crucial|essential|vital|critical) (?:to note |to mention |to remember )?that(?!\s+(?:this|these|the))": "",
    r"(?:Please )?(?:note|keep in mind|remember|bear in mind) that(?!\s+(?:this|these|the))": "",
    r"You (?:should|need to|must|ought to) (?:know|understand|be aware|realize) that(?!\s+(?:this|these|the))": "",
    r"(?:I want to|I need to|I should) (?:emphasize|stress|highlight) that(?!\s+(?:this|these|the))": "",
    r"(?:It's worth|It is worth) (?:noting|mentioning|pointing out) that(?!\s+(?:this|these|the))": "",
    r"(?:I think|I believe|I feel) (?:it's important|it's worth noting) that(?!\s+(?:this|these|the))": "",
    
    # Closing/summary patterns (expanded)
    r"(?:In )?(?:summary|conclusion|short|closing)": "",
    r"(?:To )?(?:sum up|summarize|conclude|wrap up)": "",
    r"(?:Overall|All in all|In general|On the whole|By and large)": "",
    r"(?:At the end of the day|When all is said and done|Bottom line)": "",
    r"(?:In the final analysis|Ultimately|Finally)": "",
    
    # Question/request patterns - preserve when asking about specific technical topics
    r"(?:I have a question about|I'm curious about|I'd like to know about)(?!\s+(?:how|what|when|where|why))": "About",
    r"(?:Can you tell me|Could you explain|Would you clarify)(?!\s+(?:how|what|when|where|why))": "Explain",
    r"(?:I'm interested in|I'd like to learn about|I want to understand)(?!\s+(?:how|what|when|where|why))": "About",
    
    # Uncertainty and hedging patterns - preserve when expressing technical uncertainty
    r"(?:I think|I believe|I guess|I suppose|I imagine) (?:that )?(?!\s+(?:this|these|the|it))": "",
    r"(?:It seems|It appears|It looks) (?:like |that |as if )(?!\s+(?:this|these|the|it))": "",
    r"(?:Perhaps|Maybe|Possibly|Presumably|Apparently)(?!\s+(?:this|these|the|it))": "",
    r"(?:Sort of|Kind of|More or less|To some extent)(?!\s+(?:like|similar))": "",
    
    # Meta-conversational patterns
    r"(?:As I (?:mentioned|said|noted) (?:before|earlier)|As mentioned (?:before|earlier))": "",
    r"(?:Going back to|Returning to|Back to) (?:what I said|my earlier point)": "",
    r"(?:To (?:put it|phrase it) (?:differently|another way)|In other words)": "",
    r"(?:What I mean (?:is|to say)|What I'm (?:trying to say|getting at))": "",
}

# Advanced linguistic simplifications with context awareness
_LINGUISTIC_SIMPLIFICATIONS = {
    # Passive to active voice patterns (comprehensive) - preserve technical terms
    r"is (?:being )?(?:used|utilized|employed|implemented|applied) by(?!\s+(?:the\s+)?(?:system|algorithm|method|approach))": "uses",
    r"(?:are|were) (?:being )?(?:used|utilized|employed|implemented|applied) by(?!\s+(?:the\s+)?(?:systems|algorithms|methods|approaches))": "use",
    r"(?:can|will|should|must) be (?:done|performed|executed|completed|finished) by(?!\s+(?:the\s+)?(?:system|algorithm))": "can do",
    r"is (?:being )?(?:developed|created|built|constructed|designed) by(?!\s+(?:the\s+)?(?:team|company|organization))": "builds",
    r"(?:are|were) (?:being )?(?:developed|created|built|constructed|designed) by(?!\s+(?:the\s+)?(?:teams|companies|organizations))": "build",
    r"is (?:being )?(?:written|authored|composed) by(?!\s+(?:the\s+)?(?:author|team))": "writes",
    r"(?:are|were) (?:being )?(?:written|authored|composed) by(?!\s+(?:the\s+)?(?:authors|teams))": "write",
    r"is (?:being )?(?:managed|handled|maintained) by(?!\s+(?:the\s+)?(?:team|system))": "manages",
    r"(?:are|were) (?:being )?(?:managed|handled|maintained) by(?!\s+(?:the\s+)?(?:teams|systems))": "manage",
    r"is (?:being )?(?:tested|examined|evaluated) by(?!\s+(?:the\s+)?(?:team|system))": "tests",
    r"(?:are|were) (?:being )?(?:tested|examined|evaluated) by(?!\s+(?:the\s+)?(?:teams|systems))": "test",
    
    # Wordy constructions (expanded) - with context preservation
    r"(?:in the process of|currently|presently|right now) (?:working on|developing|creating)(?!\s+(?:a|an|the))": "developing",
    r"(?:in the middle of|currently|at the moment) (?:trying to|attempting to|working to)(?!\s+(?:understand|solve|fix))": "trying to",
    r"(?:have the ability to|are able to|are capable of|can|are in a position to)(?!\s+(?:provide|offer|support))": "can",
    r"(?:make use of|utilize|employ|take advantage of)(?!\s+(?:advanced|sophisticated|complex))": "use",
    r"\b(?:carry out|perform|execute|conduct|undertake)\b(?!\s+(?:analysis|research|testing))": "do",
    r"(?:bring about|cause|result in|lead to|give rise to)(?!\s+(?:significant|major|important))": "cause",
    r"(?:take place|occur|happen|come about)(?!\s+(?:during|after|before))": "happen",
    r"(?:come to a decision|reach a decision|make a decision)(?!\s+(?:about|regarding))": "decide",
    r"(?:give consideration to|take into consideration|consider carefully)(?!\s+(?:all|various|multiple))": "consider",
    r"(?:make an attempt|try to|attempt to|endeavor to)(?!\s+(?:understand|solve|explain))": "try",
    r"(?:put forward|present|offer|propose|suggest)(?!\s+(?:a|an|the))": "suggest",
    r"(?:come to an end|finish|conclude|terminate)(?!\s+(?:the|this|that))": "end",
    r"(?:get started|begin|commence|initiate)(?!\s+(?:the|this|with))": "start",
    r"(?:keep track of|monitor|observe|watch)(?!\s+(?:the|this|all))": "track",
    r"(?:get in touch with|contact|reach out to)(?!\s+(?:the|our|your))": "contact",
    r"(?:take a look at|examine|inspect|review)(?!\s+(?:the|this|all))": "check",
    r"(?:have a conversation|talk|discuss|speak)(?!\s+(?:about|regarding|with))": "discuss",
    r"(?:make a comparison|compare|contrast)(?!\s+(?:the|different|various))": "compare",
    r"(?:give assistance|help|assist|aid)(?!\s+(?:with|in|users))": "help",
    r"(?:provide support|support|back|assist)(?!\s+(?:for|to|users))": "support",
    r"(?:give information|inform|tell|notify)(?!\s+(?:about|users|customers))": "inform",
    r"(?:make a request|request|ask for)(?!\s+(?:assistance|help|support))": "request",
    r"(?:give permission|allow|permit|authorize)(?!\s+(?:access|users|customers))": "allow",
    r"(?:make a change|change|alter|modify)(?!\s+(?:the|this|settings))": "change",
    r"(?:give an explanation|explain|clarify|elaborate)(?!\s+(?:how|why|what))": "explain",
    
    # Redundant prepositional phrases - preserve technical contexts
    r"(?:with regard to|with respect to|in regard to|in respect to|concerning|regarding)(?!\s+(?:the|this|your|our))": "about",
    r"(?:in connection with|in relation to|in association with)(?!\s+(?:the|this|our))": "about",
    r"(?:for the purpose of|with the purpose of|with the intention of)(?!\s+(?:providing|ensuring|maintaining))": "to",
    r"(?:in the event that|in case|if it happens that)(?!\s+(?:the|you|we))": "if",
    r"(?:during the time that|at the time when|while)(?!\s+(?:the|you|we))": "when",
    r"(?:in spite of the fact that|despite the fact that|although)(?!\s+(?:the|this))": "despite",
    r"(?:due to the fact that|because of the fact that|owing to)(?!\s+(?:the|this))": "because",
    r"(?:by means of|through the use of|by way of)(?!\s+(?:the|this|advanced))": "by",
    r"(?:in the course of|during the course of|in the process of)(?!\s+(?:the|this|our))": "during",
    r"(?:on the basis of|based on|according to)(?!\s+(?:the|this|our))": "based on",
    r"(?:for the reason that|on account of|as a result of)(?!\s+(?:the|this))": "because",
    
    # Question constructions (expanded) - preserve specific technical questions
    r"(?:What is|What are) the (?:best )?(?:way|method|approach|means) (?:to|for)(?!\s+(?:implement|achieve|ensure))": "How to",
    r"(?:How can I|How do I|What should I do to|What's the best way to)(?!\s+(?:implement|configure|setup))": "How to",
    r"(?:Is there a way to|Is it possible to|Can I)(?!\s+(?:configure|setup|implement))": "How to",
    r"(?:What would be the best|What's the ideal|What's the optimal) (?:way|method|approach)(?!\s+(?:to|for))": "How to",
    r"(?:I need to know how|I want to know how|Tell me how)(?!\s+(?:to|I))": "How",
    r"(?:Can you show me|Will you show me|Could you demonstrate)(?!\s+(?:how|the))": "Show",
    r"(?:I'd like to understand|Help me understand|Explain to me)(?!\s+(?:how|why|what))": "Explain",
    
    # Time and sequence simplifications - preserve technical timing references
    r"(?:at this point in time|at the present time|at this moment)(?!\s+(?:in|during|the))": "now",
    r"(?:in the near future|in the not too distant future|before long)(?!\s+(?:we|the|this))": "soon",
    r"(?:at an earlier point in time|at a previous time|previously)(?!\s+(?:mentioned|discussed|established))": "earlier",
    r"(?:during the same time period|at the same time|simultaneously)(?!\s+(?:as|with|the))": "together",
    r"(?:prior to|before|in advance of)(?!\s+(?:the|this|implementing))": "before",
    r"(?:subsequent to|following|after)(?!\s+(?:the|this|completing))": "after",
    r"(?:in the aftermath of|as a result of|following)(?!\s+(?:the|this|implementation))": "after",
}

# Wordiness patterns that can be simplified - with context preservation
_WORDINESS_PATTERNS = {
    # Redundant expressions - preserve when part of technical terms
    r"\bfree gift\b(?!\s+(?:card|offer))": "gift",
    r"\bfinal outcome\b(?!\s+(?:of|will))": "outcome", 
    r"\badvance planning\b(?!\s+(?:phase|stage))": "planning",
    r"\bfuture plans\b(?!\s+(?:include|involve))": "plans",
    r"\bpast history\b(?!\s+(?:shows|indicates))": "history",
    r"\bendemic crisis\b(?!\s+(?:response|management))": "crisis",
    r"\bunexpected surprise\b(?!\s+(?:attack|event))": "surprise",
    r"\bunique difference\b(?!\s+(?:between|is))": "difference",
    r"\bexact same\b(?!\s+(?:time|way|method))": "same",
    r"\bcompletely eliminate\b(?!\s+(?:the|all|any))": "eliminate",
    r"\btotally destroy\b(?!\s+(?:the|all|any))": "destroy",
    r"\bunanimous consensus\b(?!\s+(?:was|is))": "consensus",
    r"\bgeneral public\b(?!\s+(?:health|safety|interest))": "public",
    r"\bbasic fundamentals\b(?!\s+(?:of|include))": "fundamentals",
    r"\beach individual\b(?!\s+(?:user|case|instance))": "each",
    r"\bevery single\b(?!\s+(?:user|case|instance))": "every",
    r"\bsum total\b(?!\s+(?:of|is))": "total",
    r"\bend result\b(?!\s+(?:of|is|will))": "result",
    r"\bfinal destination\b(?!\s+(?:of|is))": "destination",
    r"\binitial beginning\b(?!\s+(?:of|phase))": "beginning",
    r"\btrue facts\b(?!\s+(?:about|are))": "facts",
    r"\brevert back\b(?!\s+(?:to|when))": "revert",
    r"\breturn back\b(?!\s+(?:to|when))": "return",
    r"\brepeat again\b(?!\s+(?:the|this))": "repeat",
    r"\bcontinue on\b(?!\s+(?:with|to))": "continue",
    r"\bproceeed forward\b(?!\s+(?:with|to))": "proceed",
    r"\badvance forward\b(?!\s+(?:with|to))": "advance",
    r"\bdescend down\b(?!\s+(?:the|to))": "descend",
    r"\bascend up\b(?!\s+(?:the|to))": "ascend",
    r"\bconnect together\b(?!\s+(?:with|to))": "connect",
    r"\bcombine together\b(?!\s+(?:with|to))": "combine",
    r"\bmerge together\b(?!\s+(?:with|to))": "merge",
    r"\bunite together\b(?!\s+(?:with|to))": "unite",
    r"\bjoin together\b(?!\s+(?:with|to))": "join",
    r"\blink together\b(?!\s+(?:with|to))": "link",
    r"\bcooperate together\b(?!\s+(?:with|to))": "cooperate",
    r"\bcollaborate together\b(?!\s+(?:with|to))": "collaborate",
    
    # Verbose expressions - preserve technical contexts
    r"\ba large number of\b(?!\s+(?:users|systems|algorithms))": "many",
    r"\ba great deal of\b(?!\s+(?:data|information|complexity))": "much",
    r"\ba majority of\b(?!\s+(?:users|systems|cases))": "most",
    r"\ba small number of\b(?!\s+(?:users|systems|cases))": "few",
    r"\ban adequate amount of\b(?!\s+(?:data|memory|storage))": "enough",
    r"\bin a timely manner\b(?!\s+(?:to|for))": "promptly",
    r"\bin close proximity\b(?!\s+(?:to|of))": "near",
    r"\bat this point in time\b(?!\s+(?:the|we))": "now",
    r"\bfor the purpose of\b(?!\s+(?:ensuring|providing|maintaining))": "to",
    r"\bwith the exception of\b(?!\s+(?:the|this|certain))": "except",
    r"\bin the event that\b(?!\s+(?:the|you|we))": "if",
    r"\bunder circumstances where\b(?!\s+(?:the|you|we))": "when",
    r"\bin situations where\b(?!\s+(?:the|you|we))": "when",
    r"\bunder conditions where\b(?!\s+(?:the|you|we))": "when",
    r"\bin instances where\b(?!\s+(?:the|you|we))": "when",
    r"\bin cases where\b(?!\s+(?:the|you|we))": "when",
    r"\bat times when\b(?!\s+(?:the|you|we))": "when",
    r"\bduring periods when\b(?!\s+(?:the|you|we))": "when",
    r"\bon occasions when\b(?!\s+(?:the|you|we))": "when",
    r"\bin moments when\b(?!\s+(?:the|you|we))": "when",
    
    # Business jargon - preserve when part of official terms
    r"\bleverage\b(?!\s+(?:existing|advanced|enterprise))": "use",
    r"\bsynergize\b(?!\s+(?:with|across|multiple))": "combine",
    r"\boptimize\b(?!\s+(?:performance|efficiency|costs))": "improve",
    r"\bstreamline\b(?!\s+(?:processes|operations|workflows))": "simplify",
    r"\benhance\b(?!\s+(?:performance|security|user))": "improve",
    r"\bfacilitate\b(?!\s+(?:communication|collaboration|integration))": "help",
    r"\bimplement\b(?!\s+(?:solutions|systems|features))": "do",
    r"\binitiate\b(?!\s+(?:processes|procedures|workflows))": "start",
    r"\bterminate\b(?!\s+(?:processes|connections|sessions))": "end",
    r"\butilize\b(?!\s+(?:advanced|existing|available))": "use",
    r"\bdemonstrate\b(?!\s+(?:capabilities|features|functionality))": "show",
    r"\baccomplish\b(?!\s+(?:objectives|goals|tasks))": "do",
    r"\bassist\b(?!\s+(?:users|customers|teams))": "help",
    r"\bobtain\b(?!\s+(?:access|permissions|credentials))": "get",
    r"\bacquire\b(?!\s+(?:resources|assets|capabilities))": "get",
    r"\bpurchase\b(?!\s+(?:licenses|subscriptions|services))": "buy",
    r"\bprocure\b(?!\s+(?:resources|services|equipment))": "get",
    r"\brequest\b(?!\s+(?:access|permissions|support))": "ask",
    r"\binquire\b(?!\s+(?:about|regarding|concerning))": "ask",
    r"\bexamine\b(?!\s+(?:the|this|all))": "check",
    r"\binvestigate\b(?!\s+(?:the|this|all))": "check",
    r"\banalyze\b(?!\s+(?:the|this|data))": "study",
    r"\bevaluate\b(?!\s+(?:the|this|options))": "assess",
    r"\bdetermine\b(?!\s+(?:the|how|what))": "find",
    r"\bascertain\b(?!\s+(?:the|how|what))": "find",
}

# Redundant construction patterns with context awareness
_REDUNDANT_CONSTRUCTIONS = {
    # "There is/are" constructions that can be simplified - preserve technical contexts
    r"\bthere (?:is|are) (?:a |an |some |many |several |few )?(?!\s*(?:evidence|data|information|research|analysis))": "",
    r"\bthere (?:was|were) (?:a |an |some |many |several |few )?(?!\s*(?:evidence|data|information|research|analysis))": "",
    r"\bthere will be (?:a |an |some |many |several |few )?(?!\s*(?:changes|updates|improvements))": "",
    r"\bthere can be (?:a |an |some |many |several |few )?(?!\s*(?:issues|problems|conflicts))": "",
    r"\bthere might be (?:a |an |some |many |several |few )?(?!\s*(?:issues|problems|conflicts))": "",
    r"\bthere should be (?:a |an |some |many |several |few )?(?!\s*(?:validation|verification|testing))": "",
    
    # "It is" constructions - preserve when making technical assertions
    r"\bit is (?:a |an |the )?fact that(?!\s*(?:this|the|performance))": "",
    r"\bit is (?:true |clear |obvious |evident ) that(?!\s*(?:this|the|performance))": "",
    r"\bit is (?:possible |likely |probable ) that(?!\s*(?:this|the|performance))": "",
    r"\bit is (?:important |necessary |essential ) that(?!\s*(?:this|the|you))": "",
    
    # Redundant "that" clauses - preserve when introducing technical concepts
    r"\b(?:the fact|the reality|the truth) that\b(?!\s*(?:this|the|performance))": "",
    r"\b(?:the idea|the concept|the notion) that\b(?!\s*(?:this|the|users))": "",
    r"\b(?:the possibility|the chance|the likelihood) that\b(?!\s*(?:this|the|users))": "",
    
    # Wordy connectors - preserve technical connections
    r"\bin addition to the fact that\b(?!\s*(?:this|the|performance))": "and",
    r"\bas well as the fact that\b(?!\s*(?:this|the|performance))": "and", 
    r"\balong with the fact that\b(?!\s*(?:this|the|performance))": "and",
    r"\bnot to mention the fact that\b(?!\s*(?:this|the|performance))": "and",
    r"\bin spite of the fact that\b(?!\s*(?:this|the|performance))": "despite",
    r"\bdespite the fact that\b(?!\s*(?:this|the|performance))": "despite",
    r"\bregardless of the fact that\b(?!\s*(?:this|the|performance))": "despite",
}

# Advanced prompt templates
_ADVANCED_TEMPLATES = {
    # Question patterns
    r"^(?:Can you |Could you |Would you |Will you )?(?:please )?(?:help me )?(.+?)(?:\?|$)": r"\1?",
    
    # Instruction patterns  
    r"^(?:I need you to |I want you to |Please )?(.+?)(?:\.|$)": r"\1",
    
    # Math problem intro removal
    r"^(?:Here's a|This is a|Consider this|Look at this) (?:math )?(?:problem|question|scenario):\s*": "",
    
    # Context setup removal
    r"^(?:Let's say|Imagine|Suppose|Assume) (?:that )?": "",
}


def smart_context_removal(text: str) -> str:
    """Step 4: Apply advanced smart context-aware removals with lookaheads/lookbehinds.
    
    Args:
        text: Input text to process
        
    Returns:
        Text with sophisticated context-aware compression applied
    """
    # Apply template pattern removal first
    for pattern, replacement in _TEMPLATE_PATTERNS.items():
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    
    # Apply redundant construction removal
    for pattern, replacement in _REDUNDANT_CONSTRUCTIONS.items():
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    
    # Apply wordiness pattern simplification
    for pattern, replacement in _WORDINESS_PATTERNS.items():
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    
    # Apply advanced linguistic simplifications
    for pattern, replacement in _LINGUISTIC_SIMPLIFICATIONS.items():
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    
    # Context-aware article removal using lookaheads/lookbehinds
    for article, pattern in _CONTEXT_AWARE_ARTICLE_PATTERNS.items():
        text = re.sub(pattern, '', text, flags=re.IGNORECASE)
    
    # Context-aware qualifier removal
    for qualifier, pattern in _CONTEXT_AWARE_QUALIFIER_PATTERNS.items():
        text = re.sub(pattern, '', text, flags=re.IGNORECASE)
    
    # Advanced simplifications with context preservation
    
    # Remove redundant "that" in various contexts - preserve technical contexts
    text = re.sub(r'\b(?:ensure|make sure|verify|confirm|guarantee) that\b(?!\s+(?:the|this|all))', r'ensure', text, flags=re.IGNORECASE)
    text = re.sub(r'\b(believe|think|feel|know|realize|understand) that\b(?!\s+(?:the|this|it))', r'\1', text, flags=re.IGNORECASE)
    text = re.sub(r'\b(say|claim|argue|suggest|propose|recommend) that\b(?!\s+(?:the|this|we))', r'\1', text, flags=re.IGNORECASE)
    text = re.sub(r'\b(hope|expect|assume|presume|suppose) that\b(?!\s+(?:the|this|you))', r'\1', text, flags=re.IGNORECASE)
    
    # Simplify "there is/are" constructions (remaining ones) - preserve technical contexts
    text = re.sub(r'\bthere (?:is|are)\s+(?!\s*(?:evidence|data|research|no|a\s+(?:need|requirement|possibility)))', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\bthere (?:was|were)\s+(?!\s*(?:evidence|data|research|no|a\s+(?:need|requirement|possibility)))', '', text, flags=re.IGNORECASE)
    
    # Remove redundant prepositions and articles - preserve technical contexts
    text = re.sub(r'\bof the\b(?!\s+(?:system|algorithm|method|approach|same|following))', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\bin the\b(?=\s+(?:process|context|case|event|situation|instance|course|midst|wake|light))(?!\s+(?:system|algorithm))', 'in', text, flags=re.IGNORECASE)
    text = re.sub(r'\bon the\b(?=\s+(?:other hand|contrary|basis|grounds))(?!\s+(?:system|network))', 'on', text, flags=re.IGNORECASE)
    text = re.sub(r'\bto the\b(?=\s+(?:extent|degree|point))(?!\s+(?:system|algorithm))', 'to', text, flags=re.IGNORECASE)
    
    # Remove redundant intensifiers in specific contexts - preserve technical emphasis
    text = re.sub(r'\b(?:very|really|quite|rather|fairly|pretty)\s+(?:important|necessary|essential|critical|vital)\b(?!\s+(?:for|to|in)\s+(?:system|performance|security))', 
                  lambda m: m.group(0).split()[-1], text, flags=re.IGNORECASE)
    
    # Simplify comparative constructions - preserve technical comparisons
    text = re.sub(r'\bmore (?:important|significant|relevant|useful|effective) than\b(?!\s+(?:other|alternative|previous))', 'better than', text, flags=re.IGNORECASE)
    text = re.sub(r'\bless (?:important|significant|relevant|useful|effective) than\b(?!\s+(?:other|alternative|previous))', 'worse than', text, flags=re.IGNORECASE)
    
    # Clean up artifacts and normalize spacing
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'\s*,\s*,', ',', text)
    text = re.sub(r'\s*\.\s*\.', '.', text)
    text = re.sub(r'^\s*[,.]', '', text)
    text = re.sub(r'\s*[,;]\s*$', '', text)
    
    # Fix spacing around punctuation
    text = re.sub(r'\s*([.!?])\s*', r'\1 ', text)
    text = re.sub(r'\s*,\s*', ', ', text)
    text = re.sub(r'\s*;\s*', '; ', text)
    text = re.sub(r'\s*:\s*', ': ', text)
    
    # Remove double spaces and trim
    text = re.sub(r'\s{2,}', ' ', text)
    
    return text.strip() 