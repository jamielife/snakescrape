import requests
from bs4 import BeautifulSoup
from .forms import CreateNew
from django.shortcuts import render
import openai, os
from dotenv import load_dotenv

#Instantiate dotenv
load_dotenv()
api_key = os.getenv('OPENAI_API_KEY')

#Replace new lines with html breaks
def nl2br(text):
    return "<br>".join(text.splitlines())

def home(request):
    if request.method == 'POST':
        form = CreateNew(request.POST)
        if form.is_valid():
            formData = [ form.cleaned_data['url'], form.cleaned_data['jobTitle'], form.cleaned_data['pageElement'], form.cleaned_data['pageClass'] ]
        return render(request, "create.html", {'formData': formData })
    else:
        form = CreateNew()
        return render(request, "home.html", {'form': form }) 

def create(request):
    if request.method == 'POST':
        form = CreateNew(request.POST)
        if form.is_valid():
            url = form.cleaned_data['url']
            jobTitle = request.POST['jobTitle']
            jobInfo = request.POST['jobInfo']
            formElem = form.cleaned_data['pageElement']
            formClass = form.cleaned_data['pageClass']

            if url:
                try:
                    # Scrape the text from the website
                    response = requests.get(url, headers= {
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36',
                    })
                    soup = BeautifulSoup(response.content, "html.parser")

                except ConnectionError as err:
                    return render(request, "home.html", {'form': form , 'error': err })
                except requests.exceptions.RequestException as err:
                    return render(request, "home.html", {'form': form , 'error': err })                    
                
                if formClass:
                    text = soup.find(formElem,  {'class': formClass}).get_text()            
                elif formElem:
                    text = soup.find(formElem).get_text()
                else:
                    text = soup.find('body').get_text()

            elif jobInfo:
                    text = jobInfo

            else:
                return render(request, "home.html", {'form': form, 'error': "Either URL or Job Information is require. " })

            if api_key is not None:
                openai.api_key = api_key
                prompt  = f"Starting with 'Dear Hiring Manager', write a cover letter that's at least 400 words long for the position of {jobTitle} for an appicant named James Taylor. " 
                prompt2 = f"Use the following company bio to create the cover letter: '{text}'. "
                prompt3 = "Do not mention, 'enabling javascript', 'cookies', or anything about a 'degree', 'Bachelor's degree' or 'Master's degree'. "

                # response = openai.Completion.create(
                #     #engine="text-davinci-002",
                #     #engine="gpt-3.5-turbo-0613",
                #     model="gpt-3.5-turbo",
                #     prompt=prompt,
                #     temperature=0.5,
                #     max_tokens=1000,
                # )

                response = openai.ChatCompletion.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant."},
                        {"role": "user", "content": prompt + prompt2 + prompt3 },
                    ]                    
                )

                chatbot_reponse = nl2br(response['choices'][0]['message']['content'])

            return render(request, "create.html", {'data': chatbot_reponse})
                        

    else:
        form = CreateNew()
        return render(request, "home.html", {'form': form , 'error': "URL not found or formatted improperly" })