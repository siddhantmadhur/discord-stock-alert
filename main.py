from google.auth.transport.requests import Request
from oauth2client.service_account import ServiceAccountCredentials
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import os
from PIL import Image
import jinja2
import pandas as pd

import discord
import requests

from html2image import Html2Image
SPREADSHEET_ID = "1LY0-ltHIzJvcf1gtWZYTf7FOiRu6X5K_EwFAVR8i07w"
RANGE_NAME = "Stock League 2024 Dec-2025 Dec!D7:D10"



def create_leaderboard_img ():
    creds = ServiceAccountCredentials.from_json_keyfile_name("serviceAccount.json")
    if not creds or creds.invalid:
        exit(1)
    service = build("sheets", "v4", credentials=creds)
    sheet = service.spreadsheets()
    result = (
        sheet.values()
        .get(spreadsheetId=SPREADSHEET_ID, range=RANGE_NAME)
        .execute()
    )
    values: list[str]= [x[0] for x in result.get("values", [])] 
    total_money_s= [x.replace("$", "").replace(" ", "") for x in values]
    total_money_f= [float(x.replace(",", "")) for x in total_money_s]
    print(total_money_s)
    print(total_money_f)

    data ={
        "profile_pfp": [
            "https://cdn.discordapp.com/avatars/1332927115590500423/08b0f03087601838f16b1a71ae1769be.png?size=240",
            "https://cdn.discordapp.com/avatars/1157115675828047933/3437e68a9d2ebc4af62aba68bb562d8a.png?size=160",
            "https://cdn.discordapp.com/avatars/290528554540597249/1c0dc7ec081e0b601f235d3c136c3f46.png?size=160",
            "https://cdn.discordapp.com/avatars/387291057810833408/3133f498fa2b7d545193415491d27dd1.png?size=160",
        ],
        "name": ['Alekan Serrao', 'Siddhant Madhur', 'Raghav Bhatia', 'Manav Shock'],
        "money_s": total_money_s,
        "money_f": total_money_f,
    }
    df = pd.DataFrame(data)
    df.sort_values(by='money_f', ascending=False,inplace=True)
    df = df.reset_index(drop=True)
    print(df)

    hti = Html2Image()
    f = open('index.html')
    html_str_raw= f.read()
    env = jinja2.Environment()
    template = env.from_string(html_str_raw)


    format_arr = [[row['name'], row['money_s'], row['profile_pfp'], idx] for idx, row in df.iterrows()]
    html_str = template.render(users=format_arr)
    hti.screenshot(html_str, save_as='output_from_file.png', size=(800, 800) )

    img = Image.open('output_from_file.png')
    bbox = img.getbbox()
    if bbox:
        trimmed_img = img.crop(bbox)
        ratio = trimmed_img.size[0] / trimmed_img.size[1] 
        length = 320
        trimmed_img = trimmed_img.resize((int(length * ratio), length), Image.Resampling.LANCZOS)
        trimmed_img.save("processed_img.png")
        return trimmed_img

def run_discord():
    DISCORD_TOKEN = os.getenv('DISCORD_API_KEY')
    print("TOKEN ", DISCORD_TOKEN)
    if DISCORD_TOKEN is None:
        exit(1)
    
    headers = {
        "Authorization": f"Bot {DISCORD_TOKEN}",
        "User-Agent": f"DiscordBot"
    } 

    files = {
        "file" : ("./processed_img.png", open("./processed_img.png", 'rb')) # The picture that we want to send in binary
    }

    channel_id = 1232893663361892376 
    prod_channel_id = 1344793378159726593
    BASE_URL = f"https://discord.com/api/v9"
    SEND_URL = BASE_URL + "/channels/{id}/messages"
    r = requests.post(SEND_URL.format(id=channel_id), headers=headers, files=files)
    

def main():
    create_leaderboard_img()
    run_discord()

main()