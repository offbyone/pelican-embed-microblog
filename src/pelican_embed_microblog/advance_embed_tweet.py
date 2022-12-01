import re
from pelican import signals
from bs4 import BeautifulSoup

TWITTER_USER_RE = re.compile(r"(^|[^@\w])@(\w{1,15})\b[^/]?")
TWITTER_TWEET_RE = re.compile(r"(^|[^@\w])@(\w{1,15})/status/(\d+)\b")
TWITTER_MOMENT_RE = re.compile(r"(^|[^@\w])@(\w{1,15})/moments/(\d+)\b")


def user(content: BeautifulSoup) -> bool:
    modified = False
    for string in content.find_all(string=TWITTER_USER_RE):
        new_text = TWITTER_USER_RE.sub('\\1<a href="https://twitter.com/\\2">@\\2</a>', string)
        string.replace_with(BeautifulSoup(new_text, "html.parser"))
        modified = True

    return modified


def tweet(content: BeautifulSoup, config_data) -> bool:
    modified = False
    for string in content.find_all(string=TWITTER_TWEET_RE):
        new_text = TWITTER_TWEET_RE.sub(
            '\\1<blockquote class="twitter-tweet" '
            + config_data
            + '><a href="https://twitter.com/\\2/status/\\3">Tweet of \\2/\\3</a></blockquote>',
            string,
        )
        string.replace_with(BeautifulSoup(new_text, "html.parser"))
        modified = True
    return modified


def momenti(content: BeautifulSoup) -> bool:
    modified = False
    for string in content.find_all(string=TWITTER_MOMENT_RE):
        new_text = TWITTER_MOMENT_RE.sub(
            '\\1<blockquote class="twitter-tweet">'
            + '<a class="twitter-moment" href="https://twitter.com/i/moments/\\3">Tweet of \\2/\\3</a></blockquote>'
            + '<script async src="https://platform.twitter.com/widgets.js" charset="utf-8"></script> ',
            string,
        )
        string.replace_with(BeautifulSoup(new_text, "html.parser"))
        modified = True
    return modified


def embed_tweet(generator):

    config_data = ""

    if "TWITTER_CARDS" in generator.settings:
        config_data += " data-cards = '" + generator.settings["TWITTER_CARDS"] + "'"

    if "TWITTER_THEME" in generator.settings:
        config_data += " data-theme = '" + generator.settings["TWITTER_THEME"] + "'"

    if "TWITTER_CONVERSATION" in generator.settings:
        config_data += " data-conversation = '" + generator.settings["TWITTER_CONVERSATION"] + "'"

    if "TWITTER_LINK_COLOR" in generator.settings:
        config_data += " data-link-color = '" + generator.settings["TWITTER_LINK_COLOR"] + "'"

    if "TWITTER_WIDTH" in generator.settings:
        config_data += " data-width = '" + generator.settings["TWITTER_WIDTH"] + "'"

    if "TWITTER_ALIGN" in generator.settings:
        config_data += " data-align = '" + generator.settings["TWITTER_ALIGN"] + "'"

    if "TWITTER_LANG" in generator.settings:
        config_data += " data-lang = '" + generator.settings["TWITTER_LANG"] + "'"

    if "TWITTER_DNT" in generator.settings:
        config_data += " data-dnt = '" + generator.settings["TWITTER_DNT"] + "'"

    if not generator._content:
        return

    soup = BeautifulSoup(generator._content, "html.parser")
    modified = momenti(soup)
    modified = modified or tweet(soup, config_data)
    modified = modified or user(soup)

    if modified and soup.body:
        new_tag = soup.new_tag(
            "script", src="https://platform.twitter.com/widgets.js", charset="utf-8"
        )
        new_tag.attrs["async"] = None
        soup.body.append(new_tag)

    generator._content = soup.prettify(formatter="html")
    # generator._content = momenti(generator._content)
    # generator._content = tweet(generator._content, config_data)
    # generator._content = user(generator._content)


def register():
    signals.content_object_init.connect(embed_tweet)
