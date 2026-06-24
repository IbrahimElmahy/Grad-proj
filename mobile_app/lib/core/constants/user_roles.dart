enum UserRole {
  admin,
  officer,
  manager,
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
}