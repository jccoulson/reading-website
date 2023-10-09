from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from messaging.models import Message
from messaging.forms import MessageForm
from django.contrib.auth.models import User


@login_required(login_url='/login/')
def inbox(request):
    if (request.method == "GET" and "delete" in request.GET):
        id = request.GET["delete"]
        Message.objects.filter(id=id).delete()
        return redirect("/inbox/")
    else:
        incoming = Message.objects.filter(receiver=request.user)
        outgoing = Message.objects.filter(sender=request.user)
        context = {
            "incoming": incoming,
            "outgoing": outgoing
        }
    return render(request, 'messaging/inbox.html', context)

@login_required(login_url='/login/')
def compose(request):
    if (request.method == "POST"):
        if ("add" in request.POST):
            form = MessageForm(request.POST)
            if (form.is_valid()):
                newMsg = form.save(commit=False)
                newMsg.sender = request.user
                try:
                    newMsg.receiver = User.objects.get(username=form.cleaned_data["recipient"])
                except User.DoesNotExist:
                    context = {
                        "form_data": form,
                        "dne": form.cleaned_data["recipient"],
                    }
                    return render(request, "messaging/compose.html", context)
                newMsg.save()
                return redirect("/inbox/")
            else:
                context = {
                    "form_data": form
                }
                return render(request, "messaging/compose.html", context)
        else:
            return redirect("/inbox/")
    else:
        context = {
            "form_data": MessageForm()
        }
        return render(request, "messaging/compose.html", context)
