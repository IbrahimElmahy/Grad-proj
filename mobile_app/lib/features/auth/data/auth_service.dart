import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:http_parser/http_parser.dart';
import '../../../core/network/api_client.dart';
import '../../../core/network/api_config.dart';
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

  Future<AppUser> updateProfile({
    required int userId,
    String? name,
    List<int>? imageBytes,
    String? imageName,
  }) async {
    final uri = ApiConfig.uri('/api/auth/update-profile/');
    final request = http.MultipartRequest('POST', uri);
    request.fields['user_id'] = userId.toString();
    if (name != null) {
      request.fields['name'] = name;
    }

    if (imageBytes != null && imageName != null) {
      final multipartFile = http.MultipartFile.fromBytes(
        'profile_picture',
        imageBytes,
        filename: imageName,
        contentType: MediaType(
          'image',
          imageName.split('.').last,
        ),
      );
      request.files.add(multipartFile);
    }

    final streamedResponse = await request.send();
    final response = await http.Response.fromStream(streamedResponse);

    if (response.statusCode >= 200 && response.statusCode < 300) {
      final decodedBody = jsonDecode(response.body);
      if (decodedBody is Map<String, dynamic>) {
        final user = AppUser.fromJson(decodedBody['user'] as Map<String, dynamic>);
        AuthSession.user = user;
        return user;
      }
      throw Exception('Invalid server response format.');
    } else {
      final decodedBody = jsonDecode(response.body);
      final error = decodedBody is Map ? (decodedBody['detail'] ?? decodedBody['error'] ?? 'Update failed.') : 'Update failed.';
      throw Exception(error);
    }
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
