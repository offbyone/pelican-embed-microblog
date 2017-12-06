# Pelican plugin: Advance Embed Tweet
Embedding tweets into your Pelican blog posts.
This repo is an advance version of the plugin from [lqez](https://github.com/lqez/pelican-embed-tweet) which hasn't the config for the style.

| Author | Fundor333 |
| :----: |	|:-----------------------------:	|
|   Email  	|       f333@fundor333.com      	|
| Homepage 	|   https://www.fundor333.com   	|
|  Github  	|  https://github.com/fundor333 	|
|  Twitter 	| https://twitter.com/fundor333 	|

# How to use it
----------------

 1. Download the repo
 2. Copy it wherever or just into `pelican/plugins/`
 3. Put `pelican-advance-embed-tweet` into plugin list of settings.
    - `PLUGINS = ['pelican.plugins.pelican-advance-embed-tweet']`
 4. Add your config into the `pelicanconf.py`

## Config
The config implement the [Twitter Api](https://dev.twitter.com/web/embedded-tweets/parameters).

| **Config Label**     | **Description**                                                                                                                                      |
| :------------------: | ---------------------------------------------------------------------------------------------------------------------------------------------------- |
| TWITTER_CARDS        | When set to `hidden`, links in a Tweet are not expanded to photo, video, or link previews.                                                           |
| TWITTER_THEME        | When set to `none`, only the cited Tweet will be displayed even if it is in reply to another Tweet.                                                  |
| TWITTER_CONVERSATION | When set to `dark`, displays Tweet with light text over a dark background.                                                                           |
| TWITTER_LINK_COLOR   | Adjust the color of Tweet links with a hexadecimal color value.                                                                                      |
| TWITTER_WIDTH        | The maximum width of the rendered Tweet in whole pixels. This value should be between 250 and 550 pixels.                                            |
| TWITTER_ALIGN        | Float the Tweet `left`, `right`, or `center` relative to its container. Typically set to allow text or other content to wrap around the Tweet.       |
| TWITTER_LANG         | A supported Twitter language code. Loads text components in the specified language. Note: does not affect the text of the cited Tweet.               |
| TWITTER_DNT          | When set to true, the Tweet and its embedded page on your site are not used for purposes that include personalized suggestions and personalized ads. |
