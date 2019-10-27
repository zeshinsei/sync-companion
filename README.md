# Sync Companion

Sync Companion is a Reddit bot that helps reduce moderator workload with subreddit automation and synchronizing the sidebar with widgets. It is provided as an open source bot for your own hosting.

Want to suggest an improvement or report a bug? Submit an [issue](https://github.com/zeno-mcdohl/sync-companion/issues). If you're seeking to submit changes, just open a Pull Request.

--------------

<!-- TOC -->

- [Sync Companion](#sync-companion)
    - [Features](#features)
    - [Setup](#setup)
        - [Prerequisites](#prerequisites)
        - [Installation](#installation)
    - [Instructions for Moderators](#instructions-for-moderators)
        - [Adding new content](#adding-new-content)
        - [Editing existing content](#editing-existing-content)
        - [Deleting content](#deleting-content)
        - [Adding only sidebar content](#adding-only-sidebar-content)
    - [Configuration](#configuration)
        - [Dynamic content](#dynamic-content)
        - [config.ini](#configini)
        - [praw.ini](#prawini)
    - [License](#license)

<!-- /TOC -->

## Features

* Allows for sidebar to be structured data.
* Synchronizes sidebar and widgets. Widget types supported:
  * Textarea
  * Community List
* Any form of markdown used.
* Multiple lines of text.
* Ability to update a sidebar section without a correlating widget.
* Preserve widget color set from mod tools.
* Various automations:
  * Twitch stream list for specific game (currently not functioning).
  * Discord members online count.
  * Countdown clock to a target date and time.
* Sidebar character limit warning via modmail.

## Setup

### Prerequisites

See [requirements.txt](requirements.txt). This bot has been developed and tested under:

* Linux 5.1.17
* Python 3.6.6
* PRAW 6.3.1

### Installation

1) Download this bot code.
2) Copy `config.ini.example` to `config.ini`, and `praw.ini.example` to `praw.ini`.
3) Enter your Reddit API information into praw.ini as [instructed here](https://praw.readthedocs.io/en/latest/getting_started/configuration/prawini.html).
4) Copy your sidebar content (`/about/sidebar`) to a new wiki page *sidebar*. Set the edit permission to mods only and de-list the page from the wiki listing.
5) Create another new wiki page *sidebar_sync*. Set the permissions again as described above.
6) Validate the bot by making a change to the *sidebar* wiki page then running `synccompanion.py` with Python, using the argument of your subreddit name. This should push your changes live to the actual sidebar. Example: `python synccompanion.py AskReddit`
7) Create a scheduled task (e.g. `crontab` in Linux) running `synccompanion.py` with Python and using an argument of your subreddit name (e.g. `AskReddit`).


## Instructions for Moderators

### Adding new content

1) New content that you wish to be synced between old Reddit and the redesign should be added to the *sidebar_sync* wiki page under a new header (`####`). The header name should be concise and contain underscores instead of spaces; it represents the ID of this content section. Below that should **contain the content** which can be multiple lines. Example:

```
####Current_Shows
This could be a list of relevant TV shows. It appears on old Reddit and the redesign!
```

Note per above that only a single newline should follow the header, not two newlines.

2) On the *sidebar* wiki page, add a line that corresponds with the header name from above and surround it with `%%`. This page defines **where the content is located** on the sidebar for old Reddit (this makes it essentially structured data). Example:

```
%%Current_Shows%%
```

**This page acts as your sidebar**, so format it as you'd like. It can contain any typical sidebar content and include the IDs that'll sync between your sidebar and widgets.

3) Open the redesign and manually **create a new widget**. The title of the widget should be the header name from above, except replace the underscores with spaces. The widget text can be left blank, as it will be automatically updated. Example: `Current Shows` as a widget title.

### Editing existing content

If content exists that is being synced between old Reddit and the redesign, it is defined on the *sidebar_sync* wiki page. Simply edit your desired text on *sidebar_sync*, save the page, and wait for the next scheduled run of the bot. [Example gif.](https://i.imgur.com/aMGwVav.gifv)

### Deleting content

Simply delete the corresponding text on the *sidebar_sync* wiki page including the header, as well as the header ID section on the *sidebar* wiki page.

### Adding only sidebar content

If you wish to add content to the sidebar (such as formatting, text around CSS hacks, etc) simply edit the *sidebar* wiki page and wait for the next bot run. Do not edit `/about/sidebar` as the bot handles that, just edit the *sidebar* wiki page.

## Configuration

### Dynamic content

The following items can be defined in the *sidebar_sync* wiki page to provide dynamic content. Format: `####String_Below|Argument 1|Argument 2`

* **Twitch_Streams**: Provides a list of links of current streams for a specific game. The second line can be any header ID you wish for use on the *sidebar* wiki page, below we used TWITCH as a header name. Syntax: 
```
####Twitch_Streams|GAME NAME HERE
%%TWITCH%%
```

* **Discord_Info**: Provides a member count for a specific Discord server. Syntax:
```
####Discord_Info|DISCORD SERVER ID HERE
%%DISCORD%%
```

* **Countdown**: Provides a countdown clock that counts down to a specific date & time. The 2nd argument is the name of the widget title this should update. Example:
```
####Countdown|2019-12-19 14:00:00|Meetup_starts_at
%%CTDOWN%%
```

### config.ini

* **DebugMode**: `False` or `True`; if True this will enable console logging and not push any changes live.
* **ItemLimit**: An integer; used with automated content to return this maximum number of items.
* **NumCountdownLimit**: An integer; used with the countdown clock feature and is the maximum number of clocks allowed on sidebar.
* **UserAgent**: User agent string; used with any calls to web content including the Discord API.

### praw.ini

See https://praw.readthedocs.io/en/latest/getting_started/configuration/prawini.html

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details
