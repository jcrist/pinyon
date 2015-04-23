from .static import StaticPatternSet
from .dynamic import DynamicPatternSet
from .pattern import Pattern, PatternSet
from .util import copy_doc


class Engine(object):
    """Main entry point for Pinyon"""

    def __init__(self, context):
        self.context = context

    @copy_doc(Pattern, True)
    def pattern(self, pat, vars=()):
        return Pattern(self.context, pat, vars)

    @copy_doc(PatternSet, True)
    def patternset(self, patterns, type='dynamic'):
        if type == 'dynamic':
            return DynamicPatternSet(self.context, patterns)
        else:
            return StaticPatternSet(self.context, patterns)
