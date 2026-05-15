import '../../../core/network/api_client.dart';
import 'auth_session.dart';
import 'models/app_user.dart';

class AuthService {
  const AuthService({this.apiClient = const ApiClient()});

  final ApiClient apiClient;

  Future<AppUser> login({
    required String email,
    required String password,
  }) async {
    final json = await apiClient.postJson('/api/auth/login/', {
      'email': email,
      'password': password,
    }) as Map<String, dynamic>;

    final user = AppUser.fromJson(json['user'] as Map<String, dynamic>);
    AuthSession.setSession(
      newToken: json['token'] as String? ?? '',
      newUser: user,
    );
    return user;
  }

  Future<PasswordResetRequest> forgotPassword(String email) async {
    final json = await apiClient.postJson('/api/auth/forgot-password/', {
      'email': email,
    }) as Map<String, dynamic>;

    return PasswordResetRequest(
      email: json['email'] as String? ?? email,
      token: json['token'] as String? ?? '',
    );
  }

  Future<void> resetPassword({
    required String token,
    required String password,
    required String passwordConfirm,
  }) async {
    await apiClient.postJson('/api/auth/reset-password/', {
      'token': token,
      'password': password,
      'password_confirm': passwordConfirm,
    });
  }
}

class PasswordResetRequest {
  const PasswordResetRequest({
    required this.email,
    required this.token,
  });

  final String email;
  final String token;
}
