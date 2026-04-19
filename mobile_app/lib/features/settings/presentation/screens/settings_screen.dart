import 'package:flutter/material.dart';
import 'package:gradiuationg_project/core/widgets/custom_bottom_nav_bar.dart';
import '../../../../core/theme/app_colors.dart';
import '../widgets/logout_tile.dart';
import '../widgets/settings_item.dart';

class SettingsScreen extends StatefulWidget {
  const SettingsScreen({super.key});

  @override
  State<SettingsScreen> createState() => _SettingsScreenState();
}

class _SettingsScreenState extends State<SettingsScreen> {
  int currentIndex = 3;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.background,
      bottomNavigationBar: const CustomBottomNavBar(
  currentIndex: 3,
),
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: 16),
          child: Column(
            children: [
              const SizedBox(height: 18),
              const Center(
                child: Text(
                  'Settings',
                  style: TextStyle(
                    fontSize: 22,
                    fontWeight: FontWeight.w700,
                    color: Colors.black,
                  ),
                ),
              ),
              const SizedBox(height: 34),
              Expanded(
                child: Column(
                  children: [
                    SettingsItem(
                      icon: Icons.info,
                      title: 'Account Info',
                      onTap: () {},
                    ),
                    SettingsItem(
                      icon: Icons.key,
                      title: 'Change Password',
                      onTap: () {},
                    ),
                    SettingsItem(
                      icon: Icons.shield,
                      title: 'Privacy& Policy',
                      onTap: () {},
                    ),
                    SettingsItem(
                      icon: Icons.notifications,
                      title: 'Notifications',
                      trailingText: 'Enabled',
                      onTap: () {},
                    ),
                    SettingsItem(
                      title: 'About',
                      smallLeadingText: 'about.me',
                      onTap: () {},
                    ),
                    const SizedBox(height: 22),
                    LogoutTile(
                      onTap: () {},
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}