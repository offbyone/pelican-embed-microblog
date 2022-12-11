from abc import ABC
import logging
import os
import re
from difflib import ndiff

from bs4 import BeautifulSoup, NavigableString
from pelican import signals, generators

logger = logging.getLogger(__name__)

PELICAN_MICROBLOG_DEBUG = bool(os.environ.get("PELICAN_MICROBLOG_DEBUG", None))

TWITTER_USER_RE = re.compile(
    r"""
    (^|[^@\w])   # ensure we're at a word boundary where the preceding character is not a "@"
    @(\w{1,15})  # basic twitter username format
    \b(?![/@#])  # at the end, a word boundary with no '@', '#' or '/' following
""",
    re.VERBOSE,
)
TWITTER_TWEET_RE = re.compile(r"(^|[^@\w])@(\w{1,15})/status/(\d+)\b")
TWITTER_MOMENT_RE = re.compile(r"(^|[^@\w])@(\w{1,15})/moments/(\d+)\b")

MASTODON_USER_RE = re.compile(
    r"""
    (?P<pre>^|[^@\w])   # the thing before needs to not be a '@'
    @(?P<username>[a-z0-9_]+(?:[a-z0-9_\.-]+[a-z0-9_]+)?)
    @(?P<domain>\w+(?:\.\w+)+)
    \b(?![/@#])
""",
    re.VERBOSE,
)


# some CSS debugging utilities:
def get_element(node):
    # for XPATH we have to count only for nodes with same type!
    length = len(list(node.previous_siblings)) + 1
    if (length) > 1:
        return "%s:nth-child(%s)" % (node.name, length)
    else:
        return node.name


def get_css_path(node):
    if e := get_element(node):
        path = [get_element(node)]
    else:
        path = []

    for parent in node.parents:
        if parent.name == "body":
            break
        if e := get_element(parent):
            path.insert(0, e)
    return " > ".join(path)


class Embedder(ABC):
    user_re = re.compile(r"IMPLEMENT_IN_A_SUBCLASS")
    status_re = re.compile(r"IMPLEMENT_IN_A_SUBCLASS")

    def __init__(self, generator: generators.Generator):
        self.modified = False
        self.generator = generator
        self.settings = generator.settings

    def applies(self, content: str) -> bool:
        return (
            self.user_re.search(content) is not None or self.status_re.search(content) is not None
        )

    def embed(self, content: BeautifulSoup):
        self.modified = False

        if PELICAN_MICROBLOG_DEBUG:
            pre_image = content.prettify(formatter="html")
        else:
            pre_image = ""  # make the type checker happy

        self.user(content)
        if PELICAN_MICROBLOG_DEBUG:
            post_user = content.prettify(formatter="html")
            diff = ndiff(pre_image.splitlines(keepends=False), post_user.splitlines(keepends=False))
            logger.debug("changed: \n%s", "\n".join(diff))
            pre_image = post_user

        self.status(content)
        if PELICAN_MICROBLOG_DEBUG:
            post_status = content.prettify(formatter="html")
            diff = ndiff(
                pre_image.splitlines(keepends=False), post_status.splitlines(keepends=False)
            )
            logger.debug("changed: \n%s", "\n".join(diff))
            pre_image = post_status

        self.embed_other(content)
        if PELICAN_MICROBLOG_DEBUG:
            post_other = content.prettify(formatter="html")
            diff = ndiff(
                pre_image.splitlines(keepends=False), post_other.splitlines(keepends=False)
            )
            logger.debug("changed: \n%s", "\n".join(diff))
            pre_image = post_other

        if self.modified:
            self.add_scripts(content)

    def user(self, content: BeautifulSoup):
        for string in content.find_all(string=self.user_re):
            if PELICAN_MICROBLOG_DEBUG:
                logger.debug("found user ID in %s", get_css_path(string))

            string.replace_with(BeautifulSoup(self.replace_user(string), "html.parser"))
            self.modified = True

    def status(self, content: BeautifulSoup):
        for string in content.find_all(string=self.status_re):
            if PELICAN_MICROBLOG_DEBUG:
                logger.debug("found status in %s", get_css_path(string))
            string.replace_with(BeautifulSoup(self.replace_status(string), "html.parser"))
            self.modified = True

    def replace_user(self, matched: NavigableString) -> str:
        return matched

    def replace_status(self, matched: NavigableString) -> str:
        return matched

    def embed_other(self, content: BeautifulSoup) -> None:
        ...

    def add_scripts(self, content: BeautifulSoup):
        ...


