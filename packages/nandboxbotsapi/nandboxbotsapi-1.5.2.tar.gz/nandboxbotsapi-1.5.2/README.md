# A Python nandbox Bot API


A Python library to interact with official Nandbox Bot API. A bot token is **required** and can be obtained [this way](https://www.youtube.com/watch?v=FXb6tjOuxSc).

## Build your first bot
You can easily build your bot by following the below steps:

**1.Setup your configuration object** once you get your bot configuration data from nandbox app , copy it to a `config` object.

If you don't know how to get bot configuration data and token from nandbox 

- Open your bot in nandbox app then open the top right menu and click to `Get token` .This process explained in this [video](https://www.youtube.com/watch?v=FXb6tjOuxSc&feature=youtu.be).


You will get data like this:
``` 
token:90091783784280234234WBBPmJAnSD5ILIkc6N6QjY3ZzeY
url:wss://<SERVER>:<PORT>/nandbox/api/  
download:https://<SERVER>:<PORT>/nandbox/download/  
upload:https://<SERVER>:<PORT>/nandbox/upload/
```
Add your token and the other data to  `config.json` file just like below :
```json
{
    "Token": "<your token>",
    "URI": "wss://<SERVER>:<PORT>/nandbox/api/",
    "DownloadServer": "https://<SERVER>:<PORT>/nandbox/download/",  
    "UploadServer": "https://<SERVER>:<PORT>/nandbox/upload/"
}
```

**2.Implement your main.py file :** To do that please follow the next instructions:
1. Make sure `config.json` file is created.
2. Implement the `CallBack.on_connect` function.
3. Implement the rest of the functions as your application requires.

```python
import json

from nandboxbots.nandbox import Nandbox
from nandboxbots.NandboxClient import NandboxClient
from nandboxbots.util.Utils import get_unique_id

CONFIG_FILE = "./config.json"

f = open(CONFIG_FILE)
config = json.load(f)
f.close()

TOKEN = config['Token']

client = NandboxClient.get(config)

nandbox = Nandbox()

napi = nandbox.Api()


class CallBack(nandbox.Callback):
    def on_connect(self, api):
        global napi
        napi = api
        print("Connected")

    def on_close(self):
        print("Closed")

    def on_error(self):
        print("Error")

    def on_receive(self, incoming_msg):
        print("Message Received")

        if incoming_msg.is_text_msg():
            chatId = incoming_msg.chat.id
            text = incoming_msg.text
            reference = get_unique_id()
            napi.send_text(chat_id=chatId, text=text, reference=reference)


callBack = CallBack()
client.connect(config['Token'], callBack)
```

____Have a look at the [test](https://github.com/nandbox/nandboxbotsapi-py/tree/main/nandboxbots/test) folder, you might find useful examples.____

## License 
MIT License

Copyright (c) 2023 nandbox

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.