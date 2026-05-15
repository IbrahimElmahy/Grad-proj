class AppUser {
  const AppUser({
    required this.id,
    required this.username,
    required this.name,
    required this.email,
    required this.role,
    required this.airport,
  });

  final int id;
  final String username;
  final String name;
  final String email;
  final String role;
  final String airport;

  factory AppUser.fromJson(Map<String, dynamic> json) {
    return AppUser(
      id: json['id'] as int? ?? 0,
      username: json['username'] as String? ?? '',
      name: json['name'] as String? ?? 'RVMS User',
      email: json['email'] as String? ?? '',
      role: json['role'] as String? ?? 'Safety Officer',
      airport: json['airport'] as String? ?? 'RVMS Operations',
    );
  }
}
