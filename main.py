# from flask import Flask
from fastapi import FastAPI, Request, Response
import uvicorn
import ssl
import slack
import httpx
import concurrent.futures

# from slackeventsapi import SlackEventAdapter

from googlesheets.theeds import grade
import slacks.api as slackAPI

CHANNEL_ID_CAMPY = "#campy"
COMMAND_CAMPY = "/campy"

app = FastAPI()

# This is slack token

# app = Flask(__name__)
 
def get_slack_client():
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE

    client = slack.WebClient(token=SLACK_TOKEN, ssl=ssl_context)
    # client = slack.WebClient(token=SLACK_TOKEN)
    client.chat_postMessage(channel=CHANNEL_ID_CAMPY,text='Hello your bot here, what can I do for you?')
    
    
    return client
    # slack_event_adapter = SlackEventAdapter(SIGNING_SECRET, '/slack/events', app)

def send_results(response_url: str, response_text: str):
    print(f'production_status(): waiting for 10 sec...')
    # Simulate a long-running task
    import time
    time.sleep(6)
    print(f'production_status(): DONE waiting 10 sec...')

    with httpx.Client() as client:
        print(f'send_results(): sending http POST - {response_url} -> {response_text}')
        delayed_resp = {
            "text": response_text
        }
        # try: 
        resp = client.post(url=response_url, json=delayed_resp)
        print(f'production_status(): posted to webhook {response_url} - {resp.status_code}, {resp.reason_phrase}, {resp.text}, {resp.content}\n')
        print(f'production_status(): response headers = {resp.headers}')
        # except httpx.TimeoutException:
        #     print("Request timed out!")
        # except httpx.HTTPStatusError:
        #     print("Error response")

def spawn_process(param1: str, param2: str):
    
    with concurrent.futures.ProcessPoolExecutor(max_workers=2) as executor:
        print(f'spawn_process()...')
        future_to_url = executor.submit(send_results, param1, param2)
        # future = concurrent.futures.as_completed(future_to_url)
        # try:
        #     data = future.result()
        # except Exception as exc:
        #     print('%r generated an exception: %s' % (param1, exc))
        # else:
        #     print('%r page is %d bytes' % (param1, len(data)))
        print(f'spawn_process(): done.')

""" 
client.chat_postMessage(channel='#campy',text='Hello, your bot here, what can I do for you?')
slack_event_manager = SlackEventManager(SIGNING_SECRET, '/slack/events', app)

@slack_event_manager.on('reaction_added')
async def reaction_added(event_data):
    emoji = event_data['event']['reaction']
    print(emoji)


@slack_event_manager.on('message')
def message(payload):
    print(payload)
    event = payload.get('event', {})
    channel_id = event.get('campy')
    user_id = event.get('user')
    print("message(): user_id = " + user_id)

    text = event.get('text')
 
    if text == "hi":
        client.chat_postMessage(channel=channel_id, text="Hello, got it")
 
"""


# @app.route('/productions', methods = ['GET', 'POST'])
@app.get("/productions")
async def production_status(request: Request):
    slack_client = get_slack_client()
    print("Getting production status: ")
       
    # grades = await grade()
    # await grade()
    
    # if not grades:
    #     slack_client.chat_postMessage(channel='#campy', text=f'Getting grades...!')
    #     # return "grades not ready..."
    # else:
    #     slack_client.chat_postMessage(channel='#campy', text=f'Calculated some grades: DONE!')
        
    slack_client.chat_postMessage(channel=CHANNEL_ID_CAMPY, text=f'Calculated some grades: DONE!')
    return {"message": "production status checked"}

@app.post("/productions")
async def production_status(request: Request):
    slack_client = get_slack_client()
    print("Starting grading process... ")
    slack_client.chat_postMessage(channel=CHANNEL_ID_CAMPY, 
                                  text=f'Starting grading process, which will take a few moments, stay tuned...')
       
    slackAPI.get_users(slack_client)
    
    headers = request.headers
    print(f'production_status(): headers = {headers}')

    data = await request.form()

    print(f'production_status(): formData = {data}')
    if data is not None and data.get('command') == COMMAND_CAMPY:
        print(f'production_status(): got the grading request...')
        # command = data.get('command')
        text = data.get('text')
        response_url = data.get('response_url')
        user_id = data.get('user_id')
        channel_id = data.get('channel_id')

        # if command == '/campy':
        # Send immediate acknowledgment
        slack_client.chat_postMessage(
            channel=CHANNEL_ID_CAMPY,
            text="Your request is being processed. You will receive a response shortly."
        )

        ack_response = {
            "response_type": "ephemeral",  # The message will be visible only to the user who invoked the command
            "text": "Processing your request. This might take a few seconds..."
        }
        
        # grades = await grade()
        # await grade()
        
        # if not grades:
        #     slack_client.chat_postMessage(channel='#campy', text=f'Getting grades...!')
        #     # return "grades not ready..."
        # else:
        #     slack_client.chat_postMessage(channel='#campy', text=f'Calculated some grades: DONE!')
        
        # Send delayed response
        response_text = "After processing, production status checked, grading DONE" # "This is the delayed response after 10 seconds."
        spawn_process(response_url, response_text)

        # return Response(ack_response)

        return 'OK', 200
    
            # return {'message': response_text}
        # slack_client.chat_postMessage(
        #     channel=channel_id,
        #     text=response_text
        # )
        # slack_client.chat_postMessage(channel=CHANNEL_ID_CAMPY, text=f'Hey <@U076YT1E28Z> Calculated some grades: DONE!')
        # slack_client.chat_postMessage(channel=CHANNEL_ID_CAMPY, text=f'Hi <!channel> Calculated some grades: All DONE!')

        # return {"message": "production status checked, grading DONE"}

@app.get("/")
@app.get("/index")
@app.get("/echo")
@app.get("/healthz")
async def root():
    return {"message": "Hello from Campy Bot"}

# @app.route('/')
# @app.route('/index')
# def index():   
#     return 'Hello from Campy Bot'

if __name__ == "__main__":
    # app.run(debug=True)
    uvicorn.run(app, host="0.0.0.0", port=5000)