class MastodonEmbed(Embedder):
    user_re = MASTODON_USER_RE
    status_re = MASTODON_USER_RE

    def replace_user(self, matched: NavigableString) -> str:
        return self.user_re.sub(
            r'\1<a href="https://\3/@\2">@\2@\3</a>',
            matched,
        )


class TwitterEmbed(Embedder):
    user_re = TWITTER_USER_RE
    status_re = TWITTER_TWEET_RE

    def applies(self, content: str) -> bool:
        return super().applies(content) or TWITTER_MOMENT_RE.search(content) is not None

    def replace_user(self, matched: NavigableString) -> str:
        new_text = self.user_re.sub('\\1<a href="https://twitter.com/\\2">@\\2</a>', matched)
        return new_text

    def replace_status(self, matched: NavigableString) -> str:
        new_text = self.status_re.sub(
            '\\1<blockquote class="twitter-tweet" '
            + self.config_data
            + '><a href="https://twitter.com/\\2/status/\\3">Tweet of \\2/\\3</a></blockquote>',
            matched,
        )
        return new_text

    def embed_other(self, content: BeautifulSoup):
        for string in content.find_all(string=TWITTER_MOMENT_RE):
            if PELICAN_MICROBLOG_DEBUG:
                logger.debug("found twitter moment in %s", get_css_path(string))
            new_text = TWITTER_MOMENT_RE.sub(
                '\\1<blockquote class="twitter-tweet">'
                + '<a class="twitter-moment" href="https://twitter.com/i/moments/\\3">Tweet of \\2/\\3</a></blockquote>'
                + '<script async src="https://platform.twitter.com/widgets.js" charset="utf-8"></script> ',
                string,
            )
            string.replace_with(BeautifulSoup(new_text, "html.parser"))
            self.modified = True

    def add_scripts(self, content: BeautifulSoup):
        if content.body:
            new_tag = content.new_tag(
                "script", src="https://platform.twitter.com/widgets.js", charset="utf-8"
            )
            new_tag.attrs["async"] = None
            content.body.append(new_tag)

    @property
    def config_data(self):
        config_data = ""
        if "TWITTER_CARDS" in self.settings:
            config_data += " data-cards = '" + self.settings["TWITTER_CARDS"] + "'"

        if "TWITTER_THEME" in self.settings:
            config_data += " data-theme = '" + self.settings["TWITTER_THEME"] + "'"

        if "TWITTER_CONVERSATION" in self.settings:
            config_data += " data-conversation = '" + self.settings["TWITTER_CONVERSATION"] + "'"

        if "TWITTER_LINK_COLOR" in self.settings:
            config_data += " data-link-color = '" + self.settings["TWITTER_LINK_COLOR"] + "'"

        if "TWITTER_WIDTH" in self.settings:
            config_data += " data-width = '" + self.settings["TWITTER_WIDTH"] + "'"

        if "TWITTER_ALIGN" in self.settings:
            config_data += " data-align = '" + self.settings["TWITTER_ALIGN"] + "'"

        if "TWITTER_LANG" in self.settings:
            config_data += " data-lang = '" + self.settings["TWITTER_LANG"] + "'"

        if "TWITTER_DNT" in self.settings:
            config_data += " data-dnt = '" + self.settings["TWITTER_DNT"] + "'"

        return config_data


def embed_tweet(generator):
    if not generator._content:
        return

    embedders = [TwitterEmbed(generator), MastodonEmbed(generator)]

    # to save on parsing, we're going to do a fast check on each embedder to see if they _may_ apply
    if not any([e.applies(generator._content) for e in embedders]):
        return

    soup = BeautifulSoup(generator._content, "html.parser")
    TwitterEmbed(generator).embed(soup)
    MastodonEmbed(generator).embed(soup)
    generator._content = soup.prettify(formatter="html")


def register():
    signals.content_object_init.connect(embed_tweet)
