import random
from django.core.mail import send_mail
from django.core.cache import cache
from django.contrib.auth import get_user_model
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from .serializer import UserProfileSerializer

User = get_user_model()

@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    '''Register User, register with email, username and password'''
    username = request.data.get('username')
    email = request.data.get('email')
    password = request.data.get('password')

    if not all([username, email, password]):
        return Response({'error': 'Username, email, and password are required.'}, status=status.HTTP_400_BAD_REQUEST)

    if User.objects.filter(username=username).exists():
        return Response({'error': 'Username already exists.'}, status=status.HTTP_400_BAD_REQUEST)
    if User.objects.filter(email=email).exists():
        return Response({'error': 'Email already exists.'}, status=status.HTTP_400_BAD_REQUEST)

    user = User.objects.create_user(username=username, email=email, password=password, is_active=False)
    user.save()

    otp = random.randint(100000, 999999)
    cache.set(f'registration_otp_{email}', otp, timeout=300)

    subject = "Registration OTP"
    message = f"Your OTP code for registration is: {otp}"
    from_email = "noreply@example.com"
    try:
        send_mail(subject, message, from_email, [email])
    except Exception as e:
        return Response({'error': f'Error sending email: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return Response({'message': 'Registration successful. An OTP has been sent to your email for verification.'},
                    status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([AllowAny])
def verify_registration(request):
    '''Verify new email on registration '''
    email = request.data.get('email')
    otp_input = request.data.get('otp')

    if not all([email, otp_input]):
        return Response({'error': 'Email and OTP are required.'}, status=status.HTTP_400_BAD_REQUEST)

    stored_otp = cache.get(f'registration_otp_{email}')
    if stored_otp and str(otp_input) == str(stored_otp):
        try:
            user = User.objects.get(email=email)
            user.is_active = True
            user.save()
            cache.delete(f'registration_otp_{email}')
            return Response({'message': 'Email verification successful. Your account is now active.'}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)
    else:
        return Response({'error': 'Invalid OTP.'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def profile(request):
    '''Get user pofile, return username and email'''

    serializer = UserProfileSerializer(request.user)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['PUT'])
def update_profile(request):
    '''Update profile request'''
    user = request.user
    data = request.data.copy()
    new_email = data.get('email')

    # If the email is being changed, send OTP to the new email.
    if new_email and new_email != user.email:
        otp = random.randint(100000, 999999)
        cache.set(f'update_email_otp_{user.id}', otp, timeout=300)
        cache.set(f'pending_new_email_{user.id}', new_email, timeout=300)

        subject = "Verify Your New Email"
        message = f"Your OTP for email change is: {otp}"
        try:
            send_mail(subject, message, "noreply@example.com", [new_email])
        except Exception as e:
            return Response({'error': f'Error sending email: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({'message': 'OTP sent to the new email address. Please verify to update email.'},
                        status=status.HTTP_200_OK)

    # If email is not changed, update other fields.
    serializer = UserProfileSerializer(user, data=data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def verify_email_update(request):
    ''' Veify new email update'''
    user = request.user
    otp_input = request.data.get('otp')
    stored_otp = cache.get(f'update_email_otp_{user.id}')
    pending_new_email = cache.get(f'pending_new_email_{user.id}')

    if not all([otp_input, stored_otp, pending_new_email]):
        return Response({'error': 'Missing OTP or pending email.'}, status=status.HTTP_400_BAD_REQUEST)

    if str(otp_input) == str(stored_otp):
        user.email = pending_new_email
        user.save()
        cache.delete(f'update_email_otp_{user.id}')
        cache.delete(f'pending_new_email_{user.id}')
        return Response({'message': 'Email updated successfully.'}, status=status.HTTP_200_OK)
    else:
        return Response({'error': 'Invalid OTP.'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def forgot_password(request):
    '''Handle fogot passwod request and an email OTP will be sent'''
    email = request.data.get('email')
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return Response({'error': 'User with this email does not exist.'}, status=status.HTTP_404_NOT_FOUND)

    otp = random.randint(100000, 999999)
    cache.set(f'forgot_password_otp_{user.id}', otp, timeout=300)
    
    subject = "Password Reset OTP"
    message = f"Your OTP for password reset is: {otp}"
    try:
        send_mail(subject, message, "noreply@example.com", [email])
    except Exception as e:
        return Response({'error': f'Error sending email: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    return Response({'message': 'OTP sent to your email.'}, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([AllowAny])
def verify_forgot_password(request):
    ''' Verify forgot-password OTP and reset password '''
    email = request.data.get('email')
    otp_input = request.data.get('otp')
    new_password = request.data.get('new_password')

    if not all([email, otp_input, new_password]):
        return Response({'error': 'Email, OTP, and new password are required.'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)

    stored_otp = cache.get(f'forgot_password_otp_{user.id}')
    if stored_otp and str(otp_input) == str(stored_otp):
        user.set_password(new_password)
        user.save()
        cache.delete(f'forgot_password_otp_{user.id}')
        return Response({'message': 'Password reset successfully.'}, status=status.HTTP_200_OK)
    else:
        return Response({'error': 'Invalid OTP.'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def change_password(request):
    ''' Endpoint to send change password OTP '''
    user = request.user
    otp = random.randint(100000, 999999)
    cache.set(f'change_password_otp_{user.id}', otp, timeout=300)
    
    subject = "Change Password OTP"
    message = f"Your OTP for password change is: {otp}"
    try:
        send_mail(subject, message, "noreply@example.com", [user.email])
    except Exception as e:
        return Response({'error': f'Error sending email: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    return Response({'message': 'OTP sent to your email.'}, status=status.HTTP_200_OK)


@api_view(['POST'])
def verify_change_password(request):
    ''' Endpoint to veify change password OTP and change password '''
    user = request.user
    otp_input = request.data.get('otp')
    new_password = request.data.get('new_password')
    stored_otp = cache.get(f'change_password_otp_{user.id}')

    if not all([otp_input, new_password, stored_otp]):
        return Response({'error': 'Missing data or OTP not requested.'}, status=status.HTTP_400_BAD_REQUEST)

    if str(otp_input) == str(stored_otp):
        user.set_password(new_password)
        user.save()
        cache.delete(f'change_password_otp_{user.id}')
        return Response({'message': 'Password changed successfully.'}, status=status.HTTP_200_OK)
    else:
        return Response({'error': 'Invalid OTP.'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def home(request):
    '''Home page endpoint'''
    return Response({"message": f"Welcome, {request.user.username}!"}, status=status.HTTP_200_OK)

@api_view(['POST'])
def logout_view(request):
    ''' Deleting access token'''
    return Response({"message": "Logout endpoint. Remove token client-side."}, status=status.HTTP_200_OK)
