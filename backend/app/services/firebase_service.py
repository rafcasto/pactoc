import json
import base64
import firebase_admin
from firebase_admin import credentials, auth
from flask import current_app
import logging

logger = logging.getLogger(__name__)

class FirebaseService:
    """Service class for Firebase operations."""
    
    @staticmethod
    def initialize():
        """Initialize Firebase Admin SDK."""
        try:
            config = current_app.config
            
            if config.get('FIREBASE_SERVICE_ACCOUNT_KEY'):
                service_account_info = json.loads(config['FIREBASE_SERVICE_ACCOUNT_KEY'])
                cred = credentials.Certificate(service_account_info)
                logger.info("Using Firebase service account from environment variable")
                
            elif config.get('FIREBASE_SERVICE_ACCOUNT_BASE64'):
                encoded_key = config['FIREBASE_SERVICE_ACCOUNT_BASE64']
                decoded_key = base64.b64decode(encoded_key).decode('utf-8')
                service_account_info = json.loads(decoded_key)
                cred = credentials.Certificate(service_account_info)
                logger.info("Using Firebase service account from base64 environment variable")
                
            else:
                # Fallback to service account key file
                cred = credentials.Certificate(config['FIREBASE_SERVICE_ACCOUNT_FILE'])
                logger.info("Using Firebase service account from file")
            
            firebase_admin.initialize_app(cred)
            logger.info("Firebase Admin initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing Firebase: {e}")
            raise
    
    @staticmethod
    def verify_token(token):
        """Verify Firebase ID token."""
        try:
            decoded_token = auth.verify_id_token(token)
            return decoded_token, None
        except Exception as e:
            logger.error(f"Token verification failed: {e}")
            return None, str(e)
