enum UserRole {
  controller,
  manager,
  officer,
}

class UserPermissions {
  static bool canAccessHome(UserRole role) {
    return true;
  }

  static bool canAccessAlerts(UserRole role) {
    return role == UserRole.officer || role == UserRole.manager || role == UserRole.controller;
  }

  static bool canAccessHistory(UserRole role) {
    return true;
  }

  static bool canAccessSettings(UserRole role) {
    return role == UserRole.officer || role == UserRole.controller;
  }

  static UserRole fromString(String value) {
    final val = value.toLowerCase();
    if (val.contains('controller')) {
      return UserRole.controller;
    }
    if (val.contains('manager')) {
      return UserRole.manager;
    }
    if (val.contains('officer')) {
      return UserRole.officer;
    }
    return UserRole.values.firstWhere(
      (role) => role.name.toLowerCase() == val,
      orElse: () => UserRole.officer,
    );
  }
}
