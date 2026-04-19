import 'package:flutter/material.dart';
import 'package:gradiuationg_project/core/widgets/custom_bottom_nav_bar.dart';
import '../../../../core/theme/app_colors.dart';
import '../../../../core/widgets/user_avatar.dart';
import '../../../../core/widgets/user_welcome_column.dart';
import '../../../alerts/data/models/alert_model.dart';
import '../../../alerts/presentation/widgets/alert_card.dart';
import '../widgets/draggable_check_bar.dart';
import '../widgets/home_stats_section.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {

  final List<AlertModel> alerts = const [
    AlertModel(
      runwayTitle: 'RWY 30R',
      date: '20/12/2025',
      time: '05:22 PM',
      statusText: 'Safe',
      imagePath: 'assets/images/background_image.png',
      severity: AlertSeverity.safe,
    ),
    AlertModel(
      runwayTitle: 'RWY 09L \\ 27R',
      date: '20/12/2025',
      time: '05:01 PM',
      statusText: 'High Risk',
      imagePath: 'assets/images/onboarding_background.jpeg',
      severity: AlertSeverity.highRisk,
    ),
  ];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.background,
      bottomNavigationBar: const CustomBottomNavBar(
  currentIndex: 0,
),
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: 14),
          child: SingleChildScrollView(
            child: Column(
              children: [
                const SizedBox(height: 12),
                const Row(
                  children: [
                    UserAvatar(imagePath: 'assets/images/user_image.jpg'),
                    SizedBox(width: 10),
                    Expanded(
                      child: UserWelcomeColumn(
                        userName: 'Ali',
                        userRole: 'Safety Officer',
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 20),
                const HomeStatsSection(),
                const SizedBox(height: 18),
                DraggableCheckBar(
                  onCompleted: () {
                    ScaffoldMessenger.of(context).showSnackBar(
                      const SnackBar(content: Text('New check started')),
                    );
                  },
                ),
                const SizedBox(height: 16),
                ListView.separated(
                  itemCount: alerts.length,
                  shrinkWrap: true,
                  physics: const NeverScrollableScrollPhysics(),
                  separatorBuilder: (_, __) => const SizedBox(height: 14),
                  itemBuilder: (context, index) {
                    return AlertCard(
                      alert: alerts[index],
                      onTap: () {},
                    );
                  },
                ),
                const SizedBox(height: 100),
              ],
            ),
          ),
        ),
      ),
    );
  }
}