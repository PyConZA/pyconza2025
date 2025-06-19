from django.conf import settings
from django.shortcuts import render


MD_DIR_PATH = settings.BASE_DIR / "md_content"


def page_home(request):
    return render(request, "website/page_home.html")


def page_code_of_conduct(request):
    with open(MD_DIR_PATH / "page_code_of_conduct.md") as f:
        content = f.read()
    context = {"content": content}
    return render(request, "website/page_code_of_conduct.html", context=context)
