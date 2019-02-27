import json
import re


class Filter(object):
    """
    Base filter object. Takes a string in the constructor and knows how to apply a text transformation
    """
    @property
    def regex(self):
        raise NotImplemented

    @staticmethod
    def repl(match):
        raise NotImplemented

    def __init__(self, text):
        self.text = text

    def apply(self):
        return self.regex.sub(self.repl, self.text).strip()


class NoPadPunctuation(Filter):
    """ Removes padding from punctuation that should not be padded, e.g. - """

    @property
    def regex(self):
        terms = ('-', '\\', '\'', '’', '/')
        return re.compile('\\s([' + ''.join(terms) + '])\\s')

    @staticmethod
    def repl(match):
        return match.group(1)


class RightPadPunctuation(Filter):
    """ Adds right padding to punctuation e.g. : """

    @property
    def regex(self):
        terms = (':', ',', '.', '!', '?', '+')
        return re.compile('\\s?([' + ''.join(terms) + ')])\\s?')

    @staticmethod
    def repl(match):
        return '%s ' % match.group(1)


class LeftPadPunctuation(Filter):
    """ Adds left padding to punctuation e.g. ( """

    @property
    def regex(self):
        return re.compile(r'\s?([(])\s?')

    @staticmethod
    def repl(match):
        return ' %s' % match.group(1)


class MaybePluralParens(Filter):
    """ For the special case of maybe plural(s), remove left padding. """

    @property
    def regex(self):
        return re.compile(r'\s(\(s\))\s', flags=re.IGNORECASE)

    @staticmethod
    def repl(match):
        return '%s ' % match.group(1)


class Ellip(Filter):
    """ Replaces 2 or more .. with ... """

    @property
    def regex(self):
        return re.compile(r'([.]\s){3,}\s?')

    @staticmethod
    def repl(match):
        return '... '


class SentenceCase(Filter):
    """ Converts the given text to sentence case. """

    def apply(self):
        return '. '.join(i.capitalize() for i in self.text.split('. '))


class TitleCase(Filter):
    """ Converts the given text to Title Case """

    @property
    def regex(self):
        terms = json.load(open('bot/terms-to-title-case.json'))
        return re.compile('\\b(' + '|'.join(terms) + ')\\b', flags=re.IGNORECASE)

    @staticmethod
    def repl(match):
        return match.group(1).title()


class AllCaps(Filter):
    """ Converts the given text to ALL CAPS """

    @property
    def regex(self):
        terms = json.load(open('bot/terms-to-capitalize.json'))
        return re.compile('\\b(' + '|'.join(terms) + ')\\b', flags=re.IGNORECASE)

    @staticmethod
    def repl(match):
        return match.group(1).upper()
