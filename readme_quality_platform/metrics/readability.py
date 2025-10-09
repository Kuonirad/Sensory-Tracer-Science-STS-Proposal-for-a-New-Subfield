"""
Comprehensive Readability Analysis Implementation

Implements all major readability formulas adapted for technical documentation:
- Flesch Reading Ease (1948) 
- Flesch-Kincaid Grade Level (1975)
- Gunning Fog Index (1952)
- SMOG Index (1969) 
- Dale-Chall Readability Score (1948)
- Automated Readability Index (1967)
- Coleman-Liau Index
- Linsear Write Formula

Based on computational linguistics research and established educational metrics.
"""

import re
import math
from typing import List, Dict, Set, Tuple
import nltk
from nltk.corpus import cmudict
from nltk.tokenize import sent_tokenize, word_tokenize
import textstat

from ..core.models import ReadabilityMetrics


class ReadabilityAnalyzer:
    """
    Advanced readability analysis using multiple established formulas.
    
    Provides comprehensive linguistic analysis suitable for technical documentation
    with special handling for code blocks, technical terms, and markdown formatting.
    """
    
    def __init__(self):
        """Initialize analyzer with required NLTK resources."""
        self._ensure_nltk_data()
        self._load_dale_chall_words()
        self._syllable_dict = None
        
    def _ensure_nltk_data(self) -> None:
        """Download required NLTK data if not present."""
        try:
            nltk.data.find('tokenizers/punkt')
            nltk.data.find('corpora/cmudict')
        except LookupError:
            nltk.download('punkt', quiet=True)
            nltk.download('cmudict', quiet=True)
            
    def _load_dale_chall_words(self) -> None:
        """Load Dale-Chall familiar words list."""
        # Simplified Dale-Chall word list (3000 most common words)
        # In production, this would load from the complete 3000-word list
        self.dale_chall_words = set([
            'a', 'able', 'about', 'above', 'accept', 'across', 'act', 'action',
            'activity', 'actually', 'add', 'address', 'administration', 'admit',
            'adult', 'affect', 'after', 'again', 'against', 'age', 'agency',
            'agent', 'ago', 'agree', 'agreement', 'ahead', 'air', 'all',
            'allow', 'almost', 'alone', 'along', 'already', 'also', 'although',
            'always', 'american', 'among', 'amount', 'analysis', 'and', 'animal',
            'another', 'answer', 'any', 'anyone', 'anything', 'appear', 'apply',
            'approach', 'area', 'argue', 'arm', 'around', 'arrive', 'art',
            'article', 'artist', 'as', 'ask', 'assume', 'at', 'attack',
            'attention', 'attorney', 'audience', 'author', 'authority', 'available',
            'avoid', 'away', 'baby', 'back', 'bad', 'bag', 'ball', 'bank',
            'bar', 'base', 'be', 'beat', 'beautiful', 'because', 'become',
            'bed', 'before', 'begin', 'behavior', 'behind', 'believe', 'benefit',
            'best', 'better', 'between', 'beyond', 'big', 'bill', 'billion',
            'bit', 'black', 'blood', 'blue', 'board', 'body', 'book', 'born',
            'both', 'box', 'boy', 'break', 'bring', 'brother', 'budget',
            'build', 'building', 'business', 'but', 'buy', 'by', 'call',
            'camera', 'campaign', 'can', 'cancer', 'candidate', 'capital',
            'car', 'card', 'care', 'career', 'carry', 'case', 'catch',
            'cause', 'cell', 'center', 'central', 'century', 'certain',
            'certainly', 'chair', 'challenge', 'chance', 'change', 'character',
            'charge', 'check', 'child', 'choice', 'choose', 'church', 'citizen',
            'city', 'civil', 'claim', 'class', 'clear', 'clearly', 'close',
            'coach', 'cold', 'collection', 'college', 'color', 'come',
            'commercial', 'common', 'community', 'company', 'compare', 'computer',
            'concept', 'concern', 'condition', 'conference', 'congress',
            'consider', 'consumer', 'contain', 'continue', 'control', 'cost',
            'could', 'country', 'couple', 'course', 'court', 'cover', 'create',
            'crime', 'cultural', 'culture', 'cup', 'current', 'customer',
            'cut', 'dark', 'data', 'daughter', 'day', 'dead', 'deal', 'death',
            'debate', 'decade', 'decide', 'decision', 'deep', 'defense',
            'degree', 'democrat', 'democratic', 'describe', 'design', 'despite',
            'detail', 'determine', 'develop', 'development', 'die', 'difference',
            'different', 'difficult', 'dinner', 'direction', 'director',
            'discover', 'discuss', 'discussion', 'disease', 'do', 'doctor',
            'dog', 'door', 'down', 'draw', 'dream', 'drive', 'drop', 'drug',
            'during', 'each', 'early', 'east', 'easy', 'eat', 'economic',
            'economy', 'edge', 'education', 'effect', 'effort', 'eight',
            'either', 'election', 'else', 'employee', 'end', 'energy',
            'enjoy', 'enough', 'enter', 'entire', 'environment', 'environmental',
            'especially', 'establish', 'even', 'evening', 'event', 'ever',
            'every', 'everybody', 'everyone', 'everything', 'evidence',
            'exactly', 'example', 'executive', 'exist', 'expect', 'experience',
            'expert', 'explain', 'eye', 'face', 'fact', 'factor', 'fail',
            'fall', 'family', 'far', 'fast', 'father', 'fear', 'federal',
            'feel', 'feeling', 'few', 'field', 'fight', 'figure', 'fill',
            'film', 'final', 'finally', 'financial', 'find', 'fine', 'finger',
            'finish', 'fire', 'firm', 'first', 'fish', 'five', 'floor',
            'fly', 'focus', 'follow', 'food', 'foot', 'for', 'force',
            'foreign', 'forget', 'form', 'former', 'forward', 'four', 'free',
            'friend', 'from', 'front', 'full', 'fund', 'future', 'game',
            'garden', 'gas', 'general', 'generation', 'get', 'girl', 'give',
            'glass', 'go', 'goal', 'good', 'government', 'great', 'green',
            'ground', 'group', 'grow', 'growth', 'guess', 'gun', 'guy',
            'hair', 'half', 'hand', 'hang', 'happen', 'happy', 'hard',
            'have', 'he', 'head', 'health', 'hear', 'heart', 'heat',
            'heavy', 'help', 'her', 'here', 'herself', 'high', 'him',
            'himself', 'his', 'history', 'hit', 'hold', 'home', 'hope',
            'hospital', 'hot', 'hotel', 'hour', 'house', 'how', 'however',
            'huge', 'human', 'hundred', 'husband', 'i', 'idea', 'identify',
            'if', 'image', 'imagine', 'impact', 'important', 'improve', 'in',
            'include', 'including', 'increase', 'indeed', 'indicate', 'individual',
            'industry', 'information', 'inside', 'instead', 'institution',
            'interest', 'interesting', 'international', 'interview', 'into',
            'investment', 'involve', 'issue', 'it', 'item', 'its', 'itself',
            'job', 'join', 'just', 'keep', 'key', 'kid', 'kill', 'kind',
            'kitchen', 'know', 'knowledge', 'land', 'language', 'large',
            'last', 'late', 'later', 'laugh', 'law', 'lawyer', 'lay',
            'lead', 'leader', 'learn', 'least', 'leave', 'left', 'leg',
            'legal', 'less', 'let', 'letter', 'level', 'lie', 'life',
            'light', 'like', 'likely', 'line', 'list', 'listen', 'little',
            'live', 'local', 'long', 'look', 'lose', 'loss', 'lot', 'love',
            'low', 'machine', 'magazine', 'main', 'maintain', 'major',
            'majority', 'make', 'man', 'manage', 'management', 'manager',
            'many', 'market', 'marriage', 'material', 'matter', 'may',
            'maybe', 'me', 'mean', 'measure', 'media', 'medical', 'meet',
            'meeting', 'member', 'memory', 'mention', 'message', 'method',
            'middle', 'might', 'military', 'million', 'mind', 'minute',
            'miss', 'mission', 'model', 'modern', 'moment', 'money',
            'month', 'more', 'morning', 'most', 'mother', 'mouth', 'move',
            'movement', 'movie', 'mr', 'mrs', 'much', 'music', 'must',
            'my', 'myself', 'name', 'nation', 'national', 'natural',
            'nature', 'near', 'nearly', 'necessary', 'need', 'network',
            'never', 'new', 'news', 'newspaper', 'next', 'nice', 'night',
            'no', 'none', 'nor', 'north', 'not', 'note', 'nothing',
            'notice', 'now', 'number', 'occur', 'of', 'off', 'offer',
            'office', 'officer', 'official', 'often', 'oh', 'oil', 'ok',
            'old', 'on', 'once', 'one', 'only', 'onto', 'open', 'operation',
            'opportunity', 'option', 'or', 'order', 'organization', 'other',
            'others', 'our', 'out', 'outside', 'over', 'own', 'owner',
            'page', 'pain', 'painting', 'paper', 'parent', 'part', 'participant',
            'particular', 'particularly', 'partner', 'party', 'pass', 'past',
            'patient', 'pattern', 'pay', 'peace', 'people', 'per', 'perform',
            'performance', 'perhaps', 'period', 'person', 'personal', 'phone',
            'physical', 'pick', 'picture', 'piece', 'place', 'plan', 'plant',
            'play', 'player', 'pm', 'point', 'police', 'policy', 'political',
            'politics', 'poor', 'popular', 'population', 'position', 'positive',
            'possible', 'power', 'practice', 'prepare', 'present', 'president',
            'pressure', 'pretty', 'prevent', 'price', 'private', 'probably',
            'problem', 'process', 'produce', 'product', 'production', 'professional',
            'professor', 'program', 'project', 'property', 'protect', 'prove',
            'provide', 'public', 'pull', 'purpose', 'push', 'put', 'quality',
            'question', 'quickly', 'quite', 'race', 'radio', 'raise', 'range',
            'rate', 'rather', 'reach', 'read', 'ready', 'real', 'reality',
            'realize', 'really', 'reason', 'receive', 'recent', 'recently',
            'recognize', 'record', 'red', 'reduce', 'reflect', 'region',
            'relate', 'relationship', 'religious', 'remain', 'remember',
            'remove', 'report', 'represent', 'republican', 'require', 'research',
            'resource', 'respond', 'response', 'responsibility', 'rest',
            'result', 'return', 'reveal', 'rich', 'right', 'rise', 'risk',
            'road', 'rock', 'role', 'room', 'rule', 'run', 'safe', 'same',
            'save', 'say', 'scene', 'school', 'science', 'scientist', 'score',
            'sea', 'season', 'seat', 'second', 'section', 'security', 'see',
            'seek', 'seem', 'sell', 'send', 'senior', 'sense', 'series',
            'serious', 'serve', 'service', 'set', 'seven', 'several', 'sex',
            'sexual', 'shake', 'share', 'she', 'shoot', 'short', 'shot',
            'should', 'shoulder', 'show', 'side', 'significant', 'similar',
            'simple', 'simply', 'since', 'sing', 'single', 'sister', 'sit',
            'site', 'situation', 'six', 'size', 'skill', 'skin', 'small',
            'smile', 'so', 'social', 'society', 'soldier', 'some', 'somebody',
            'someone', 'something', 'sometimes', 'son', 'song', 'soon',
            'sort', 'sound', 'source', 'south', 'southern', 'space', 'speak',
            'special', 'specific', 'speech', 'spend', 'sport', 'spring',
            'staff', 'stage', 'stand', 'standard', 'star', 'start', 'state',
            'statement', 'station', 'stay', 'step', 'still', 'stock', 'stop',
            'store', 'story', 'strategy', 'street', 'strong', 'structure',
            'student', 'study', 'stuff', 'style', 'subject', 'success',
            'successful', 'such', 'suddenly', 'suffer', 'suggest', 'summer',
            'support', 'sure', 'surface', 'system', 'table', 'take', 'talk',
            'task', 'tax', 'teach', 'teacher', 'team', 'technology', 'television',
            'tell', 'ten', 'tend', 'term', 'test', 'than', 'thank', 'that',
            'the', 'their', 'them', 'themselves', 'then', 'theory', 'there',
            'these', 'they', 'thing', 'think', 'third', 'this', 'those',
            'though', 'thought', 'thousand', 'threat', 'three', 'through',
            'throughout', 'throw', 'thus', 'time', 'to', 'today', 'together',
            'tonight', 'too', 'top', 'total', 'tough', 'toward', 'town',
            'trade', 'traditional', 'training', 'travel', 'treat', 'treatment',
            'tree', 'trial', 'trip', 'trouble', 'true', 'truth', 'try',
            'turn', 'tv', 'two', 'type', 'under', 'understand', 'unit',
            'until', 'up', 'upon', 'us', 'use', 'used', 'user', 'usually',
            'value', 'various', 'very', 'victim', 'view', 'violence', 'visit',
            'voice', 'vote', 'wait', 'walk', 'wall', 'want', 'war', 'watch',
            'water', 'way', 'we', 'weapon', 'wear', 'week', 'weight', 'well',
            'west', 'western', 'what', 'whatever', 'when', 'where', 'whether',
            'which', 'while', 'white', 'who', 'whole', 'whom', 'whose',
            'why', 'wide', 'wife', 'will', 'win', 'wind', 'window', 'wish',
            'with', 'within', 'without', 'woman', 'wonder', 'word', 'work',
            'worker', 'world', 'worry', 'would', 'write', 'writer', 'wrong',
            'yard', 'yeah', 'year', 'yes', 'yet', 'you', 'young', 'your',
            'yourself'
        ])
    
    def analyze(self, text: str, clean_text: str = None) -> ReadabilityMetrics:
        """
        Perform comprehensive readability analysis.
        
        Args:
            text: Raw markdown text
            clean_text: Text with markdown formatting removed (optional)
            
        Returns:
            ReadabilityMetrics: Complete readability assessment
        """
        if clean_text is None:
            clean_text = self._clean_text_for_analysis(text)
        
        if not clean_text.strip():
            return ReadabilityMetrics()
            
        metrics = ReadabilityMetrics()
        
        # Basic text statistics
        sentences = self._get_sentences(clean_text)
        words = self._get_words(clean_text)
        
        metrics.sentence_count = len(sentences)
        metrics.word_count = len(words)
        metrics.character_count = len(clean_text)
        
        if metrics.word_count == 0:
            return metrics
            
        # Syllable analysis
        metrics.syllable_count = self._count_syllables(words)
        metrics.polysyllable_count = self._count_polysyllables(words)
        
        # Calculate all readability metrics
        metrics.flesch_reading_ease = self._flesch_reading_ease(
            metrics.sentence_count, metrics.word_count, metrics.syllable_count
        )
        
        metrics.flesch_kincaid_grade = self._flesch_kincaid_grade(
            metrics.sentence_count, metrics.word_count, metrics.syllable_count
        )
        
        metrics.gunning_fog = self._gunning_fog_index(
            metrics.sentence_count, metrics.word_count, metrics.polysyllable_count
        )
        
        metrics.smog_index = self._smog_index(
            metrics.sentence_count, metrics.polysyllable_count
        )
        
        metrics.dale_chall = self._dale_chall_score(words, metrics.sentence_count)
        
        metrics.automated_readability_index = self._ari(
            metrics.sentence_count, metrics.word_count, metrics.character_count
        )
        
        metrics.coleman_liau = self._coleman_liau_index(
            metrics.sentence_count, metrics.word_count, metrics.character_count
        )
        
        metrics.linsear_write = self._linsear_write_formula(
            sentences, metrics.sentence_count
        )
        
        # Calculate composite metrics
        grade_levels = [
            metrics.flesch_kincaid_grade,
            metrics.gunning_fog,
            metrics.smog_index,
            metrics.automated_readability_index,
            metrics.coleman_liau,
            metrics.linsear_write
        ]
        
        valid_grades = [g for g in grade_levels if g > 0]
        metrics.average_grade_level = (
            sum(valid_grades) / len(valid_grades) if valid_grades else 0
        )
        
        metrics.readability_consensus = self._determine_consensus(metrics)
        
        return metrics
    
    def _clean_text_for_analysis(self, text: str) -> str:
        """Remove markdown formatting and code blocks for readability analysis."""
        # Remove code blocks
        text = re.sub(r'```[\s\S]*?```', '', text)
        text = re.sub(r'`[^`]+`', '', text)
        
        # Remove markdown formatting
        text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)  # Links
        text = re.sub(r'!\[([^\]]*)\]\([^\)]+\)', '', text)     # Images
        text = re.sub(r'[*_]{1,2}([^*_]+)[*_]{1,2}', r'\1', text)  # Bold/italic
        text = re.sub(r'#{1,6}\s+', '', text)                  # Headers
        text = re.sub(r'>\s+', '', text)                       # Blockquotes
        text = re.sub(r'^\s*[-*+]\s+', '', text, flags=re.MULTILINE)  # Lists
        text = re.sub(r'^\s*\d+\.\s+', '', text, flags=re.MULTILINE)  # Numbered lists
        
        # Clean up HTML tags
        text = re.sub(r'<[^>]+>', '', text)
        
        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def _get_sentences(self, text: str) -> List[str]:
        """Tokenize text into sentences."""
        try:
            return sent_tokenize(text)
        except:
            # Fallback if NLTK fails
            sentences = re.split(r'[.!?]+', text)
            return [s.strip() for s in sentences if s.strip()]
    
    def _get_words(self, text: str) -> List[str]:
        """Tokenize text into words."""
        try:
            words = word_tokenize(text.lower())
            return [w for w in words if w.isalpha()]
        except:
            # Fallback if NLTK fails
            words = re.findall(r'\b[a-zA-Z]+\b', text.lower())
            return words
    
    def _count_syllables(self, words: List[str]) -> int:
        """Count total syllables in word list."""
        if self._syllable_dict is None:
            try:
                self._syllable_dict = cmudict.dict()
            except:
                self._syllable_dict = {}
        
        total_syllables = 0
        for word in words:
            syllables = self._syllables_in_word(word)
            total_syllables += syllables
            
        return total_syllables
    
    def _syllables_in_word(self, word: str) -> int:
        """Count syllables in a single word."""
        word = word.lower()
        
        # Try CMU dictionary first
        if self._syllable_dict and word in self._syllable_dict:
            pronunciations = self._syllable_dict[word]
            if pronunciations:
                # Count stress markers (0, 1, 2) in pronunciation
                return len([p for p in pronunciations[0] if p[-1].isdigit()])
        
        # Fallback syllable counting algorithm
        word = re.sub(r'[^a-z]', '', word)
        if len(word) <= 1:
            return 1 if word else 0
            
        # Count vowel groups
        vowels = 'aeiouy'
        syllables = 0
        prev_was_vowel = False
        
        for char in word:
            is_vowel = char in vowels
            if is_vowel and not prev_was_vowel:
                syllables += 1
            prev_was_vowel = is_vowel
        
        # Silent e rule
        if word.endswith('e') and syllables > 1:
            syllables -= 1
        
        # Minimum one syllable
        return max(1, syllables)
    
    def _count_polysyllables(self, words: List[str]) -> int:
        """Count words with 3+ syllables."""
        polysyllables = 0
        for word in words:
            if self._syllables_in_word(word) >= 3:
                polysyllables += 1
        return polysyllables
    
    def _flesch_reading_ease(self, sentences: int, words: int, syllables: int) -> float:
        """Calculate Flesch Reading Ease score (0-100, higher = easier)."""
        if sentences == 0 or words == 0:
            return 0.0
            
        asl = words / sentences  # Average sentence length
        asw = syllables / words  # Average syllables per word
        
        score = 206.835 - (1.015 * asl) - (84.6 * asw)
        return max(0, min(100, score))
    
    def _flesch_kincaid_grade(self, sentences: int, words: int, syllables: int) -> float:
        """Calculate Flesch-Kincaid Grade Level."""
        if sentences == 0 or words == 0:
            return 0.0
            
        asl = words / sentences
        asw = syllables / words
        
        grade = (0.39 * asl) + (11.8 * asw) - 15.59
        return max(0, grade)
    
    def _gunning_fog_index(self, sentences: int, words: int, polysyllables: int) -> float:
        """Calculate Gunning Fog Index."""
        if sentences == 0 or words == 0:
            return 0.0
            
        asl = words / sentences
        phw = (polysyllables / words) * 100  # Percentage of hard words
        
        fog = 0.4 * (asl + phw)
        return max(0, fog)
    
    def _smog_index(self, sentences: int, polysyllables: int) -> float:
        """Calculate SMOG Index."""
        if sentences < 3:
            return 0.0
            
        # SMOG = 1.0430 * sqrt(polysyllables * 30/sentences) + 3.1291
        smog = 1.0430 * math.sqrt(polysyllables * 30 / sentences) + 3.1291
        return max(0, smog)
    
    def _dale_chall_score(self, words: List[str], sentences: int) -> float:
        """Calculate Dale-Chall Readability Score."""
        if not words or sentences == 0:
            return 0.0
            
        # Count difficult words (not in Dale-Chall list)
        difficult_words = sum(1 for word in words if word not in self.dale_chall_words)
        pdw = (difficult_words / len(words)) * 100  # Percentage difficult words
        asl = len(words) / sentences  # Average sentence length
        
        # Base formula
        score = 0.1579 * pdw + 0.0496 * asl
        
        # Add adjustment if > 5% difficult words
        if pdw > 5:
            score += 3.6365
            
        return max(0, score)
    
    def _ari(self, sentences: int, words: int, characters: int) -> float:
        """Calculate Automated Readability Index."""
        if sentences == 0 or words == 0:
            return 0.0
            
        ari = 4.71 * (characters / words) + 0.5 * (words / sentences) - 21.43
        return max(0, ari)
    
    def _coleman_liau_index(self, sentences: int, words: int, characters: int) -> float:
        """Calculate Coleman-Liau Index."""
        if words == 0:
            return 0.0
            
        # Letters per 100 words
        l = (characters / words) * 100
        # Sentences per 100 words  
        s = (sentences / words) * 100
        
        cli = 0.0588 * l - 0.296 * s - 15.8
        return max(0, cli)
    
    def _linsear_write_formula(self, sentences: List[str], sentence_count: int) -> float:
        """Calculate Linsear Write Formula."""
        if sentence_count == 0:
            return 0.0
            
        easy_words = 0
        hard_words = 0
        
        for sentence in sentences[:100]:  # Use first 100 sentences max
            words = self._get_words(sentence)
            for word in words:
                if self._syllables_in_word(word) >= 3:
                    hard_words += 1
                else:
                    easy_words += 1
        
        if easy_words + hard_words == 0:
            return 0.0
            
        # Calculate score
        score = (easy_words + (hard_words * 3)) / sentence_count
        
        if score > 20:
            score = score / 2
        else:
            score = (score - 2) / 2
            
        return max(0, score)
    
    def _determine_consensus(self, metrics: ReadabilityMetrics) -> str:
        """Determine overall readability consensus based on multiple metrics."""
        avg_grade = metrics.average_grade_level
        
        if avg_grade <= 6:
            return "very easy"
        elif avg_grade <= 9:
            return "easy"
        elif avg_grade <= 12:
            return "fairly easy"
        elif avg_grade <= 15:
            return "standard"
        elif avg_grade <= 18:
            return "fairly difficult"
        elif avg_grade <= 21:
            return "difficult"
        else:
            return "very difficult"