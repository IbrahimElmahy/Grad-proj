import 'package:flutter/material.dart';

import '../../../../core/theme/app_colors.dart';
import '../../../inspections/data/inspection_service.dart';
import '../../../inspections/data/models/inspection_model.dart';

class NotificationsScreen extends StatefulWidget {
  const NotificationsScreen({super.key});

  @override
  State<NotificationsScreen> createState() => _NotificationsScreenState();
}

class _NotificationsScreenState extends State<NotificationsScreen> {
  final InspectionService _inspectionService = const InspectionService();
  late Future<DashboardStats> _statsFuture;

  // Interactive Switch States
  bool _pushNotifications = true;
  bool _criticalRiskOnly = false;
  bool _audioAlerts = true;

  @override
  void initState() {
    super.initState();
    _statsFuture = _inspectionService.fetchDashboardStats();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: AppBar(
        backgroundColor: AppColors.primary,
        elevation: 0,
        title: const Text(
          'Notifications & Stats',
          style: TextStyle(fontWeight: FontWeight.bold, fontSize: 19),
        ),
      ),
      body: FutureBuilder<DashboardStats>(
        future: _statsFuture,
        builder: (context, snapshot) {
          final stats = snapshot.data;

          return SingleChildScrollView(
            padding: const EdgeInsets.all(20),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                // Section Title: Daily Activity
                const Text(
                  'Daily Pipeline Stats',
                  style: TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.bold,
                    color: AppColors.textDark,
                  ),
                ),
                const SizedBox(height: 12),

                // Stats Panel
                Container(
                  padding: const EdgeInsets.all(16),
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
                  child: Row(
                    children: [
                      Expanded(
                        child: _StatCard(
                          icon: Icons.warning_amber_rounded,
                          iconColor: Colors.amber.shade600,
                          title: 'Alerts Today',
                          value: stats == null ? '...' : stats.alertsToday.toString(),
                        ),
                      ),
                      Container(
                        width: 1,
                        height: 60,
                        color: AppColors.border.withOpacity(0.5),
                      ),
                      Expanded(
                        child: _StatCard(
                          icon: Icons.fact_check_outlined,
                          iconColor: AppColors.primary,
                          title: 'Inspections',
                          value: stats == null ? '...' : stats.todayInspections.toString(),
                        ),
                      ),
                    ],
                  ),
                ),
                const SizedBox(height: 28),

                // Section Title: Settings
                const Text(
                  'Notification Preferences',
                  style: TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.bold,
                    color: AppColors.textDark,
                  ),
                ),
                const SizedBox(height: 12),

                // Grouped Settings Card
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
                      _ToggleRow(
                        icon: Icons.notifications_active_outlined,
                        title: 'Receive Push Alerts',
                        description: 'Notify immediately when runway scan completes',
                        value: _pushNotifications,
                        onChanged: (val) {
                          setState(() {
                            _pushNotifications = val;
                          });
                        },
                      ),
                      const Divider(height: 1, color: AppColors.background),
                      _ToggleRow(
                        icon: Icons.gpp_maybe_outlined,
                        title: 'Critical Risk Only',
                        description: 'Only notify for high severity alerts',
                        value: _criticalRiskOnly,
                        onChanged: (val) {
                          setState(() {
                            _criticalRiskOnly = val;
                          });
                        },
                      ),
                      const Divider(height: 1, color: AppColors.background),
                      _ToggleRow(
                        icon: Icons.volume_up_outlined,
                        title: 'System Audio Alerts',
                        description: 'Play alarms for critical events',
                        value: _audioAlerts,
                        onChanged: (val) {
                          setState(() {
                            _audioAlerts = val;
                          });
                        },
                      ),
                    ],
                  ),
                ),

                if (snapshot.hasError) ...[
                  const SizedBox(height: 20),
                  Text(
                    'Stats Sync Error: ${snapshot.error}',
                    textAlign: TextAlign.center,
                    style: const TextStyle(color: AppColors.textGrey, fontSize: 12),
                  ),
                ],
              ],
            ),
          );
        },
      ),
    );
  }
}

class _StatCard extends StatelessWidget {
  const _StatCard({
    required this.icon,
    required this.iconColor,
    required this.title,
    required this.value,
  });

  final IconData icon;
  final Color iconColor;
  final String title;
  final String value;

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        Icon(icon, color: iconColor, size: 28),
        const SizedBox(height: 8),
        Text(
          title,
          style: const TextStyle(
            fontSize: 12,
            fontWeight: FontWeight.w600,
            color: AppColors.textGrey,
          ),
        ),
        const SizedBox(height: 4),
        Text(
          value,
          style: const TextStyle(
            fontSize: 22,
            fontWeight: FontWeight.w900,
            color: AppColors.textDark,
          ),
        ),
      ],
    );
  }
}

class _ToggleRow extends StatelessWidget {
  const _ToggleRow({
    required this.icon,
    required this.title,
    required this.description,
    required this.value,
    required this.onChanged,
  });

  final IconData icon;
  final String title;
  final String description;
  final bool value;
  final ValueChanged<bool> onChanged;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
      child: Row(
        children: [
          Container(
            padding: const EdgeInsets.all(8),
            decoration: BoxDecoration(
              color: AppColors.background,
              borderRadius: BorderRadius.circular(10),
            ),
            child: Icon(icon, color: AppColors.primary, size: 22),
          ),
          const SizedBox(width: 14),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  title,
                  style: const TextStyle(
                    fontSize: 14,
                    fontWeight: FontWeight.w800,
                    color: AppColors.textDark,
                  ),
                ),
                const SizedBox(height: 2),
                Text(
                  description,
                  style: const TextStyle(
                    fontSize: 11,
                    color: AppColors.textGrey,
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(width: 8),
          Switch.adaptive(
            value: value,
            activeColor: AppColors.primary,
            onChanged: onChanged,
          ),
        ],
      ),
    );
  }
}
