import 'package:gradiuationg_project/core/constants/user_roles.dart';

class UserModel {
  final String name;
  final UserRole role;

  UserModel({required this.name, required this.role, });
  factory UserModel.fromJson(Map<String, dynamic> json) {
    return UserModel(
      name: json['name'] as String? ?? 'RVMS User',
      role: UserPermissions.fromString(json['role'] as String? ?? 'officer'),
    );
  }
}
