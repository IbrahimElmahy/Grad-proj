import 'package:flutter/material.dart';
import 'package:gradiuationg_project/core/widgets/custom_bottom_nav_bar.dart';

import '../../../../core/theme/app_colors.dart';
import '../../../inspections/data/inspection_service.dart';
import '../../data/models/alert_model.dart';
import '../widgets/alert_card.dart';

class AlertsScreen extends StatefulWidget {
  const AlertsScreen({super.key});

  @override
  State<AlertsScreen> createState() => _AlertsScreenState();
}

class _AlertsScreenState extends State<AlertsScreen> {
  final InspectionService _inspectionService = const InspectionService();
  late Future<List<AlertModel>> _alertsFuture;

  @override
  void initState() {
    super.initState();
    _alertsFuture = _loadAlerts();
  }

  Future<List<AlertModel>> _loadAlerts() async {
    final inspections = await _inspectionService.fetchInspections();
    return inspections.where((alert) => alert.severity != AlertSeverity.safe).toList();
  }

  Future<void> _refresh() async {
    final future = _loadAlerts();
    setState(() => _alertsFuture = future);
    try {
      await future;
    } catch (_) {
      return;
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.background,
      bottomNavigationBar: const CustomBottomNavBar(currentIndex: 2),
      body: SafeArea(
        child: RefreshIndicator(
          onRefresh: _refresh,
          child: FutureBuilder<List<AlertModel>>(
            future: _alertsFuture,
            builder: (context, snapshot) {
              final alerts = snapshot.data ?? const <AlertModel>[];
              return ListView.separated(
                physics: const AlwaysScrollableScrollPhysics(),
                padding: const EdgeInsets.fromLTRB(14, 18, 14, 110),
                itemCount: alerts.isEmpty ? 2 : alerts.length + 1,
                separatorBuilder: (_, __) => const SizedBox(height: 14),
                itemBuilder: (context, index) {
                  if (index == 0) {
                    return const Text(
                      'Alerts',
                      textAlign: TextAlign.center,
                      style: TextStyle(
                        fontSize: 22,
                        fontWeight: FontWeight.w800,
                        color: AppColors.textDark,
                      ),
                    );
                  }

                  if (snapshot.connectionState == ConnectionState.waiting && alerts.isEmpty) {
                    return const Center(child: CircularProgressIndicator());
                  }
                  if (snapshot.hasError) {
                    return _StateMessage(
                      icon: Icons.cloud_off_outlined,
                      title: 'Backend connection failed',
                      message: snapshot.error.toString(),
                    );
                  }
                  if (alerts.isEmpty) {
                    return const _StateMessage(
                      icon: Icons.verified_outlined,
                      title: 'No active alerts',
                      message: 'Medium and high risk inspections will appear here.',
                    );
                  }

                  return AlertCard(
                    alert: alerts[index - 1],
                    onTap: () {
                      Navigator.pushNamed(
                        context,
                        '/inspection-detail',
                        arguments: alerts[index - 1],
                      );
                    },
                  );
                },
              );
            },
          ),
        ),
      ),
    );
  }
}

class _StateMessage extends StatelessWidget {
  const _StateMessage({
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
