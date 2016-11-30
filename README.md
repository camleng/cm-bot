# GroupMe-Bot
Locates the meeting for IPFW Campus Ministry student leader meeting Monday mornings.

<br>

## Getting started

#### Python 3.6

This code requires Python 3.6. Get the dev version [here](https://www.python.org/downloads/windows/) (currently on `3.6.0b4`). Make sure to add Python to your PATH.

<br>

#### Headless devices

If you are using a Raspberry Pi or another headless device, make sure to do these steps first on a computer that has a UI, or use X with your Pi. Since the authentication requires a browser, it's impossible to authenticate with a headless device.

<br>

#### Prompts

In this guide I show prompts for Unix and Windows, and display a `$` and `>` respectively for the prompt.

If I only show a Unix prompt, that means the command will work in both Unix and Windows.

<br>

#### Get the code

Clone this repository on GitHub.

```bash
$ git clone https://github.com/camleng/groupme-bot.git
```

Enter the created directory.

```bash
$ cd groupme-bot
```

<br>

#### Virtualenv

It's good practice in Python to run code in virtual environments so you can easily manage your dependencies on a per-project basis. Read more on `virtualenv` [here](http://docs.python-guide.org/en/latest/dev/virtualenvs/).

Install `virtualenv` with `pip` (or perhaps `pip3`).

```bash
$ pip install virtualenv
```

It's assumed that you'll be using `virtualenv` in this project. Make sure to specify Python 3.6 when initalizing. I have named my environment `env`.

```bash
$ virtualenv env
```

If for some reason `virtualenv` does not select the correct version of Python, you may need to specify Python 3.6.

```bash
$ virtualenv env --python=python3.6
```

Activate your `virtualenv`.

- Unix

  ```bash
  $ . env/bin/activate
  ```


- Windows

  ```cmd
  > env\Scripts\activate
  ```

Note the `(env)` above the shell prompt (or beside on Windows).

You can later deactivate your `virtualenv` by typing the following.

```bash
(env)
$ deactivate
```

<br>

#### Get the packages

Install the packages via `pip` with the included `requirements.txt` file.

```bash
(env)
$ pip install -r requirements.txt
```

<br>

#### Registering a new GroupMe bot

- Head to https://dev.groupme.com/bots.

- Sign in with your GroupMe account

- Click "Create Bot".

- Select the group your bot will post to.

- Give the bot a name like "CM Bot" or something similar.

- It's not necessary to give a Callback or Avatar URL.

- Click "Submit".

- Copy the Bot ID of your newly-created bot.

- Open up `groupme.py` in your favorite text editor. Find the following line and change the `bot_id` to match the id of your newly-created bot.

```python
# groupme.py
bot_id = '[your_bot_id]'
```

<br>

#### Create a new project from the Google API Console

- Use [this wizard](https://console.developers.google.com/flows/enableapi?apiid=gmail) from the Google API Console to create a new project. Name the project "GroupMe Bot" or something similar.
- Once the API is enabled, click "Go to credentials".

- Under "Which API are you using?" select "Gmail API".

- Under "Where will you be calling the API from?" select "Other UI".

  *Raspberry Pi reminder: If you are planning to use a Raspberry Pi or another headless device, still select "Other UI". Since the authentication requires a browser, it's impossible to authenticate with a headless device.*

- Under "What data will you be accessing?" select "User data".

- Click "What credentials do I need?"

- Enter your device name like "MacBook Pro" or "Raspberry Pi" for the OAuth2.0 ID name to differentiate your credentials from different devices.

- Click "Create client ID".

- Enter "GroupMe-Bot" as the product name to show to users.

- Click "Continue".

- Click "Download" to download the credentials.

- Create a folder called `.credentials`.

  *Note the `.` at the beginning of the folder name.*

  ```bash
  (env)
  $ mkdir .credentials
  ```

- Rename the downloaded file to `client_secret.json`  and move it to the `.credentials` folder. 

  *Note: the downloaded file is often named `Unknown` on macOS.*

  - Unix

    ```bash
    (env)
    $ mv ~/Downloads/Unknown .credentials/client_secret.json
    ```

  - Windows

    Make sure to use tab-completion to auto-complete the long name of the downloaded client_secret file. I used 'XXXX' for brevity.

    ```cmd
    (env) > pushd %HOMEPATH%\Downloads
    (env) > ren client_secret_XXXX.json client_secret.json
    (env) > popd
    (env) > move %HOMEPATH%\Downloads\client_secret.json .credentials
    ```

<br>

#### Run `groupme.py`

```bash
(env)
$ python groupme.py
```

This will open your browser to authenticate your application.

*Raspberry Pi reminder: if you are using a Raspberry Pi or any other headless device, make sure you're running this on a computer that uses a UI, or use X with your Pi.*

Click "Allow".

This creates a file inside your `.credentials` folder called `groupme-bot.json`.

The application will now finish running, and you will not need to authenticate on any subsequent runs of the application.

<br>

#### Automation

It's assumed that this script will run every Monday morning for the Student Leader meeting.

**Unix**

If you have a Unix system, the de facto method is to use `crontab`.

Edit your `crontab` for your user.

```bash
(env)
$ crontab -e
```

Add these lines at the end. Substitute $GROUPME with the path to your `groupme-bot` folder. Sadly, `crontab` does not allow for custom variables. You can, however, use $HOME to save some typing.

```bash
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

The second entry is to clear the `.status` file. That file denotes if the message has already been sent that day. That file will be cleared every night at midnight.

<br>

## Back to the Pi

If you wish to run your application on the Pi, you'll have to repeat some of steps listed above.

**Get the code**

While on your Pi, clone the project again from GitHub.

```bash
$ git clone https://github.com/camleng/groupme-bot.git
```

<br>

**Install virtualenv**

Follow steps listed in previous section

<br>

**Transferring over the credentials**

Copy the `.credentials` directory over to the Pi underneath the `groupme-bot` folder.

If you're using Unix, you can use the `scp` command.

```bash
(env)
$ scp -r .credentials pi@10.0.0.25:/path/to/groupme-bot
```

If you're using Windows, you can use a program like [WinSCP](https://winscp.net/eng/download.php).

<br>

**Adding your own Bot ID**

Make sure to also change the `bot_id` inside of `groupme.py` with the id of your own bot.

```python
# groupme.py
bot_id = '[your_bot_id]'
```

<br>

**Finishing up**

Run `groupme.py` and you'll be all set! The credentials will be detected and it will not ask for authorization this time around.

```bash
(env)
$ python groupme.py
```

<br>
