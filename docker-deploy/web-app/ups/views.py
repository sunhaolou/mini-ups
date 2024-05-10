import os
import time

from django.contrib.auth import get_user_model, logout, update_session_auth_hash
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail

from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from sendgrid import Mail, SendGridAPIClient, To, Content, Email, sendgrid
from sendgrid.helpers.mail import subject

from .forms import AddressForm, ProfileUpdateForm, CustomSetPasswordForm
from .models import User, subscribeEmail
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.shortcuts import render
from .models import Package
from django.conf import settings

from django.shortcuts import render, redirect

from django.contrib import messages

import socket
from google.protobuf.internal.encoder import _VarintEncoder
from django.contrib.auth import authenticate



# connect to world, ups
def clientSocket(host, port):
    print("BEGINNING clientSocket...")
    client_fd = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_fd.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        client_fd.connect((host, port))
    except Exception as e:
        print(f"Failed to connect: {e}")
        raise
    print("client fd is:", client_fd)
    return client_fd

while True:
  try:
    print("try to connect to backedn: ")
    back_fd = clientSocket("ups", 8888)
    print("connect to back end succss")
    break
  except:
    time.sleep(3)
    continue

def send_msg(msg, socket):
    print("Sending message to backend...")
    string = str(msg)
    string_bytes = string.encode('utf-8')
    data = []
    _VarintEncoder()(data.append, len(string_bytes), None)
    size = b''.join(data)
    socket.sendall(size + string_bytes)
    print("Message sent successfully.")

    socket.close()
    print("Socket closed.")


def subscribe_email(request):
    if request.method == 'POST':
        print("this is subscribe email")

        email = request.POST.get('email')
        if email:

            if subscribeEmail.objects.filter(email=email).exists():
                messages.error(request, 'You have already subscribed to this！')
            else:
                new_subscription = subscribeEmail(email=email)
                new_subscription.save()
                messages.success(request, 'Congratulations, you have successfully subscribed!')
        else:
            messages.error(request, 'Please enter a valid email address')
        return redirect('index')



def contact_email(request):
    if request.method == 'POST':
        print("this is test message")
        name = request.POST.get('name')
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        request_message = request.POST.get('email')

        if not all([subject, message, request_message]):
            messages.error(request, 'Missing information. Please fill all fields.')
            return redirect('contact')  # Adjust 'contact' to your actual URL name for the contact page

        try:

            email_template_name = 'contact_email.txt'
            c = {
                "name": name,
                "subject": subject,
                "request_message": request_message

            }
            full_message = render_to_string(email_template_name, c)
            sendEmail(subject, request_message, full_message)
            messages.success(request, 'Email sent successfully!')
        except Exception as e:
            messages.error(request, f'Failed to send email. Error: {str(e)}')

        return redirect('contact')  # Adjust 'contact' to your actual URL name for the contact page
    else:
        return HttpResponse("Invalid request", status=400)



def sendEmail(subject, toEmail, message_content):
    sg = sendgrid.SendGridAPIClient(api_key=settings.SENDGRID_API_KEY)
    from_email = Email(settings.DEFAULT_FROM_EMAIL)
    to_email = To(toEmail)
    content = Content("text/plain", message_content)

    mail = Mail(from_email, to_email, subject, content)

    response = sg.client.mail.send.post(request_body=mail.get())

def contact_view(request):
    return render(request, "ups/contact.html")

def password_reset_complete(request):
    return render(request, 'ups/password_reset_complete.html')


