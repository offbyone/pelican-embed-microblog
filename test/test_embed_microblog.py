import os
import unittest.mock

import pytest
from bs4 import BeautifulSoup
from pelican.contents import Article, Content
from pelican.settings import DEFAULT_CONFIG

from pelican_embed_microblog.embed_microblog import embed_tweet


@pytest.fixture(autouse=True)
def force_debug():
    import pelican_embed_microblog.embed_microblog

    with unittest.mock.patch.object(
        pelican_embed_microblog.embed_microblog, "PELICAN_MICROBLOG_DEBUG", True
    ):
        yield


@pytest.fixture(name="settings")
def get_settings():
    settings = DEFAULT_CONFIG.copy()
    return settings


@pytest.fixture(name="content_maker")
def make_content(settings):
    def maker(content):
        return Article(
            content=content,
            metadata={},
            settings=settings.copy(),
            source_path=os.path.dirname(__file__),
            context=settings.copy(),
        )

    return maker


@pytest.fixture(name="link_content")
def make_link(content_maker):
    content = content_maker("""<a href='https://some.site/@username'>content</a>""")
    embed_tweet(content)
    return content._content


@pytest.fixture(name="bare_text_content")
def make_bare_text(content_maker):
    content = content_maker("""<p>@offby1</p>""")
    embed_tweet(content)
    return content._content


@pytest.fixture(name="bare_text_body_content")
def make_bare_text_body(content_maker):
    content = content_maker("""<html><body><p>@offby1</p></body></html>""")
    embed_tweet(content)
    return content._content


def test_sub_twitter_ignores_at_in_href(link_content):
    soup = BeautifulSoup(link_content, "html.parser")
    assert soup.find("a", href="https://some.site/@username")


def test_no_script_in_ignored_content(link_content):
    assert (
        '<script src="//platform.twitter.com/widgets.js" charset="utf-8"></script>'
        not in link_content
    )


def test_sub_twitter_for_user_reference_in_text(bare_text_content):
    assert "https://twitter.com/offby1" in bare_text_content


def test_no_script_in_modified_content_without_body(bare_text_content):
    assert (
        '<script src="//platform.twitter.com/widgets.js" charset="utf-8"></script>'
        not in bare_text_content
    )


def test_script_in_modified_content_with_body(bare_text_body_content):
    assert 'src="https://platform.twitter.com/widgets.js"' in bare_text_body_content
    assert "async" in bare_text_body_content


@pytest.fixture(name="soup")
def make_soup_from_text(content_maker, text):
    content = content_maker(f"""<html><body><p>{text}</p></body></html>""")
    embed_tweet(content)
    soup = BeautifulSoup(content._content, "html.parser")
    return soup


valid_twitter_user_texts = pytest.mark.parametrize(
    "text",
    [
        "@offby1",
        "a link to @offby1",
        "@offby1 was here",
        "find @offby1 in the middle",
        "@offby1 is interested in @offby1 twice",
    ],
)


@valid_twitter_user_texts
def test_twitter_user_link_present(soup, text):
    assert soup.find("a", href="https://twitter.com/offby1")
    assert len(soup.find_all("a", href="https://twitter.com/offby1")) == text.count("@offby1")


@valid_twitter_user_texts
def test_twitter_user_link_present_has_script(soup):
    assert soup.find("script", src="https://platform.twitter.com/widgets.js")
    assert "async" in str(soup)


valid_tweet_texts = pytest.mark.parametrize(
    "text",
    [
        "a @offby1/status/31415926 tweet",
        "@offby1/status/31415926",
        "two tweets: @offby1/status/31415926 and @offby1/status/31415926",
    ],
)


@valid_tweet_texts
def test_tweet_present(soup):
    assert soup.find("a", href="https://twitter.com/offby1/status/31415926")


@valid_tweet_texts
def test_tweet_link_present_has_script(soup):
    assert soup.find("script", src="https://platform.twitter.com/widgets.js")
    assert "async" in str(soup)


valid_moment_texts = pytest.mark.parametrize(
    "text",
    [
        "a @offby1/moments/31415926 tweet",
        "@offby1/moments/31415926",
        "two moments: @offby1/moments/31415926 and @offby1/moments/31415926",
    ],
)


@valid_moment_texts
def test_moment_present(soup):
    assert soup.find("a", "twitter-moment", href="https://twitter.com/i/moments/31415926")


@valid_moment_texts
def test_moment_link_present_has_script(soup):
    assert soup.find("script", src="https://platform.twitter.com/widgets.js")
    assert "async" in str(soup)
