import {
    signInWithEmailAndPassword,
    createUserWithEmailAndPassword,
    signOut,
    sendPasswordResetEmail,
    updateProfile,
    UserCredential,
    AuthError,
  } from 'firebase/auth';
  import { auth } from './config';
  
  export const authService = {
    // Sign in with email and password
    async signIn(email: string, password: string): Promise<UserCredential> {
      try {
        return await signInWithEmailAndPassword(auth, email, password);
      } catch (error) {
        const authError = error as AuthError;
        throw new Error(authError.message || 'Failed to sign in');
      }
    },
  
    // Register with email and password
    async register(email: string, password: string, displayName?: string): Promise<UserCredential> {
      try {
        const userCredential = await createUserWithEmailAndPassword(auth, email, password);
        
        // Update profile with display name if provided
        if (displayName && userCredential.user) {
          await updateProfile(userCredential.user, { displayName });
        }
        
        return userCredential;
      } catch (error) {
        const authError = error as AuthError;
        throw new Error(authError.message || 'Failed to register');
      }
    },
  
    // Sign out
    async signOut(): Promise<void> {
      try {
        await signOut(auth);
      } catch (error) {
        const authError = error as AuthError;
        throw new Error(authError.message || 'Failed to sign out');
      }
    },
  
    // Reset password
    async resetPassword(email: string): Promise<void> {
      try {
        await sendPasswordResetEmail(auth, email);
      } catch (error) {
        const authError = error as AuthError;
        throw new Error(authError.message || 'Failed to send reset email');
      }
    },
  
    // Get current user's ID token
    async getIdToken(): Promise<string | null> {
      const user = auth.currentUser;
      if (user) {
        return await user.getIdToken();
      }
      return null;
    },
  };