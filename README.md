# GroupMe-Bot
Locates the meeting for IPFW Campus Ministry student leader team meeting Monday mornings

---

## Getting started

**Python 3.6**

This code requires Python 3.6. Get the dev version [here](https://docs.python.org/dev/download.html) (currently on `3.6.0b4`).

<br>

**Headless devices**

If you are using a Raspberry Pi or other headless device, make sure to do these steps first on a computer that has a UI, or use X with your Pi. Since the authentication requires a browser, it's impossible to authenticate with a headless device.

<br>

**Get the code**

Clone this repository on Github.

```sh
(env)
$ git clone https://github.com/camleng/groupme-bot.git
```

<br>

**Virtualenv**

It's good practice in Python to run code in virtual environments so you can easily manage your dependencies on a per-project basis. Read more on virtualenv [here](http://docs.python-guide.org/en/latest/dev/virtualenvs/). It's assumed that you'll be using `virtualenv` in this project. I have named my environment `env` — note the `(env)` above shell prompts.

<br>

**Get the packages**

Install the packages via `pip` with the included `requirements.txt` file.

```sh
(env)
$ pip install -r requirements.txt
```

<br>

**Registering a new GroupMe bot**

- Register a new bot at https://dev.groupme.com/bots.
- Make note of your Bot ID.
- In `groupme.py`, change the `bot_id` to match your newly-created bot.

```python
# groupme.py
bot_id = '[your_bot_id]'
```

<br>

**Create a new project from the Google API Console**

- Use [this wizard](https://console.developers.google.com/flows/enableapi?apiid=gmail) from the Google API Console to create a new project. Name the project "GroupMe Bot" or something similar.

- Once the API is enabled, click "Go to credentials".

- Under "Which API are you using?" select "Gmail API".

- Under "Where will you be calling the API from?" select your device.

  *Raspberry Pi reminder: If using a Raspberry Pi or other headless device, select "Other UI". Since the authentication requires a UI, it's impossible to authenticate with a headless device.*

- Under "What data will you be accessing?" select "User data".

- Click "What credentials do I need?"

- Enter your device name like "MacBook Pro" or "Raspberry Pi" for the OAuth2.0 ID name to differentiate your credentials from different devices.

- Click "Create client ID".

- Enter "GroupMe-Bot" as the product name to show to users

- Click "Continue".

- Click "Download" to download the credentials.

- Rename this file to `client_secret.json` move it to a folder named `.credentials`.

  *Note the `.` at the beginning of the folder name.*

- Make sure that folder is inside of your `groupme-bot` folder.

<br>

**Run `	groupme.py`**

```sh
(env)
$ python groupme.py
```

This will open your browser to authenticate your application.

*Raspberry Pi reminder: if you are using a Raspberry Pi or any other headless device, make sure to run this on a computer that uses a UI, or use X with your Pi.*

Click "Allow".

This creates a file underneath your `.credentials` folder called `groupme-bot.json`.

The application will now run, and you will not need to authenticate on any subsequent runs of the application.

<br>

**Back to the Pi**

If you wish to run your application on the Pi, make sure to clone the project again from Github.

```sh
$ git clone https://github.com/camleng/groupme-bot.git
```

<br>

Copy the `.credentials` directory over to the Pi underneath the `groupme-bot` folder.

Make sure to also change the `bot_id` inside of `groupme.py` with the id of your own bot.

```python
# groupme.py
bot_id = '[your_bot_id]'
```

<br>

Run `groupme.py` and you'll be all set! The credentials will be detected and it will not ask for authorization this time around.

```sh
(env)
$ python groupme.py
```

<br>

**Automation**

It's assumed that this script will run every Monday morning for the Student Leader Meeting. If you have a Unix system the defacto method is to use `crontab`.

Edit your `crontab` for your user.

```sh
(env)
$ crontab -e
```

Add these lines at the end. Substitute $GROUPME with the path to your `groupme-bot` folder. Sadly, `crontab` does not allow for custom variables. You can, however, use \$HOME to save some typing.

```sh
# m     h       dom     mon     dow     command
30      8       *       *       1       $GROUPME/env/bin/python $GROUPME/groupme.py
0       0       *       *       *       echo > $GROUPME/.status
```

These values assume the script will run at 8:30 am every Monday morning. If you want to change that, alter the values given. The columns are detailed below.

- Minute (0-59)
- Hours (0-23)
- Day (0-31)
- Month (0-12 [12 == December])
- Day of the week (0-7 [7 or 0 == Sunday])
- `/path/to/command` – Script or command name to schedule

