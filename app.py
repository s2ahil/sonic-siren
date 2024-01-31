
import browsers
from taipy import Gui
from flask import Flask, request, jsonify
# import openai
from taipy.gui import Html
import re
import os
from PIL import Image
import google.generativeai as palm
from dotenv import load_dotenv
from youtubesearchpython.__future__ import VideosSearch
import asyncio
import threading
from queue import Queue
load_dotenv() 


palm.configure(api_key= os.getenv("key"))


models = [m for m in palm.list_models() if 'generateText' in m.supported_generation_methods]
model = models[0].name


image="https://i.gifer.com/cm8.gif"
videoUrl=""
# image = Image.open(image_path)

def format_content(content):
    # Define a regular expression pattern to identify headings
    heading_pattern = re.compile(r'\*\*([^*]+)\*\*')
    
    # Replace each heading with a new line after it
    formatted_content = heading_pattern.sub(r'\n\n\1 ', content)

    return formatted_content


async def search(name, result_queue):
    videosSearch = VideosSearch(f"{name}", limit=1)
    videosResult = await videosSearch.next()
    result_queue.put(videosResult)


def perform_search_async(name, result_queue):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    loop.run_until_complete(search(name, result_queue))

def submit_scenario(state):

    s1=state.s1
    s2=state.s2
    songLang=state.songLang

    data={
          "song_name1":s1 ,
          "song_name2": s2,
          "song_lang":songLang
    }

    song_name1 = data.get("song_name1")
    song_name2 = data.get("song_name2")
    song_lang= data.get("song_lang")


    prompt = f"""Given the songs " {song_name1}"  and "{song_name2}", recommend a song that shares similar musical qualities and would appeal to fans of both these songs in the language = {song_lang}. Consider factors like genre, tempo, mood, instrumentation, and overall sound when making your recommendation. Please provide the song title, artist name, and a brief explanation of why you think this song is a good match.
Output only one song and only its title and nothing else not even the artist name.
"""


    # Output only one song and only its title and nothing else not even the artist name
    completion = palm.generate_text(
    model=model,
    prompt=prompt,
    temperature=0.7,
    max_output_tokens=200,
    )
    print(completion.result)

    result_queue = Queue()
    threading.Thread(target=perform_search_async, args=(completion.result, result_queue)).start()
    search_result = result_queue.get()  # Wait for the result in the main thread
    print("search result",search_result)
    thumbnails = search_result.get('result', [])[0].get('thumbnails', [])
    thumbnail_urls = [thumbnail.get('url') for thumbnail in thumbnails]
    image_path=thumbnail_urls[0]
    print(image_path)
    state.image = image_path
    global videoUrl
    videoUrl = search_result.get('result', [])[0].get('link', '')
    state.videoUrl= videoUrl 
    print("check",videoUrl)


    print('reached')
    message = completion.result
    state.message = message




def videoLink(state):
    global videoUrl
    browsers.launch("chrome", url=videoUrl,args=["--incognito"])
   


s1=""
s2=""
songLang=""
message=""

page = """

<style>

.container-heading {
  
  font-size: 7rem;
  display:flex;
  justify-content:center;
   paddding:2rem;
  }

  .desc{
   display:flex;
  justify-content:center;
  align-items:center;
  }

.center{
 display:flex;
  justify-content:center;
   paddding:2rem;
   margin:3rem;
   text-align:center;
}

.form{
 display:flex;
 flex-direction:column;
 justify-content:space-evenly;
 padding:2rem;
 margin-top:2rem;
}


.middleSection{
 display:flex;
 justify-content:center;
 gap:2rem;
 padding:"2rem"
 
}

.buttonStyle{
margin-top:1rem;
}

.fullCenter{
 display:flex;
 justify-content:center;
 align-items:center;
}

</style>

<|container-heading|


Sonic Siren 🎧
|>


<|desc| 

<||  - Discover your next musical soulmate. |> 

|>


<|middleSection| 
 
<|fullCenter|  
 <|{image}|image|label=Your song will appear here |on_action=videoLink|>

 |>

<||

<h4>Music based on your taste </h4>



<|form| 
Enter first song : <br></br>
<|{s1}|input|>

 Enter second song: 
<|{s2}|input|>

 Enter song language to recommend:  <br></br>
<|{songLang}|input|>


<|buttonStyle|
<|submit|button|on_action=submit_scenario|>
|>




|>




|>



 |>






 

<|center|

Ai song name :  <|{message}|text|>

|>


<|center|

Made with 💙 by
[Rahul Yadav](https://www.linkedin.com/in/rahul-yadav-50276723b/) ,
[Sahil Pradhan](https://www.linkedin.com/in/sahil-pradhan-46a0a31b7/)

|>





"""




if __name__ =="__main__": 
# Create a Gui object with our page content
 app=Gui(page=page)
 app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True)
