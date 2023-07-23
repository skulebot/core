# SkuleBot A Telegram Bot

## Running The Project Locally

#### **Step 1 Virtual Enviroment [Recommended]**
Create a virtual environmet

#### **Step 2 Installing Requirements**
```console
$ pip install -r requirements/dev.txt
```

#### **Step 3 Set Environment Variables**
Creat a `.env` file at the project root directory and place your token in place of `<TOKEN>`

**`skulebot/.env`**
```shell
BOT_TOKEN=<TOKEN>
# Either 'development' or 'production'. To run the bot locally this should be set to 'development'
ENV=development
```

#### **Step 4 Run the project**
```console
$ python main.py
```