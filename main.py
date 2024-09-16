from fastapi import FastAPI
# add the following new import statements
from fastapi.responses import HTMLResponse
import requests

# Add the following new import statements
from contextlib import asynccontextmanager
import ldclient
from ldclient import Context
from ldclient.config import Config
import os
import random

# Add this new function to instantiate and shut down the LaunchDarkly client
@asynccontextmanager
async def lifespan(app: FastAPI):
   # initialize the LaunchDarkly SDK
   ld_sdk_key = os.getenv("LAUNCHDARKLY_SDK_KEY")
   ldclient.set_config(Config(ld_sdk_key))
   yield
   # Shut down the connection to the LaunchDarkly client
   ldclient.get().close()

# Add this new parameter
app = FastAPI(lifespan=lifespan)


def call_dad_joke_api():
   headers = {"Accept": "text/plain", "User-Agent": "LaunchDarkly FastAPI Tutorial"}
   response = requests.get(url='https://icanhazdadjoke.com/', headers=headers)
   return response.content.decode("utf-8")

# Add this new function as a fallback when external API calls are disabled
def get_dad_joke_from_local():
   jokes = [
       "what's black and white and red all over? The newspaper.",
       "Why does Han Solo like gum? It's chewy!",
       "Why don't skeletons ride roller coasters? They don't have the stomach for it.",
       "Why are pirates called pirates? Because they arrr!",
       "I'm hungry! Hi Hungry, I'm Dad."
   ]
   return random.choice(jokes)

@app.get("/")
def read_root():
   return {"Hello": "World"}


# Add this new route to return an HTML response with a joke
@app.get("/joke/", response_class=HTMLResponse)
async def get_joke():
   context = Context.builder("context-key-123abc").name("Dad").build()
   use_dadjokes_api = ldclient.get().variation("use-dadjokes-api", context, False)
   if use_dadjokes_api:
       joke = call_dad_joke_api()
   else:
       joke = get_dad_joke_from_local()

   html = """
   <html>
       <head>
           <title>My cool dad joke app</title>
       </head>
       <body>
           <h1>{joke}</h1>
       </body>
   </html>
   """.format(joke=joke)
   return html