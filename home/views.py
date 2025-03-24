from django.contrib.auth import authenticate, login, logout, get_user_model

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import random
from django.core.mail import send_mail
from rest_framework.permissions import IsAuthenticated
from .serializer import UserProfileSerializer
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

User = get_user_model()

# Create your views here.
from django.http import HttpResponse


class LoginAPIView(APIView):
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        
        if not username or not password:
            return Response({'error': 'Please provide both username and password.'}, 
                            status=status.HTTP_400_BAD_REQUEST)
        
        user = authenticate(username=username, password=password)
        if user:
            login(request, user)
            return Response({'message': 'Login Successful.'}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Invalid credentials.'}, status=status.HTTP_401_UNAUTHORIZED)
        
class RegisterAPIView(APIView):
    def post(self, request):
        username = request.data.get('username')
        email = request.data.get('email')
        password = request.data.get('password')
        
        if not all([username, email, password]):
            return Response({'error': 'Username, email, and password are required.'}, 
                            status=status.HTTP_400_BAD_REQUEST)
        
        if User.objects.filter(username=username).exists():
            return Response({'error': 'Username already exists.'}, status=status.HTTP_400_BAD_REQUEST)
        if User.objects.filter(email=email).exists():
            return Response({'error': 'Email already exists.'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Create user as inactive until email verification is complete.
        user = User.objects.create_user(username=username, email=email, password=password, is_active=False)
        user.save()
        
        # Generate OTP (6-digit code)
        otp = random.randint(100000, 999999)
        
        # Store OTP and user info in session (or use a custom model/cache for stateless APIs)
        request.session['otp'] = otp
        request.session['user_id'] = user.id
        
        # Send OTP via email
        subject = "OTP Code"
        message = f"Your OTP code is: {otp}"
        from_email = "precert@email.com"
        recipient_list = [email]
        
        try:
            send_mail(subject, message, from_email, recipient_list)
        except Exception as e:
            return Response({'error': f'Error sending email: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response({'message': 'Registration successful. An OTP has been sent to your email for verification.'},
                        status=status.HTTP_201_CREATED)
        
class VerifyOTPAPIView(APIView):
    def post(self, request):
        otp_input = request.data.get('otp')
        stored_otp = request.session.get('otp')
        user_id = request.session.get('user_id')
        
        if not otp_input:
            return Response({'error': 'OTP is required.'}, status=status.HTTP_400_BAD_REQUEST)
        
        if str(otp_input) == str(stored_otp):
            try:
                user = User.objects.get(id=user_id)
                user.is_active = True
                user.save()
                # Optionally, clear the session values for OTP
                request.session.pop('otp', None)
                request.session.pop('user_id', None)
                return Response({'message': 'Email verification successful. Your account is now active.'},
                                status=status.HTTP_200_OK)
            except User.DoesNotExist:
                return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({'error': 'Invalid OTP.'}, status=status.HTTP_400_BAD_REQUEST)


class HomeAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Return a simple welcome message along with the username
        return Response({"message": f"Welcome, {request.user.username}!"}, status=status.HTTP_200_OK)
    
    
class LogoutAPIView(APIView):
    def post(self, request):
        logout(request)
        return Response({"message": "Logged out successfully!"}, status=status.HTTP_200_OK)
    
class ProfileAPIView(APIView):
    """
    Retrieve the profile of the authenticated user.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

@method_decorator(csrf_exempt, name='dispatch')
class UpdateProfileAPIView(APIView):
    """
    Update the profile of the authenticated user.
    If the email is changed, an OTP will be sent to the new email.
    """
    permission_classes = [IsAuthenticated]

    def put(self, request):
        user = request.user
        data = request.data.copy()

        new_email = data.get('email')
        if new_email and new_email != user.email:
            # Generate OTP for email verification.
            otp = random.randint(100000, 999999)
            # Store OTP and the pending new email in session.
            request.session['update_email_otp'] = otp
            request.session['pending_new_email'] = new_email

            # Send the OTP to the new email.
            subject = "Verify Your New Email"
            message = f"Your OTP for email change is: {otp}"
            send_mail(subject, message, "noreply@example.com", [new_email])

            return Response(
                {'message': 'OTP sent to the new email address. Please verify to update email.'},
                status=status.HTTP_200_OK
            )

        # Update other fields (e.g., username)
        serializer = UserProfileSerializer(user, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class VerifyEmailUpdateAPIView(APIView):
    """
    Verify the OTP for an email update and then update the user's email.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        otp_input = request.data.get('otp')
        session_otp = request.session.get('update_email_otp')
        pending_new_email = request.session.get('pending_new_email')

        if not otp_input or not session_otp or not pending_new_email:
            return Response({'error': 'Missing OTP or pending email.'}, status=status.HTTP_400_BAD_REQUEST)

        if str(otp_input) == str(session_otp):
            user = request.user
            user.email = pending_new_email
            user.save()
            # Clear the session data.
            request.session.pop('update_email_otp')
            request.session.pop('pending_new_email')
            return Response({'message': 'Email updated successfully.'}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Invalid OTP.'}, status=status.HTTP_400_BAD_REQUEST)

# --- Forgot Password Endpoints ---

class ForgotPasswordAPIView(APIView):
    """
    Initiate a password reset by sending an OTP to the user's email.
    """
    def post(self, request):
        email = request.data.get('email')
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'error': 'User with this email does not exist.'}, status=status.HTTP_404_NOT_FOUND)

        otp = random.randint(100000, 999999)
        # Store OTP and the user ID in session.
        request.session['forgot_password_otp'] = otp
        request.session['forgot_password_user_id'] = user.id

        subject = "Password Reset OTP"
        message = f"Your OTP for password reset is: {otp}"
        send_mail(subject, message, "noreply@example.com", [email])
        return Response({'message': 'OTP sent to your email.'}, status=status.HTTP_200_OK)


class VerifyForgotPasswordAPIView(APIView):
    """
    Verify the OTP and reset the user's password.
    """
    def post(self, request):
        otp_input = request.data.get('otp')
        new_password = request.data.get('new_password')
        session_otp = request.session.get('forgot_password_otp')
        user_id = request.session.get('forgot_password_user_id')

        if not otp_input or not new_password or not session_otp or not user_id:
            return Response({'error': 'Missing data or OTP not requested.'}, status=status.HTTP_400_BAD_REQUEST)

        if str(otp_input) == str(session_otp):
            try:
                user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)

            user.set_password(new_password)
            user.save()
            # Clear the session.
            request.session.pop('forgot_password_otp')
            request.session.pop('forgot_password_user_id')
            return Response({'message': 'Password reset successfully.'}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Invalid OTP.'}, status=status.HTTP_400_BAD_REQUEST)

# --- Change Password Endpoints for Authenticated Users ---

class ChangePasswordAPIView(APIView):
    """
    Request an OTP for changing the password of an authenticated user.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        otp = random.randint(100000, 999999)
        request.session['change_password_otp'] = otp
        request.session['change_password_user_id'] = user.id

        subject = "Change Password OTP"
        message = f"Your OTP for password change is: {otp}"
        send_mail(subject, message, "noreply@example.com", [user.email])
        return Response({'message': 'OTP sent to your email.'}, status=status.HTTP_200_OK)


class VerifyChangePasswordAPIView(APIView):
    """
    Verify the OTP and change the password for an authenticated user.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        otp_input = request.data.get('otp')
        new_password = request.data.get('new_password')
        session_otp = request.session.get('change_password_otp')
        user_id = request.session.get('change_password_user_id')

        if not otp_input or not new_password or not session_otp or not user_id:
            return Response({'error': 'Missing data or OTP not requested.'}, status=status.HTTP_400_BAD_REQUEST)

        if str(otp_input) == str(session_otp) and user_id == request.user.id:
            user = request.user
            user.set_password(new_password)
            user.save()
            request.session.pop('change_password_otp')
            request.session.pop('change_password_user_id')
            return Response({'message': 'Password changed successfully.'}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Invalid OTP or unauthorized.'}, status=status.HTTP_400_BAD_REQUEST)
