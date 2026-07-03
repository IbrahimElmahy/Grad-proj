import 'package:gradiuationg_project/core/constants/user_roles.dart';

class AppUser {
  const AppUser({
    required this.id,
    required this.username,
    required this.name,
    required this.email,
    required this.role,
    required this.airport,
    this.profilePicture,
  });

  final int id;
  final String username;
  final String name;
  final String email;
  final String role;
  final String airport;
  final String? profilePicture;

  factory AppUser.fromJson(Map<String, dynamic> json) {
    final roleString = json['role'] as String? ?? 'officer';
    final normalizedRole = UserPermissions.fromString(roleString).name.toLowerCase();

    return AppUser(
      id: json['id'] as int? ?? 0,
      username: json['username'] as String? ?? '',
      name: json['name'] as String? ?? 'RVMS User',
      email: json['email'] as String? ?? '',
      role: normalizedRole,
      airport: json['airport'] as String? ?? 'RVMS Operations',
      profilePicture: json['profile_picture'] as String?,
    );
  }

  AppUser copyWith({
    String? name,
    String? profilePicture,
  }) {
    return AppUser(
      id: id,
      username: username,
      name: name ?? this.name,
      email: email,
      role: role,
      airport: airport,
      profilePicture: profilePicture ?? this.profilePicture,
    );
  }
}
