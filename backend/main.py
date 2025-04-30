from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from better_profanity import profanity
from dotenv import load_dotenv
from redis_client import r
from google import genai
from google.genai import types
from dotenv import load_dotenv
import os

load_dotenv() #to load local environment variable for gemini api key
client=genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

class LinkedList:
    def __init__(self, redis_client, user_id):
        self.redis=redis_client
        self.user_key=f"history: {user_id}"

    def add(self, guess: str)-> bool:
        '''guess=guess.lower()
        if guess in self.guesses:
            return False
        self.guesses.append(guess)
        return True'''
        if self.redis.sismember("all_guesses", guess):
            return False
        
        self.redis.rpush(self.user_key, guess)
        self.redis.sadd("all_guesses", guess)
        return True
    
    def history(self):
        return self.redis.lrange(self.user_key, -5, -1)
        #to print previous prompts

user_sessions={}

async def check_with_ai(seed: str, guess: str, persona: str)->bool:
    #responsible for checking if user query beats seed
    persona_prompt={
        "You are the ultimate authority on the rules of a beats game. Given two elements determine if the first element beats the second. here are some estabilished rules for reference. Rock beats scissors, scissors beats paper, paper beats rock, water beats fire, electricity beats water, water does not beat electricity, electricity does not beat ground. The opposite pairs hold return the opposite value. For instance, electricity cannot beat ground. But ground beats electricity. Fire beats grass but grass does not beat fire. Consider the query, and respond only with a YES if it does beat it, or only with a NO. Return nothing else."
    }

    prompt=f"Does {guess} beat {seed}?" 
    
    cache_key=f"verdict:{persona}:{seed.lower()}:{guess.lower()}"
    cached=r.get(cache_key)
    if cached:
        return cached.strip().upper()=="YES"
    
    '''response=client.responses.create(
        model="gpt-3.5-turbo",
        instructions=persona_prompt,
        input=prompt,
        temperature=0,
    )
    print(response.output_text)'''
    #verdict="YES"

    '''generated_text=outputs[0]['generated_text']
    if "YES" in generated_text:
        verdict="YES"
    else:
        verdict="NO"

    r.set(cache_key, verdict, ex=86400)
    return verdict=="YES"'''
    #return "YES"

    '''response=client.models.generate_content(
        model="gemini-2.0-flash",
        contents=[
            types.Content(
                parts=[
                    types.Part.text(prompt),
                ]
            )
        ],
        config=types.GenerateContentConfig(
            temperature=0,
            system_instruction=persona_prompt
        )
    )'''

    response=client.models.generate_content(
        model="gemini-2.0-flash",
        config=types.GenerateContentConfig(
            system_instruction=persona_prompt
        ),
        contents=prompt
    )

    generated_text=response.text.strip().upper()
    verdict="YES" if "YES" in generated_text else "NO"
    r.set(cache_key, verdict, ex=86400)
    return verdict=="YES"

    '''config=types.GenerateContentConfig(
        system_instruction=persona_prompt),
        contents=prompt)'''

profanity.load_censor_words() #censors profanity

app=FastAPI()

class GuessRequest(BaseModel):
    seed_word: str
    guess: str
    user_id: str
    persona: str="serious"

user_sessions={}

@app.post("/guess")
async def make_guess(request: GuessRequest):
    if profanity.contains_profanity(request.guess):
        return{
            "error": "profanity detected in guess, please retry."
        }

    linked_list=LinkedList(r, request.user_id)

    if not linked_list.add(request.guess.lower()):
        return{
            "game_over": True, 
            "message": f"{request.guess} was already guessed. Game over.",
            "history": linked_list.history()
        }
    
    verdict=await check_with_ai(request.seed_word, request.guess, request.persona)
    custom_message=await personalize_response(request.seed_word, request.guess, verdict, request.persona)

    r.incr(request.guess.lower())#loading redis client
    count=int(r.get(request.guess.lower()) or 0) #incrementing count for succesful queries

    if verdict:
        return {
            "game_over":False,
            "message": custom_message,
            "times_guessed": count,
            "score": r.llen(linked_list.user_key),
            "history": linked_list.history(),
            "llm response": "user beats seed"
        }
    
    else:
        return{
            "game_over": True,
            "message": custom_message,
            "score": r.llen(linked_list.user_key),
            "history":linked_list.history(),
            "llm response": "user does not beat seed"
        }

@app.get("/history/{user_id}")
async def get_history(user_id :str):
    linked_list=LinkedList(r, user_id)
    return {"last_5_guesses": linked_list.history()}

@app.get("/")
async def root():
    return {"message": "Rock game API is running"}


async def rate_limit_middleware(request: Request, call_next):
    ip=request.client.host
    key=f"ratelimit:{ip}"
    count=r.incr(key)
    if count==1:
        r.expire(key, 60)

    if count>60:
        return JSONResponse(status_code=429, content={"error": "Rate limited"})
    return await call_next(request)

@app.post("/reset/{user_id}")
async def reset_user(user_id: str):
    r.delete(f"history: {user_id}")
    r.delete(f"user_guesses: {user_id}")

    for key in r.scan_iter("history:*"):
        r.delete(key)

    for key in r.scan_iter("user_guesses:*"):
        r.delete(key)

    r.delete("all_guesses")

    return {"status": "global reset succesful"}

async def personalize_response(seed: str, guess: str, verdict: str, persona: str)-> str:
    #to generate responses based on type of persona agent chosen
    tone="cheery and fun" if persona=="cheery" else "serious and deadpan"

    if verdict:
        relation=f"{guess} beats {seed}"

    else:
        relation=f"{guess} does not beat {seed}"

    prompt=f"Rephrase the fact that {relation} in a {tone} tone. Explicitly state who won in a one-liner."

    output=client.models.generate_content(
        model="gemini-2.0-flash",
        config=types.GenerateContentConfig(),
        contents=prompt
    )
    return output.text.strip()
