from django.shortcuts import render


def page_home(request):
    return render(request, "website/page_home.html")


def page_tickets(request):
    return render(request, "website/page_tickets.html")


def page_friends_of_pycon_africa(request):
    return render(request, "website/page_friends_of_pycon_africa.html")
