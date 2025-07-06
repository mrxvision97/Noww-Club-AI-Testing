import streamlit as st
import re
from typing import Dict, Any, Optional
from core.auth import AuthenticationManager
from core.session_manager import SessionManager

class AuthInterface:
    def __init__(self, auth_manager: AuthenticationManager, session_manager: SessionManager):
        self.auth_manager = auth_manager
        self.session_manager = session_manager
    
    def validate_email(self, email: str) -> bool:
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    def validate_password(self, password: str) -> tuple[bool, str]:
        """Validate password strength"""
        if len(password) < 8:
            return False, "Password must be at least 8 characters long"
        if not re.search(r'[A-Z]', password):
            return False, "Password must contain at least one uppercase letter"
        if not re.search(r'[a-z]', password):
            return False, "Password must contain at least one lowercase letter"
        if not re.search(r'\d', password):
            return False, "Password must contain at least one number"
        return True, ""
    
    def render_auth_interface(self):
        """Render the authentication interface"""
        st.markdown("""
        <div style="text-align: center; padding: 40px 0; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 15px; margin-bottom: 30px; box-shadow: 0 6px 20px rgba(0,0,0,0.1);">
            <h1 style="color: white; font-size: 3rem; font-weight: 700; margin-bottom: 10px; text-shadow: 0 2px 4px rgba(0,0,0,0.3);">
                🤝 Welcome to Noww Club AI
            </h1>
            <p style="color: #E6E6FA; font-size: 1.2rem; font-weight: 500; margin: 0;">
                Your Personalized AI Companion with Memory & Intelligence
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Authentication tabs
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "🔐 Local Sign In", 
            "👤 Local Sign Up", 
            "📧 Supabase Email", 
            "📱 Supabase Phone", 
            "🌐 OAuth"
        ])
        
        with tab1:
            self.render_signin_form()
        
        with tab2:
            self.render_signup_form()
            
        with tab3:
            self.render_supabase_email_auth()
            
        with tab4:
            self.render_supabase_phone_auth()
        
        with tab5:
            self.render_oauth_options()
    
    def render_signin_form(self):
        """Render the sign-in form"""
        st.markdown("### 🔐 Sign In to Your Account")
        
        with st.form("signin_form"):
            email = st.text_input("📧 Email Address", placeholder="Enter your email")
            password = st.text_input("🔒 Password", type="password", placeholder="Enter your password")
            
            col1, col2 = st.columns(2)
            with col1:
                signin_button = st.form_submit_button("🚀 Sign In", type="primary", use_container_width=True)
            with col2:
                forgot_password = st.form_submit_button("🔄 Forgot Password?", use_container_width=True)
            
            if signin_button:
                if not email or not password:
                    st.error("Please fill in all fields")
                elif not self.validate_email(email):
                    st.error("Please enter a valid email address")
                else:
                    with st.spinner("Signing in..."):
                        user_info = self.auth_manager.authenticate_user(email, password)
                        
                        if user_info:
                            st.success("✅ Successfully signed in!")
                            self.session_manager.login_user(user_info)
                            st.rerun()
                        else:
                            st.error("❌ Invalid email or password")
            
            if forgot_password:
                st.info("🔔 Password reset functionality will be implemented soon. Please contact support.")
    
    def render_signup_form(self):
        """Render the sign-up form"""
        st.markdown("### 👤 Create Your Account")
        
        with st.form("signup_form"):
            full_name = st.text_input("👤 Full Name", placeholder="Enter your full name")
            email = st.text_input("📧 Email Address", placeholder="Enter your email")
            password = st.text_input("🔒 Password", type="password", placeholder="Create a password")
            confirm_password = st.text_input("🔒 Confirm Password", type="password", placeholder="Confirm your password")
            
            terms_agreed = st.checkbox("I agree to the Terms of Service and Privacy Policy")
            
            signup_button = st.form_submit_button("🌟 Create Account", type="primary", use_container_width=True)
            
            if signup_button:
                if not all([full_name, email, password, confirm_password]):
                    st.error("Please fill in all fields")
                elif not self.validate_email(email):
                    st.error("Please enter a valid email address")
                elif password != confirm_password:
                    st.error("Passwords do not match")
                elif not terms_agreed:
                    st.error("Please agree to the Terms of Service and Privacy Policy")
                else:
                    is_valid, error_msg = self.validate_password(password)
                    if not is_valid:
                        st.error(error_msg)
                    else:
                        with st.spinner("Creating your account..."):
                            result = self.auth_manager.register_user(email, password, full_name)
                            
                            if "error" in result:
                                st.error(f"❌ {result['error']}")
                            else:
                                st.success("✅ Account created successfully! Please sign in.")
                                st.balloons()
    
    def render_oauth_options(self):
        """Render OAuth authentication options"""
        st.markdown("### 🌐 OAuth Sign In Options")
        
        # Check for OAuth callback first
        query_params = st.query_params
        if query_params and ('code' in query_params or 'error' in query_params):
            st.info("🔄 Processing OAuth callback...")
            self.handle_oauth_callback(query_params)
            return
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("#### Direct Google OAuth")
            if st.button("🔗 Google (Direct)", use_container_width=True, help="Direct Google OAuth integration"):
                self.handle_google_auth()
        
        with col2:
            st.markdown("#### Supabase Google OAuth")
            if st.button("🔗 Google (Supabase)", use_container_width=True, help="Google OAuth through Supabase"):
                self.handle_supabase_google_auth()
        
        with col3:
            st.markdown("#### Legacy Supabase Auth")
            if st.button("🔗 Supabase Legacy", use_container_width=True, help="Legacy Supabase authentication"):
                self.render_supabase_legacy_auth()
    
    def handle_supabase_google_auth(self):
        """Handle Google OAuth through Supabase"""
        if not self.auth_manager.supabase_client:
            st.error("❌ Supabase authentication is not configured")
            return
        
        try:
            result = self.auth_manager.supabase_auth(action="google_oauth")
            if result and "oauth_url" in result:
                st.markdown(f"""
                <div style="text-align: center; margin: 20px 0;">
                    <a href="{result['oauth_url']}" target="_self" style="
                        background: linear-gradient(135deg, #4285f4 0%, #34a853 50%, #fbbc05 75%, #ea4335 100%);
                        color: white;
                        padding: 12px 24px;
                        text-decoration: none;
                        border-radius: 8px;
                        font-weight: bold;
                        display: inline-block;
                        box-shadow: 0 4px 12px rgba(66, 133, 244, 0.3);
                        transition: transform 0.2s;
                    " onmouseover="this.style.transform='scale(1.05)'" onmouseout="this.style.transform='scale(1)'">
                        🔗 Continue with Google (Supabase)
                    </a>
                </div>
                """, unsafe_allow_html=True)
                
                st.info("🔄 You will be redirected to Google for authentication via Supabase")
            else:
                st.error("❌ Failed to initiate Google OAuth through Supabase")
        except Exception as e:
            st.error(f"❌ Supabase Google OAuth error: {str(e)}")
    
    def render_supabase_legacy_auth(self):
        """Render legacy Supabase authentication form"""
        if not self.auth_manager.supabase_client:
            st.error("Supabase authentication is not configured")
            return
        
        st.markdown("#### Legacy Supabase Authentication")
        with st.form("supabase_legacy_auth"):
            email = st.text_input("📧 Email for Supabase", placeholder="Enter your email")
            password = st.text_input("🔒 Password", type="password", placeholder="Enter your password")
            
            col1, col2 = st.columns(2)
            with col1:
                signin_btn = st.form_submit_button("Sign In", use_container_width=True)
            with col2:
                signup_btn = st.form_submit_button("Sign Up", use_container_width=True)
            
            if signin_btn or signup_btn:
                if not email or not password:
                    st.error("Please fill in all fields")
                elif not self.validate_email(email):
                    st.error("Please enter a valid email address")
                else:
                    action = "sign_up" if signup_btn else "sign_in"
                    with st.spinner(f"Processing {action}..."):
                        result = self.auth_manager.supabase_auth(email, password, action)
                        
                        if result and "error" not in result:
                            st.success("✅ Successfully authenticated with Supabase!")
                            self.session_manager.login_user(result)
                            st.rerun()
                        elif result and "error" in result:
                            st.error(f"❌ {result['error']}")
                        else:
                            st.error("Authentication failed")
    
    def handle_google_auth(self):
        """Handle Google OAuth authentication"""
        try:
            flow = self.auth_manager.google_auth_flow()
            if flow:
                authorization_url, state = flow.authorization_url(
                    access_type='offline',
                    include_granted_scopes='true'
                )
                
                # Store state in session for verification
                st.session_state.oauth_state = state
                
                st.markdown(f"""
                <div style="text-align: center; margin: 20px 0;">
                    <a href="{authorization_url}" target="_self" style="
                        background: linear-gradient(135deg, #4285f4 0%, #34a853 50%, #fbbc05 75%, #ea4335 100%);
                        color: white;
                        padding: 12px 24px;
                        text-decoration: none;
                        border-radius: 8px;
                        font-weight: bold;
                        display: inline-block;
                        box-shadow: 0 4px 12px rgba(66, 133, 244, 0.3);
                        transition: transform 0.2s;
                    " onmouseover="this.style.transform='scale(1.05)'" onmouseout="this.style.transform='scale(1)'">
                        🔗 Continue with Google
                    </a>
                </div>
                """, unsafe_allow_html=True)
                
                st.info("🔄 You will be redirected to Google for authentication")
            else:
                st.error("❌ Google OAuth is not configured. Please check your environment variables.")
                st.info("Make sure GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET are set in your .env file")
        except Exception as e:
            st.error(f"Google OAuth error: {str(e)}")
            print(f"Google OAuth exception: {e}")
    
    def render_supabase_auth(self):
        """Render Supabase authentication form"""
        if not self.auth_manager.supabase_client:
            st.error("Supabase authentication is not configured")
            return
        
        with st.form("supabase_auth"):
            email = st.text_input("📧 Email for Supabase", placeholder="Enter your email")
            password = st.text_input("🔒 Password", type="password", placeholder="Enter your password")
            
            col1, col2 = st.columns(2)
            with col1:
                signin_btn = st.form_submit_button("Sign In", use_container_width=True)
            with col2:
                signup_btn = st.form_submit_button("Sign Up", use_container_width=True)
            
            if signin_btn or signup_btn:
                if not email or not password:
                    st.error("Please fill in all fields")
                elif not self.validate_email(email):
                    st.error("Please enter a valid email address")
                else:
                    action = "sign_up" if signup_btn else "sign_in"
                    with st.spinner(f"Processing {action}..."):
                        result = self.auth_manager.supabase_auth(email, password, action)
                        
                        if result and "error" not in result:
                            st.success("✅ Successfully authenticated with Supabase!")
                            self.session_manager.login_user(result)
                            st.rerun()
                        elif result and "error" in result:
                            st.error(f"❌ {result['error']}")
                        else:
                            st.error("Authentication failed")
    
    def render_supabase_email_auth(self):
        """Render Supabase email authentication with OTP verification"""
        st.markdown("### 📧 Supabase Email Authentication")
        
        if not self.auth_manager.supabase_client:
            st.error("❌ Supabase authentication is not configured")
            st.info("Please check your SUPABASE_URL and SUPABASE_KEY in the .env file")
            return
        
        # Check if we're in OTP verification mode
        if st.session_state.get('awaiting_email_otp'):
            self.render_email_otp_verification()
            return
        
        # Email signup/signin form
        auth_type = st.radio("Choose action:", ["Sign In", "Sign Up"], key="supabase_email_type")
        
        with st.form("supabase_email_form"):
            email = st.text_input("📧 Email Address", placeholder="Enter your email")
            password = st.text_input("🔒 Password", type="password", placeholder="Enter your password")
            
            if auth_type == "Sign Up":
                confirm_password = st.text_input("🔒 Confirm Password", type="password", placeholder="Confirm your password")
                full_name = st.text_input("👤 Full Name", placeholder="Enter your full name (optional)")
            
            submit_btn = st.form_submit_button(
                f"📧 {auth_type} with Email", 
                type="primary", 
                use_container_width=True
            )
            
            if submit_btn:
                if not email or not password:
                    st.error("Please fill in all required fields")
                elif not self.validate_email(email):
                    st.error("Please enter a valid email address")
                elif auth_type == "Sign Up" and password != confirm_password:
                    st.error("Passwords do not match")
                else:
                    with st.spinner(f"{auth_type}..."):
                        if auth_type == "Sign Up":
                            result = self.auth_manager.supabase_auth(
                                email=email, 
                                password=password, 
                                action="sign_up_email"
                            )
                            
                            if result and "success" in result:
                                st.success("✅ " + result["message"])
                                st.session_state.awaiting_email_otp = True
                                st.session_state.temp_email = email
                                st.session_state.temp_name = full_name
                                st.rerun()
                            elif result and "error" in result:
                                st.error(f"❌ {result['error']}")
                        else:
                            result = self.auth_manager.supabase_auth(
                                email=email,
                                password=password,
                                action="sign_in_email"
                            )
                            
                            if result and "error" not in result:
                                st.success("✅ Successfully signed in!")
                                self.session_manager.login_user(result)
                                st.rerun()
                            elif result and "error" in result:
                                st.error(f"❌ {result['error']}")
    
    def render_email_otp_verification(self):
        """Render email OTP verification form"""
        st.markdown("### 📧 Email Verification")
        st.info("📬 Please check your email for the verification code")
        
        with st.form("email_otp_form"):
            otp = st.text_input("🔢 Enter Verification Code", placeholder="Enter 6-digit code from email")
            
            col1, col2 = st.columns(2)
            with col1:
                verify_btn = st.form_submit_button("✅ Verify", type="primary", use_container_width=True)
            with col2:
                resend_btn = st.form_submit_button("🔄 Resend Code", use_container_width=True)
            
            if verify_btn:
                if not otp:
                    st.error("Please enter the verification code")
                else:
                    with st.spinner("Verifying..."):
                        result = self.auth_manager.supabase_auth(
                            email=st.session_state.temp_email,
                            otp=otp,
                            action="verify_otp"
                        )
                        
                        if result and "error" not in result:
                            st.success("✅ Email verified successfully!")
                            # Clear temporary session data
                            del st.session_state.awaiting_email_otp
                            del st.session_state.temp_email
                            if 'temp_name' in st.session_state:
                                del st.session_state.temp_name
                            
                            self.session_manager.login_user(result)
                            st.rerun()
                        else:
                            st.error(f"❌ {result.get('error', 'Verification failed')}")
            
            if resend_btn:
                with st.spinner("Resending..."):
                    result = self.auth_manager.supabase_auth(
                        email=st.session_state.temp_email,
                        action="resend_otp"
                    )
                    if result and "success" in result:
                        st.success("✅ Verification code resent!")
                    else:
                        st.error("❌ Failed to resend code")
        
        # Cancel button
        if st.button("❌ Cancel", key="cancel_email_otp"):
            del st.session_state.awaiting_email_otp
            del st.session_state.temp_email
            if 'temp_name' in st.session_state:
                del st.session_state.temp_name
            st.rerun()
    
    def render_supabase_phone_auth(self):
        """Render Supabase phone authentication with SMS OTP"""
        st.markdown("### 📱 Supabase Phone Authentication")
        
        if not self.auth_manager.supabase_client:
            st.error("❌ Supabase authentication is not configured")
            st.info("Please check your SUPABASE_URL and SUPABASE_KEY in the .env file")
            return
        
        # Check if we're in OTP verification mode
        if st.session_state.get('awaiting_phone_otp'):
            self.render_phone_otp_verification()
            return
        
        # Phone signup/signin form
        auth_type = st.radio("Choose action:", ["Sign In", "Sign Up"], key="supabase_phone_type")
        
        with st.form("supabase_phone_form"):
            phone = st.text_input("📱 Phone Number", placeholder="+1234567890 (include country code)")
            password = st.text_input("🔒 Password", type="password", placeholder="Enter your password")
            
            if auth_type == "Sign Up":
                confirm_password = st.text_input("🔒 Confirm Password", type="password", placeholder="Confirm your password")
                full_name = st.text_input("👤 Full Name", placeholder="Enter your full name (optional)")
            
            submit_btn = st.form_submit_button(
                f"📱 {auth_type} with Phone", 
                type="primary", 
                use_container_width=True
            )
            
            if submit_btn:
                if not phone or not password:
                    st.error("Please fill in all required fields")
                elif not phone.startswith('+') or len(phone) < 10:
                    st.error("Please enter a valid phone number with country code (e.g., +1234567890)")
                elif auth_type == "Sign Up" and password != confirm_password:
                    st.error("Passwords do not match")
                else:
                    with st.spinner(f"{auth_type}..."):
                        if auth_type == "Sign Up":
                            result = self.auth_manager.supabase_auth(
                                phone=phone,
                                password=password,
                                action="sign_up_phone"
                            )
                            
                            if result and "success" in result:
                                st.success("✅ " + result["message"])
                                st.session_state.awaiting_phone_otp = True
                                st.session_state.temp_phone = phone
                                st.session_state.temp_name = full_name
                                st.rerun()
                            elif result and "error" in result:
                                st.error(f"❌ {result['error']}")
                        else:
                            result = self.auth_manager.supabase_auth(
                                phone=phone,
                                password=password,
                                action="sign_in_phone"
                            )
                            
                            if result and "error" not in result:
                                st.success("✅ Successfully signed in!")
                                self.session_manager.login_user(result)
                                st.rerun()
                            elif result and "error" in result:
                                st.error(f"❌ {result['error']}")
    
    def render_phone_otp_verification(self):
        """Render phone OTP verification form"""
        st.markdown("### 📱 Phone Verification")
        st.info(f"📲 Please check your phone ({st.session_state.temp_phone}) for the verification code")
        
        with st.form("phone_otp_form"):
            otp = st.text_input("🔢 Enter Verification Code", placeholder="Enter 6-digit SMS code")
            
            col1, col2 = st.columns(2)
            with col1:
                verify_btn = st.form_submit_button("✅ Verify", type="primary", use_container_width=True)
            with col2:
                resend_btn = st.form_submit_button("🔄 Resend Code", use_container_width=True)
            
            if verify_btn:
                if not otp:
                    st.error("Please enter the verification code")
                else:
                    with st.spinner("Verifying..."):
                        result = self.auth_manager.supabase_auth(
                            phone=st.session_state.temp_phone,
                            otp=otp,
                            action="verify_otp"
                        )
                        
                        if result and "error" not in result:
                            st.success("✅ Phone verified successfully!")
                            # Clear temporary session data
                            del st.session_state.awaiting_phone_otp
                            del st.session_state.temp_phone
                            if 'temp_name' in st.session_state:
                                del st.session_state.temp_name
                            
                            self.session_manager.login_user(result)
                            st.rerun()
                        else:
                            st.error(f"❌ {result.get('error', 'Verification failed')}")
            
            if resend_btn:
                with st.spinner("Resending..."):
                    result = self.auth_manager.supabase_auth(
                        phone=st.session_state.temp_phone,
                        action="resend_otp"
                    )
                    if result and "success" in result:
                        st.success("✅ Verification code resent!")
                    else:
                        st.error("❌ Failed to resend code")
        
        # Cancel button
        if st.button("❌ Cancel", key="cancel_phone_otp"):
            del st.session_state.awaiting_phone_otp
            del st.session_state.temp_phone
            if 'temp_name' in st.session_state:
                del st.session_state.temp_name
            st.rerun()
    
    def handle_oauth_callback(self, query_params: Dict[str, Any]):
        """Handle OAuth callback"""
        try:
            code = query_params.get('code')
            state = query_params.get('state')
            
            if code:
                print(f"OAuth callback received with code: {code[:10]}...")
                
                # Handle Google OAuth callback
                flow = self.auth_manager.google_auth_flow()
                if flow:
                    # Fetch token
                    token = flow.fetch_token(code=code)
                    print("Token fetched successfully")
                    
                    # Get user info from Google
                    from google.auth.transport.requests import Request
                    import requests
                    
                    headers = {'Authorization': f'Bearer {token["access_token"]}'}
                    response = requests.get('https://www.googleapis.com/oauth2/v2/userinfo', headers=headers)
                    
                    if response.status_code == 200:
                        user_data = response.json()
                        print(f"User data retrieved: {user_data.get('email')}")
                        
                        oauth_user = self.auth_manager.create_or_get_oauth_user(
                            email=user_data['email'],
                            full_name=user_data.get('name', ''),
                            avatar_url=user_data.get('picture'),
                            provider='google',
                            provider_id=user_data['id']
                        )
                        
                        if oauth_user:
                            st.success("✅ Successfully signed in with Google!")
                            self.session_manager.login_user(oauth_user)
                            
                            # Clear the query params to avoid reprocessing
                            st.query_params.clear()
                            
                            # Force a rerun to show the main app
                            st.rerun()
                        else:
                            st.error("❌ Failed to create/retrieve user account")
                    else:
                        st.error("❌ Failed to get user information from Google")
                        print(f"Google API error: {response.status_code} - {response.text}")
                else:
                    st.error("❌ Google OAuth flow not configured")
            else:
                error = query_params.get('error')
                if error:
                    st.error(f"❌ OAuth error: {error}")
                    
        except Exception as e:
            st.error(f"OAuth callback error: {str(e)}")
            print(f"OAuth callback exception: {e}")
            import traceback
            traceback.print_exc()
    
    def render_user_profile_dropdown(self):
        """Render user profile dropdown in the main app"""
        user_info = self.session_manager.get_user_info()
        
        if user_info:
            with st.sidebar:
                st.markdown("---")
                
                # User profile section
                if user_info.get('avatar_url'):
                    st.image(user_info['avatar_url'], width=50)
                
                st.markdown(f"**👤 {user_info['full_name']}**")
                st.markdown(f"📧 {user_info['email']}")
                
                # Logout button
                if st.button("🚪 Logout", use_container_width=True):
                    self.session_manager.logout_user()
                    st.rerun()
                
                st.markdown("---")
    
    def render_chat_session_sidebar(self):
        """Render chat session management in sidebar"""
        if not self.session_manager.is_authenticated():
            return
        
        with st.sidebar:
            st.markdown("### 💬 Chat Sessions")
            
            # New chat button
            if st.button("➕ New Chat", use_container_width=True):
                session_id = self.session_manager.create_new_chat_session()
                if session_id:
                    st.rerun()
            
            # List existing chat sessions
            chat_sessions = self.session_manager.get_chat_sessions()
            current_session = self.session_manager.get_current_chat_session()
            
            for session in chat_sessions:
                session_id = session['id']
                session_name = session['session_name']
                
                # Create columns for session name and actions
                col1, col2, col3 = st.columns([3, 1, 1])
                
                with col1:
                    if st.button(
                        f"{'🔵' if session_id == current_session else '⚪'} {session_name}",
                        key=f"session_{session_id}",
                        use_container_width=True
                    ):
                        self.session_manager.switch_chat_session(session_id)
                        st.rerun()
                
                with col2:
                    if st.button("✏️", key=f"edit_{session_id}", help="Rename"):
                        st.session_state[f"rename_{session_id}"] = True
                        st.rerun()
                
                with col3:
                    if st.button("🗑️", key=f"delete_{session_id}", help="Delete"):
                        if self.session_manager.delete_chat_session(session_id):
                            st.rerun()
                
                # Rename form
                if st.session_state.get(f"rename_{session_id}"):
                    with st.form(f"rename_form_{session_id}"):
                        new_name = st.text_input("New name:", value=session_name)
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            if st.form_submit_button("✅ Save"):
                                if self.session_manager.rename_chat_session(session_id, new_name):
                                    st.session_state[f"rename_{session_id}"] = False
                                    st.rerun()
                        
                        with col2:
                            if st.form_submit_button("❌ Cancel"):
                                st.session_state[f"rename_{session_id}"] = False
                                st.rerun()
            
            if not chat_sessions:
                st.info("No chat sessions yet. Start a new conversation!")
            
            st.markdown("---")