def password_reset_confirm(request, uidb64=None, token=None):
    UserModel = get_user_model()
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = UserModel._default_manager.get(pk=uid)
    except (TypeError, ValueError, OverflowError, UserModel.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        if request.method == 'POST':
            form = CustomSetPasswordForm(user, request.POST)
            if form.is_valid():
                form.save()
                return redirect('password_reset_complete')
        else:
            form = CustomSetPasswordForm(user)
        return render(request, 'ups/password_reset_confirm.html', {'form': form})
    else:
        return HttpResponse('Password reset link is invalid, possibly because it has been used already.')

@csrf_exempt
def password_reset_request(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        associated_users = User.objects.filter(email=email, first_name=first_name, last_name=last_name)
        if associated_users.exists():
            for user in associated_users:
                subject = "Password Reset Requested"
                email_template_name = 'password_reset_email.txt'

                public_domain = 'localhost:8000'
                protocol = 'http'


                c = {
                    "email": user.email,
                    'domain': public_domain,
                    'site_name': 'Website',
                    "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                    "user": user,
                    "token": default_token_generator.make_token(user),
                    'protocol': protocol,
                }

                email = render_to_string(email_template_name, c)
                try:

                    sendEmail(subject, user.email, email)
                except Exception as e:

                    return HttpResponse('Invalid header found.')
                return redirect('login')
        else:
            messages.error(request, 'No user found with provided information. Please check your details and try again.')


    return render(request, 'ups/forgetPassword.html')






@csrf_exempt
def forget_password(request):
    return render(request, 'ups/forgetPassword.html')


@login_required
@require_http_methods(["POST"])
def update_destination(request, package_id):
    try:
        package = Package.objects.get(id=package_id, user=request.user)





        new_end_x = request.POST.get('newEndX')
        new_end_y = request.POST.get('newEndY')

        # Check if both new_end_x and new_end_y are provided
        if new_end_x and new_end_y:
            package.end_x = new_end_x
            package.end_y = new_end_y

            # connectServer(str(package.id))

            package.save()
            send_msg(package.id, back_fd)
            return JsonResponse({'success': True})
        else:
            # If one of the fields is empty, return an error
            return JsonResponse({'success': False, 'error': 'New destination coordinates cannot be empty.'})

    except Package.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Package not found.'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


def public_package_view(request, tracking_number):
    try:
        package = Package.objects.get(track_number=tracking_number)
        status_steps = {
            "p": "wait for pick up",
            "o": "out for delivery",
            "d": "delivered for delivery"
        }
        status_progress = [status_steps[status[0]] for status in Package.STATUS if status[0] in status_steps]

        current_status_index = status_progress.index(status_steps[package.package_status])
        status_progress = status_progress[:current_status_index + 1]

        data = {
            'track_number': package.track_number,
            'start_location':"({},{})".format(package.start_x, package.start_y),
            'end_location': "({},{})".format(package.end_x, package.end_y),
            'description': package.description,
            'status': status_progress,
            'current_status': package.get_package_status_display()
        }

        return JsonResponse({'success': True, 'data': data})
    except Package.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Package not found.'})


@login_required
def package_detail_view(request, package_id):
    try:
        package = Package.objects.get(id=package_id, user=request.user)
        status_steps = {
            "p": "wait for pick up",
            "o": "out for delivery",
            "d": "delivered for delivery"
        }
        status_progress = [status_steps[status[0]] for status in Package.STATUS if status[0] in status_steps]

        current_status_index = status_progress.index(status_steps[package.package_status])
        status_progress = status_progress[:current_status_index + 1]

        data = {
            'track_number': package.track_number,
            'start_location': "({}, {})".format(package.start_x, package.start_y),
            'end_location': "({}, {})".format(package.end_x, package.end_y),
            'description': package.description,
            'status': status_progress,
            'current_status': package.get_package_status_display()
        }
        print(data)
        return JsonResponse({'success': True, 'data': data})
    except Package.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Package not found.'})



def profile_view(request):

    if not request.user.is_authenticated:

        return redirect('login')


    packages = request.user.packages.all()

    return render(request, 'ups/profile.html', {'user': request.user, 'packages': packages})
@login_required
def profileUpdate_view(request):
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully.")
            return redirect('profile')
    else:
        form = ProfileUpdateForm(instance=request.user)
    return render(request, 'ups/profileUpdate.html', {'form': form})

@login_required
def passwordChange_view(request):
    if request.method == 'POST':
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            user = request.user
            if user.check_password(form.cleaned_data['current_password']):
                user.set_password(form.cleaned_data['new_password'])
                user.save()
                update_session_auth_hash(request, user)  # Keeps the user logged in after password change
                messages.success(request, "Password updated successfully.")
                return redirect('profile')  # Adjust the redirect if necessary
            else:
                form.add_error('current_password', 'Current password is incorrect.')
    else:
        form = PasswordChangeForm(user=request.user)  # Pass the user here too

    return render(request, 'ups/passwordUpdate.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('index')

def login_view(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('profile')
        else:
            return render(request, 'ups/login.html', {'error_message': 'Invalid password or username'})
    return render(request, 'ups/login.html')

def signup_view(request):
    User = get_user_model()
    error_message = None
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        username = request.POST.get('username')
        email = request.POST.get('email')
        phone_number = request.POST.get('phone_number')
        password1 = request.POST.get('password')
        password2 = request.POST.get('password_confirm')

        if not first_name:
            error_message = "First name cannot be empty."
        elif not last_name:
            error_message = "Last name cannot be empty."
        elif not username:
            error_message = "Username cannot be empty."
        elif User.objects.filter(username=username).exists():
            error_message = "This username is already taken."

        elif not email:
            error_message = "Email cannot be empty."
        elif User.objects.filter(email=email).exists():
            error_message = "This email is already taken"
        elif not phone_number:
            error_message = "Phone number cannot be empty."
        elif not password1:
            error_message = "Password cannot be empty."
        elif password1 != password2:
            error_message = "Passwords do not match."
        else:
            try:
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password1,
                    first_name=first_name,
                    last_name=last_name,
                    phone_number=phone_number
                )
                user.save()
                messages.success(request, "Registration successful.")
                return redirect('login')
            except Exception as e:
                error_message = f"An error occurred during registration: {str(e)}"

    return render(request, 'ups/signup.html', {'error_message': error_message})


@login_required
def logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect("index")

def service_view(request):
    return render(request, 'ups/service.html')
def index(request):
    return render(request, "ups/index.html")

def test(request):
    return render(request, "ups/test.html")