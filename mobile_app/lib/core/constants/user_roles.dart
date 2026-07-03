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
    final val = value.toLowerCase();
    if (val.contains('manager')) {
      return UserRole.manager;
    }
    if (val.contains('officer')) {
      return UserRole.officer;
    }
    if (val.contains('ground')) {
      return UserRole.ground;
    }
    return UserRole.values.firstWhere(
      (role) => role.name.toLowerCase() == val,
      orElse: () => UserRole.officer,
    );
  }
}
