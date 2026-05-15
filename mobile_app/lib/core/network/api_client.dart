import 'dart:convert';

import 'package:http/http.dart' as http;

import 'api_config.dart';

class ApiException implements Exception {
  ApiException(this.message, {this.statusCode});

  final String message;
  final int? statusCode;

  @override
  String toString() => message;
}

class ApiClient {
  const ApiClient({http.Client? client}) : _client = client;

  final http.Client? _client;

  http.Client get _http => _client ?? http.Client();

  Future<dynamic> get(String path) async {
    final response = await _http.get(ApiConfig.uri(path));
    return _decode(response);
  }

  Future<dynamic> postJson(String path, Map<String, dynamic> body) async {
    final response = await _http.post(
      ApiConfig.uri(path),
      headers: const {'Content-Type': 'application/json'},
      body: jsonEncode(body),
    );
    return _decode(response);
  }

  dynamic _decode(http.Response response) {
    final body = response.body.isEmpty ? null : _tryDecodeJson(response.body);
    if (response.statusCode >= 200 && response.statusCode < 300) {
      return body;
    }

    var message = 'Request failed. Please try again.';
    if (body is Map<String, dynamic>) {
      final serverMessage = body['detail'] ?? body['error'] ?? body['message'];
      if (serverMessage != null) {
        message = serverMessage.toString();
      } else if (body.isNotEmpty) {
        final firstValue = body.values.first;
        message = firstValue is List && firstValue.isNotEmpty
            ? firstValue.first.toString()
            : firstValue.toString();
      }
    }

    throw ApiException(message, statusCode: response.statusCode);
  }

  dynamic _tryDecodeJson(String body) {
    try {
      return jsonDecode(body);
    } catch (_) {
      return body;
    }
  }
}
