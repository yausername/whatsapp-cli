# whatsapp-cli

## [Disclaimer] This is not a usable solution. I will not be able to provide any support.

## Limitations

  * You cannot initiate chat with users from whom you have not received a notification in the recent past. This is a pushbullet limitation as it uses reply to notification to send messages. I need to explore on using whatsapp web instead of pushbullet.

## Requirements
  * This CLI uses [Pushbullet APIs](https://docs.pushbullet.com/) to receive and send messages.

  * [Pushbullet App](https://play.google.com/store/apps/details?id=com.pushbullet.android) must be installed on your phone.

  * Pushbullet API token can be generated from [here](https://www.pushbullet.com/#settings/account)

  * You must be getting whatsapp notifications on your device for this to work.

  * To be able to send messages you need to receive at least one message after starting the application for seeding the conf (default location ~/.whatsapp-cli/conf).


Tested with python2.7

## Installation

    pip install whatsapp-cli


## Usage

Interactive (Curses) Mode - 

    Usage: whatsapp-cli [OPTIONS]
    
    Options:
      --token TEXT  Pushbullet API token  [required]
      --dir TEXT    data directory (default is ~/.whatsapp-cli)
      --help        Show this message and exit.

![](demo.gif)

---

Command Line Mode - 

	Usage: whatsapp-cli [OPTIONS] COMMAND [ARGS]...

	Options:
	  --token TEXT  Pushbullet API token  [required]
	  --help        Show this message and exit.

	Commands:
	  add    Add a contact
	  read   Read messages from a person/group
	  send   Send message to a person/group
	  users  List all contacts

Commands Reference

	Usage: whatsapp-cli add [OPTIONS]

	  Add a contact

	Options:
	  -u TEXT  Name of the person/group as it appears in your contacts  [required]
	  -m TEXT  12 digit mobile number  [required]
	  --help   Show this message and exit.


	Usage: whatsapp-cli read [OPTIONS]

	  Read messages from a person/group

	Options:
	  -u TEXT  Name of the person/group. Partial names are allowed
	  --help   Show this message and exit.


	Usage: whatsapp-cli send [OPTIONS]

	  Send message to a person/group

	Options:
	  -u TEXT  Name of the person/group or 12 digit mobile number. Partial names
			   are allowed  [required]
	  -m TEXT  Message to be sent  [required]
	  --help   Show this message and exit.


	Usage: whatsapp-cli users [OPTIONS]

	  List all contacts

	Options:
	  --help  Show this message and exit.
