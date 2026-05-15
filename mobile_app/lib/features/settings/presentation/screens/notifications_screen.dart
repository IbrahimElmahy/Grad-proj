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
        title: const Text('Notifications'),
      ),
      body: FutureBuilder<DashboardStats>(
        future: _statsFuture,
        builder: (context, snapshot) {
          final stats = snapshot.data;
          return ListView(
            padding: const EdgeInsets.all(16),
            children: [
              _NotificationTile(
                icon: Icons.warning_amber_rounded,
                title: 'Alerts today',
                value: stats == null ? 'Loading...' : stats.alertsToday.toString(),
              ),
              _NotificationTile(
                icon: Icons.fact_check_outlined,
                title: 'Today checks',
                value: stats == null ? 'Loading...' : stats.todayInspections.toString(),
              ),
              _NotificationTile(
                icon: Icons.notifications_active_outlined,
                title: 'Live alert feed',
                value: 'Enabled',
              ),
              if (snapshot.hasError)
                Padding(
                  padding: const EdgeInsets.only(top: 14),
                  child: Text(
                    snapshot.error.toString(),
                    textAlign: TextAlign.center,
                    style: const TextStyle(color: AppColors.textGrey),
                  ),
                ),
            ],
          );
        },
      ),
    );
  }
}

class _NotificationTile extends StatelessWidget {
  const _NotificationTile({
    required this.icon,
    required this.title,
    required this.value,
  });

  final IconData icon;
  final String title;
  final String value;

  @override
  Widget build(BuildContext context) {
    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(14),
      ),
      child: Row(
        children: [
          Icon(icon, color: AppColors.primary, size: 28),
          const SizedBox(width: 14),
          Expanded(
            child: Text(
              title,
              style: const TextStyle(fontSize: 15, fontWeight: FontWeight.w800),
            ),
          ),
          Text(
            value,
            style: const TextStyle(fontWeight: FontWeight.w900, color: AppColors.primary),
          ),
        ],
      ),
    );
  }
}
