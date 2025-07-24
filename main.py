from agents import Agent, Runner, OpenAIChatCompletionsModel, set_tracing_disabled,function_tool
from dotenv import load_dotenv
import os
from openai import AsyncOpenAI
from whatsapp import send_whatsapp_message
import asyncio
import chainlit as cl


load_dotenv()
set_tracing_disabled(True)

API_KEY = os.getenv("GAMINI_API_KEY")

external_client = AsyncOpenAI(
    api_key=API_KEY,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

model = OpenAIChatCompletionsModel(
    model="gemini-2.0-flash",
    openai_client=external_client
)

@function_tool
def get_user_data(min_age: int) -> str:
    "Retrieves user data based on a minimum age"
    users = [
        {"name":"Muneba","age":20,"height":5.5,"color":"brown"},
        {"name":"Noreen","age":22,"height":6.1,"color":"fair"},
        {"name":"Rida","age":18,"height":4.5,"color":"moderate"},
        {"name":"Sidrah","age":32,"height":5.8,"color":"fair"},
        {"name":"Mutaha","age":25},
        {"name":"Hina","age":24,"height":5.3,"color":"light brown"},
        {"name":"Areeba","age":27,"height":5.7,"color":"fair"},
        {"name":"Iqra","age":21,"height":5.2,"color":"moderate"},
        {"name":"Javeria","age":23,"height":5.9,"color":"brown"},
        {"name":"Sana","age":26,"height":5.4,"color":"fair"},
        {"name":"Mehwish","age":28,"height":5.6,"color":"wheatish"},
        {"name":"Eman","age":20,"height":5.5,"color":"light brown"},
        {"name":"Dania","age":22,"height":5.3,"color":"moderate"},
        {"name":"Laiba","age":29,"height":6.0,"color":"fair"},
        {"name":"Zara","age":30,"height":5.7,"color":"brown"},
        {"name":"Amna","age":19,"height":5.1,"color":"fair"},
        {"name":"Samreen","age":31,"height":5.9,"color":"wheatish"},
        {"name":"Nimra","age":26,"height":5.8,"color":"moderate"},
        {"name":"Hira","age":23,"height":5.4,"color":"light brown"},
        {"name":"Farah","age":25,"height":5.5,"color":"fair"},
    ]

    matches = []
    for user in users:
        if user["age"] >= min_age:
            line = f'{user["name"]} ({user["age"]} yrs'
            if "height" in user:
                line += f', {user["height"]}ft'
            if "color" in user:
                line += f', {user["color"]} complexion'
            line += ")"
            matches.append(line)

    return "\n".join(matches)


#--------agent

rishty_agent = Agent(
    name="Rishty Wali",
    instructions="""
    You are a Rishty Wali Auntie.Find matches from a custom tool based on age only.
    Reply short and send WhatsApp message only if user asks.   """,
    model=model,
    tools=[get_user_data,send_whatsapp_message]
)

@cl.on_chat_start
async def start():
    cl.user_session.set("history",[])
    await cl.Message("Salame Beta!  Main Rishty wali Aunti hoon.Apna reshta batain , age batain,or WhatsApp number dain.").send()

#--------Ruunner
@cl.on_message
async def main (message:cl.Message):
    await cl.Message("🤔 Gour-O-fikar App k liy.......").send()
    history = cl.user_session.get("history") or []
    history.append({"role":"user", "content":message.content})

    result = Runner.run_sync(
        starting_agent=rishty_agent,
        input =history
    )

    history.append({"role":"assistant","content":result.final_output})
    
    cl.user_session.set("history",history)

    await cl.Message(content=result.final_output).send()

    


