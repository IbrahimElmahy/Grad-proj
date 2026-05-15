import 'models/app_user.dart';

class AuthSession {
  AuthSession._();

  static String? token;
  static AppUser? user;

  static bool get isSignedIn => token != null && user != null;

  static void setSession({required String newToken, required AppUser newUser}) {
    token = newToken;
    user = newUser;
  }

  static void clear() {
    token = null;
    user = null;
  }
}
