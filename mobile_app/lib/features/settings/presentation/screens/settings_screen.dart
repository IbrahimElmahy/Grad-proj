import 'package:flutter/material.dart';
import 'package:gradiuationg_project/core/constants/constants.dart';
import 'package:gradiuationg_project/core/widgets/custom_bottom_nav_bar.dart';
import '../../../../core/theme/app_colors.dart';
import '../../../auth/data/auth_session.dart';
import '../widgets/logout_tile.dart';
import '../widgets/settings_item.dart';

class SettingsScreen extends StatefulWidget {
  const SettingsScreen({super.key});

  @override
  State<SettingsScreen> createState() => _SettingsScreenState();
}

class _SettingsScreenState extends State<SettingsScreen> {
  int currentIndex = 3;

  String _getInitials(String name) {
    if (name.trim().isEmpty) return 'US';
    final parts = name.trim().split(RegExp(r'\s+'));
    if (parts.length >= 2) {
      if (parts[0].isNotEmpty && parts[1].isNotEmpty) {
        return (parts[0][0] + parts[1][0]).toUpperCase();
      }
    }
    if (parts.isNotEmpty && parts[0].isNotEmpty) {
      return parts[0][0].toUpperCase();
    }
    return 'US';
  }

  @override
  Widget build(BuildContext context) {
    final user = AuthSession.user;
    final userName = user?.name ?? 'Safety Officer';
    final userEmail = user?.email ?? 'officer@rvms.com';
    final userRole = user?.role ?? 'Safety Officer';
    final initials = _getInitials(userName);

    return Scaffold(
      backgroundColor: AppColors.background,
      bottomNavigationBar: const CustomBottomNavBar(
        currentIndex: 3,
      ),
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 20),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              // Title
              const Center(
                child: Text(
                  'Settings',
                  style: TextStyle(
                    fontSize: 24,
                    fontWeight: FontWeight.w900,
                    color: AppColors.textDark,
                    letterSpacing: -0.5,
                  ),
                ),
              ),
              const SizedBox(height: 24),

              // Dynamic Profile Header Card
              Container(
                padding: const EdgeInsets.all(20),
                decoration: BoxDecoration(
                  gradient: LinearGradient(
                    colors: [
                      AppColors.primary,
                      AppColors.primary.withRed(30).withGreen(60),
                    ],
                    begin: Alignment.topLeft,
                    end: Alignment.bottomRight,
                  ),
                  borderRadius: BorderRadius.circular(20),
                  boxShadow: [
                    BoxShadow(
                      color: AppColors.primary.withOpacity(0.25),
                      blurRadius: 15,
                      offset: const Offset(0, 8),
                    ),
                  ],
                ),
                child: Row(
                  children: [
                    // Initials Avatar
                    Container(
                      width: 64,
                      height: 64,
                      decoration: const BoxDecoration(
                        color: Colors.white,
                        shape: BoxShape.circle,
                      ),
                      child: Center(
                        child: Text(
                          initials,
                          style: const TextStyle(
                            fontSize: 22,
                            fontWeight: FontWeight.w900,
                            color: AppColors.primary,
                          ),
                        ),
                      ),
                    ),
                    const SizedBox(width: 16),
                    // User Details
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            userName,
                            style: const TextStyle(
                              fontSize: 18,
                              fontWeight: FontWeight.bold,
                              color: Colors.white,
                            ),
                          ),
                          const SizedBox(height: 4),
                          Text(
                            userRole,
                            style: TextStyle(
                              fontSize: 13,
                              fontWeight: FontWeight.w500,
                              color: Colors.white.withOpacity(0.85),
                            ),
                          ),
                          const SizedBox(height: 2),
                          Text(
                            userEmail,
                            style: TextStyle(
                              fontSize: 12,
                              color: Colors.white.withOpacity(0.65),
                            ),
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 28),

              // Grouped Settings List Card
              Container(
                decoration: BoxDecoration(
                  color: Colors.white,
                  borderRadius: BorderRadius.circular(20),
                  border: Border.all(color: AppColors.border.withOpacity(0.5)),
                  boxShadow: [
                    BoxShadow(
                      color: Colors.black.withOpacity(0.02),
                      blurRadius: 10,
                      offset: const Offset(0, 4),
                    ),
                  ],
                ),
                child: Column(
                  children: [
                    SettingsItem(
                      icon: Icons.info_outline_rounded,
                      title: 'Account Info',
                      onTap: () => Navigator.pushNamed(context, AppRoutes.accountInfo),
                    ),
                    SettingsItem(
                      icon: Icons.key_rounded,
                      title: 'Change Password',
                      onTap: () => Navigator.pushNamed(context, AppRoutes.changePassword),
                    ),
                    SettingsItem(
                      icon: Icons.shield_outlined,
                      title: 'Privacy & Policy',
                      onTap: () => Navigator.pushNamed(context, AppRoutes.privacy),
                    ),
                    SettingsItem(
                      icon: Icons.notifications_none_rounded,
                      title: 'Notifications',
                      trailingText: 'Enabled',
                      onTap: () => Navigator.pushNamed(context, AppRoutes.notifications),
                    ),
                    SettingsItem(
                      icon: Icons.help_outline_rounded,
                      title: 'About',
                      onTap: () => Navigator.pushNamed(context, AppRoutes.about),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 24),

              // Logout Row
              LogoutTile(
                onTap: () {
                  AuthSession.clear();
                  Navigator.pushNamedAndRemoveUntil(
                    context,
                    AppRoutes.login,
                    (route) => false,
                  );
                },
              ),
              const SizedBox(height: 100), // Account for navigation bottom bar padding
            ],
          ),
        ),
      ),
    );
  }
}
