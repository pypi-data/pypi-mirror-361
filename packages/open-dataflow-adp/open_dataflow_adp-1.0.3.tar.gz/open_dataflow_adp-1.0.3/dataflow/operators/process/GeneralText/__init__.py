from .filters.ngram_filter import NgramFilter
from .filters.language_filter import LanguageFilter
from .filters.deita_quality_filter import DeitaQualityFilter
from .filters.deita_complexity_filter import DeitaComplexityFilter
from .filters.instag_filter import InstagFilter
from .filters.pair_qual_filter import PairQualFilter
from .filters.qurating_filter import QuratingFilter
from .filters.superfiltering_filter import SuperfilteringFilter
from .filters.fineweb_edu_filter import FineWebEduFilter
from .filters.text_book_filter import TextbookFilter
from .filters.alpagasus_filter import AlpagasusFilter
from .filters.heuristics import (
    ColonEndFilter,
    WordNumberFilter,
    BlocklistFilter,
    SentenceNumberFilter,
    LineEndWithEllipsisFilter,
    ContentNullFilter,
    MeanWordLengthFilter,
    SymbolWordRatioFilter,
    HtmlEntityFilter,
    IDCardFilter,
    NoPuncFilter,
    SpecialCharacterFilter,
    WatermarkFilter,
    StopWordFilter,
    CurlyBracketFilter,
    CapitalWordsFilter,
    LoremIpsumFilter,
    UniqueWordsFilter,
    CharNumberFilter,
    LineStartWithBulletpointFilter,
    LineWithJavascriptFilter
)

from .deduplicators.minhash_deduplicator import MinHashDeduplicator

__all__ = [
    'NgramFilter',
    'LanguageFilter',
    'DeitaQualityFilter',
    'InstagFilter',
    'PairQualFilter',
    'QuratingFilter',
    'SuperfilteringFilter',
    'MinHashDeduplicator',
    'FineWebEduFilter',
    'TextbookFilter',
    'DeitaComplexityFilter',
    # Heuristic Filters
    'ColonEndFilter',
    'WordNumberFilter',
    'BlocklistFilter',
    'SentenceNumberFilter',
    'LineEndWithEllipsisFilter',
    'ContentNullFilter',
    'MeanWordLengthFilter',
    'SymbolWordRatioFilter',
    'HtmlEntityFilter',
    'IDCardFilter',
    'NoPuncFilter',
    'SpecialCharacterFilter',
    'WatermarkFilter',
    'StopWordFilter',
    'CurlyBracketFilter',
    'CapitalWordsFilter',
    'LoremIpsumFilter',
    'UniqueWordsFilter',
    'CharNumberFilter',
    'LineStartWithBulletpointFilter',
    'LineWithJavascriptFilter'
]
