# Sync Companion

Sync Companion is a Reddit bot originally developed for /r/ffxiv that helps reduce moderator workload with subreddit automation and synchronizing sidebars with widgets. It is provided as an open source bot for your own hosting.

Want to suggest an improvement or report a bug? Submit an [issue](https://github.com/zeno-mcdohl/sync-companion/issues). If you're seeking to submit changes, just open a Pull Request.

--------------

<!-- TOC -->

- [Sync Companion](#sync-companion)
    - [Features](#features)
    - [Setup](#setup)
        - [Prerequisites](#prerequisites)
        - [Installation](#installation)
        - [Initialization](#initialization)
    - [Instructions for Moderators](#instructions-for-moderators)
    - [Configuration](#configuration)

<!-- /TOC -->

## Features

* Allows for sidebar to be structured data.
* Synchronizes sidebar text and widgets. Widget types supported:
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

See `requirements.txt`. This bot has been developed and tested under:

* Linux 5.1.17
* Python 3.6.6
* PRAW 6.3.1

### Installation

1) Download this bot code 
2) Copy `config.ini.example` to `config.ini`, and `praw.ini.example` to `praw.ini`
3) Enter your API information into praw.ini as [instructed here](https://praw.readthedocs.io/en/latest/getting_started/configuration/prawini.html)
3) Create a scheduled task (e.g. `crontab` in Linux) running `synccompanion.py` with Python and using an argument of your subreddit name (e.g. `ffxiv`)


### Initialization

Create two wiki pages on your subreddit: `sidebar_sync` and `sidebar`. Set the edit permission to mods only and de-list the page from the wiki listing.

## Instructions for Moderators

Coming soon.

## Configuration

TBA
