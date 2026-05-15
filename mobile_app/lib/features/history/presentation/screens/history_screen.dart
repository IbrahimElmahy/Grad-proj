import 'package:flutter/material.dart';
import 'package:gradiuationg_project/core/widgets/custom_bottom_nav_bar.dart';

import '../../../../core/theme/app_colors.dart';
import '../../../alerts/data/models/alert_model.dart';
import '../../../alerts/presentation/widgets/alert_card.dart';
import '../../../inspections/data/inspection_service.dart';

class HistoryScreen extends StatefulWidget {
  const HistoryScreen({super.key});

  @override
  State<HistoryScreen> createState() => _HistoryScreenState();
}

class _HistoryScreenState extends State<HistoryScreen> {
  final InspectionService _inspectionService = const InspectionService();

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.background,
      bottomNavigationBar: const CustomBottomNavBar(currentIndex: 1),
      body: SafeArea(
        child: FutureBuilder<List<AlertModel>>(
          future: _inspectionService.fetchInspections(),
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
                    'History',
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
                  return Text(
                    snapshot.error.toString(),
                    textAlign: TextAlign.center,
                    style: const TextStyle(color: AppColors.textGrey),
                  );
                }
                if (alerts.isEmpty) {
                  return const Text(
                    'No inspection history yet.',
                    textAlign: TextAlign.center,
                    style: TextStyle(color: AppColors.textGrey),
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
    );
  }
}
