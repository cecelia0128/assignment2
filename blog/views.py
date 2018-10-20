from .models import Post
from django.utils import timezone
from .forms import PostForm
from django.shortcuts import redirect
import json
from watson_developer_cloud import ToneAnalyzerV3
from watson_developer_cloud.tone_analyzer_v3 import ToneInput
from watson_developer_cloud import LanguageTranslatorV3
from django.shortcuts import render, get_object_or_404


language_translator = LanguageTranslatorV3(
        version='2018-05-31',
        iam_apikey='8z-wMioiofy1nGJiXqOWnMazw9Xxn6DmkDLUHgQ7RR4P',
         url='https://gateway.watsonplatform.net/language-translator/api'
)
service = ToneAnalyzerV3(
    ## url is optional, and defaults to the URL below. Use the correct URL for your region.
    # url='https://gateway.watsonplatform.net/tone-analyzer/api',
    username='35989440-c79d-4168-84bb-52da565dc665',
    password='CEegnYOtG3oV',
    version='2017-09-26')


def post_list(request):
    posts = Post.objects.filter(published_date__lte=timezone.now()).order_by('published_date')

    for post in posts:
        posting = post.text

        translation = language_translator.translate(
            text= post.text, model_id='en-es').get_result()
        obj = (json.dumps(translation, indent=2, ensure_ascii=False))
        print(obj)
        obj2 = json.loads(obj)
        post.obj2 = obj2['translations'][0]['translation']
        post.w_count = obj2['word_count']
        post.c_count = obj2['character_count']
        tone_input = ToneInput(post.text)
        tone = service.tone(tone_input=tone_input, content_type="application/json")
        tone2 = str(tone)
        print(tone2)
        post.tone3 = ""
        #print(post.tone3)
        temp = json.loads(tone2)
        if(len(temp['result']['document_tone']['tones'])>0):
            temp2 = temp['result']['document_tone']['tones']
            for x in temp2:
                post.tone3 += 'Tone name: '+ x['tone_name'] + '\t'+ '|\tScore: '+str(x['score'])+'\r'
        else:
            post.tone3 = 'Tone name: n/a\t|\tScore: n/a'


    return render(request, 'blog/post_list.html', {'posts': posts})




def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    return render(request, 'blog/post_detail.html', {'post': post})


def post_new(request):
    if request.method == "POST":
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.published_date = timezone.now()
            post.save()
            return redirect('post_detail', pk=post.pk)
    else:
        form = PostForm()
    return render(request, 'blog/post_edit.html', {'form': form})
def post_edit(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.method == "POST":
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.published_date = timezone.now()
            post.save()
            return redirect('post_detail', pk=post.pk)
    else:
        form = PostForm(instance=post)
    return render(request, 'blog/post_edit.html', {'form': form})



