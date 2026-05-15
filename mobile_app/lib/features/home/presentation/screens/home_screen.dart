import 'package:flutter/material.dart';
import 'package:gradiuationg_project/core/widgets/custom_bottom_nav_bar.dart';
import '../../../../core/theme/app_colors.dart';
import '../../../../core/widgets/user_avatar.dart';
import '../../../../core/widgets/user_welcome_column.dart';
import '../../../auth/data/auth_session.dart';
import '../../../alerts/data/models/alert_model.dart';
import '../../../alerts/presentation/widgets/alert_card.dart';
import '../../../inspections/data/inspection_service.dart';
import '../widgets/draggable_check_bar.dart';
import '../widgets/home_stats_section.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  final InspectionService _inspectionService = const InspectionService();
  late Future<List<AlertModel>> _alertsFuture;

  @override
  void initState() {
    super.initState();
    _alertsFuture = _inspectionService.fetchInspections();
  }

  Future<void> _refreshAlerts() async {
    final future = _inspectionService.fetchInspections();
    setState(() {
      _alertsFuture = future;
    });
    try {
      await future;
    } catch (_) {
      return;
    }
  }

  int _countTodaysChecks(List<AlertModel> alerts) {
    final now = DateTime.now();
    final today = '${now.day.toString().padLeft(2, '0')}/${now.month.toString().padLeft(2, '0')}/${now.year}';
    return alerts.where((alert) => alert.date == today).length;
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.background,
      bottomNavigationBar: const CustomBottomNavBar(
  currentIndex: 0,
),
      body: SafeArea(
        child: RefreshIndicator(
          onRefresh: _refreshAlerts,
          child: FutureBuilder<List<AlertModel>>(
            future: _alertsFuture,
            builder: (context, snapshot) {
              final alerts = snapshot.data ?? const <AlertModel>[];
              final user = AuthSession.user;

              return SingleChildScrollView(
                physics: const AlwaysScrollableScrollPhysics(),
                padding: const EdgeInsets.symmetric(horizontal: 14),
                child: Column(
                  children: [
                    const SizedBox(height: 12),
                    Row(
                      children: [
                        const UserAvatar(imagePath: 'assets/images/user_image.jpg'),
                        const SizedBox(width: 10),
                        Expanded(
                          child: UserWelcomeColumn(
                            userName: user?.name ?? 'RVMS User',
                            userRole: user?.role ?? 'Safety Officer',
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 20),
                    HomeStatsSection(
                      todaysChecks: _countTodaysChecks(alerts),
                      lastStatus: alerts.isEmpty ? 'No data' : alerts.first.statusText,
                      nextCheck: 'On demand',
                    ),
                    const SizedBox(height: 18),
                    DraggableCheckBar(
                      onCompleted: () {
                        ScaffoldMessenger.of(context).showSnackBar(
                          const SnackBar(
                            content: Text('Use the upload endpoint to start a new AI inspection.'),
                          ),
                        );
                      },
                    ),
                    const SizedBox(height: 16),
                    if (snapshot.connectionState == ConnectionState.waiting && alerts.isEmpty)
                      const Padding(
                        padding: EdgeInsets.only(top: 40),
                        child: CircularProgressIndicator(),
                      )
                    else if (snapshot.hasError)
                      _HomeMessage(
                        icon: Icons.cloud_off_outlined,
                        title: 'Backend connection failed',
                        message: snapshot.error.toString(),
                      )
                    else if (alerts.isEmpty)
                      const _HomeMessage(
                        icon: Icons.fact_check_outlined,
                        title: 'No inspections yet',
                        message: 'Inspection history will appear here after the backend receives uploads.',
                      )
                    else
                      ListView.separated(
                        itemCount: alerts.length,
                        shrinkWrap: true,
                        physics: const NeverScrollableScrollPhysics(),
                        separatorBuilder: (_, __) => const SizedBox(height: 14),
                        itemBuilder: (context, index) {
                          return AlertCard(
                            alert: alerts[index],
                            onTap: () {
                              Navigator.pushNamed(
                                context,
                                '/inspection-detail',
                                arguments: alerts[index],
                              );
                            },
                          );
                        },
                      ),
                    const SizedBox(height: 100),
                  ],
                ),
              );
            },
          ),
        ),
      ),
    );
  }
}

class _HomeMessage extends StatelessWidget {
  const _HomeMessage({
    required this.icon,
    required this.title,
    required this.message,
  });

  final IconData icon;
  final String title;
  final String message;

  @override
  Widget build(BuildContext context) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(18),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(14),
      ),
      child: Column(
        children: [
          Icon(icon, color: AppColors.primary, size: 34),
          const SizedBox(height: 10),
          Text(
            title,
            textAlign: TextAlign.center,
            style: const TextStyle(
              fontSize: 16,
              fontWeight: FontWeight.w800,
              color: AppColors.textDark,
            ),
          ),
          const SizedBox(height: 6),
          Text(
            message,
            textAlign: TextAlign.center,
            style: const TextStyle(
              fontSize: 13,
              color: AppColors.textGrey,
              height: 1.4,
            ),
          ),
        ],
      ),
    );
  }
}
