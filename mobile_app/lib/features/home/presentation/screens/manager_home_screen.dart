import 'package:flutter/material.dart';
import 'package:gradiuationg_project/core/widgets/custom_bottom_nav_bar.dart';
import 'package:gradiuationg_project/features/home/presentation/widgets/active_officers_section.dart';

import '../../../../core/theme/app_colors.dart';
import '../../../../core/widgets/user_avatar.dart';
import '../../../../core/widgets/user_welcome_column.dart';
import '../widgets/home_stats_section.dart';
import '../widgets/system_health_status.dart';

class ManagerHomeScreen extends StatelessWidget {
  const ManagerHomeScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.background,
      bottomNavigationBar: const CustomBottomNavBar(currentIndex: 0),
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: 14),
          child: SingleChildScrollView(
            physics: const BouncingScrollPhysics(),
            child: Column(
              children: const [
                SizedBox(height: 12),
                Row(
                  children: [
                    UserAvatar(imagePath: 'assets/images/user_image.jpg'),
                    SizedBox(width: 10),
                    UserWelcomeColumn(
                      userName: 'Ramy',
                      userRole: 'Safety Manager',
                    ),
                  ],
                ),
                SizedBox(height: 20),
                HomeStatsSection(
                  todaysChecks: 5,
                  lastStatus: 'Healthy',
                  nextCheck: '10:00 AM',
                ),
                SizedBox(height: 36),
                SystemHealthStatus(),
                SizedBox(height: 50),
                SizedBox(height: 36),
                ActiveOfficersSection(),
                SizedBox(height: 50),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
