import re
from pelican import signals


def user(content):
    return re.sub(r'(^|[^@\w])@(\w{1,15})\b', '\\1<a href="https://twitter.com/\\2">@\\2</a>', content)


def tweet(content, config_data):
    return re.sub(
        r'(^|[^@\w])@(\w{1,15})/status/(\d+)\b',
        '\\1<blockquote class="twitter-tweet" ' +
        config_data +
        '><a href="https://twitter.com/\\2/status/\\3">Tweet of \\2/\\3</a></blockquote>',
        content
    ) + '<script src="//platform.twitter.com/widgets.js" charset="utf-8"></script>'


def momenti(content):
    return re.sub(
        r'(^|[^@\w])@(\w{1,15})/moments/(\d+)\b',
        '\\1<blockquote class="twitter-tweet">'+
        '<a class="twitter-moment" href="https://twitter.com/i/moments/\\3">Tweet of \\2/\\3</a></blockquote>'+
        '<script async src="https://platform.twitter.com/widgets.js" charset="utf-8"></script> ', content)


def embed_tweet(generator):

    config_data = ""

    if 'TWITTER_CARDS' in generator.settings:
        config_data += " data-cards = '" + \
            generator.settings["TWITTER_CARDS"] + "'"

    if 'TWITTER_THEME' in generator.settings:
        config_data += " data-theme = '" + \
            generator.settings["TWITTER_THEME"] + "'"

    if 'TWITTER_CONVERSATION' in generator.settings:
        config_data += " data-conversation = '" + \
            generator.settings["TWITTER_CONVERSATION"] + "'"

    if 'TWITTER_LINK_COLOR' in generator.settings:
        config_data += " data-link-color = '" + \
            generator.settings["TWITTER_LINK_COLOR"] + "'"

    if 'TWITTER_WIDTH' in generator.settings:
        config_data += " data-width = '" + \
            generator.settings["TWITTER_WIDTH"] + "'"

    if 'TWITTER_ALIGN' in generator.settings:
        config_data += " data-align = '" + \
            generator.settings["TWITTER_ALIGN"] + "'"

    if 'TWITTER_LANG' in generator.settings:
        config_data += " data-lang = '" + \
            generator.settings["TWITTER_LANG"] + "'"

    if 'TWITTER_DNT' in generator.settings:
        config_data += " data-dnt = '" + \
            generator.settings["TWITTER_DNT"] + "'"

    if not generator._content:
        return

    generator._content = momenti(generator._content)
    generator._content = tweet(generator._content, config_data)
    generator._content = user(generator._content)


def register():
    signals.content_object_init.connect(embed_tweet)
