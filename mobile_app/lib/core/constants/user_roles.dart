enum UserRole {
  manager,
  ground,
  officer,
}

class UserPermissions {
  static bool canAccessHome(UserRole role) {
    return true;
  }

  static bool canAccessAlerts(UserRole role) {
    return role == UserRole.officer || role == UserRole.manager;
  }

  static bool canAccessHistory(UserRole role) {
    return true;
  }

  static bool canAccessSettings(UserRole role) {
    return role == UserRole.officer;
  }

  static UserRole fromString(String value) {
    return UserRole.values.firstWhere(
      (role) => role.name.toLowerCase() == value.toLowerCase(),
      orElse: () => UserRole.officer,
    );
  }
}
