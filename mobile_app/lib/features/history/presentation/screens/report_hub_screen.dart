import 'package:flutter/material.dart';
import 'package:gradiuationg_project/core/widgets/custom_bottom_nav_bar.dart';
import 'package:gradiuationg_project/features/history/presentation/widgets/report_card.dart';
import 'package:gradiuationg_project/features/history/presentation/widgets/report_model.dart';

import '../../../../core/theme/app_colors.dart';

class ReportHubScreen extends StatefulWidget {
  const ReportHubScreen({super.key});

  @override
  State<ReportHubScreen> createState() => _ReportHubScreenState();
}

class _ReportHubScreenState extends State<ReportHubScreen> {
  int selectedCategoryIndex = 0;

  final List<String> categories = const [
    'All',
    'System',
    'Officer',
  ];

  final List<ReportModel> reports = const [
    ReportModel(
      title: 'Daily Scan - 29 Jan',
      createdBy: 'System (Auto)',
      date: '29-01-2026, 15:20 EET',
      type: ReportType.system,
    ),
    ReportModel(
      title: 'Bird Hazard Incident',
      createdBy: 'Officer Ali Mansour',
      date: '29-01-2026, 11:30 EET',
      type: ReportType.officer,
    ),
    ReportModel(
      title: 'Manual Rwy Inspection',
      createdBy: 'Officer Hany Galal',
      date: '28-01-2026, 23:50 EET',
      type: ReportType.officer,
    ),
    ReportModel(
      title: 'Weekly Summary',
      createdBy: 'System (Auto)',
      date: '29-01-2026, 15:20 EET',
      type: ReportType.system,
    ),
  ];

   List<ReportModel> filtereReports() {
    if (selectedCategoryIndex == 1) {
      return reports.where((report) => report.type == ReportType.system).toList();
    }

    if (selectedCategoryIndex == 2) {
      return reports.where((report) => report.type == ReportType.officer).toList();
    }

    return reports;
  }

  @override
  Widget build(BuildContext context) {
    List<ReportModel> filteredReports=filtereReports();
    return Scaffold(
      backgroundColor: AppColors.background,
      bottomNavigationBar: const CustomBottomNavBar(currentIndex: 1),
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: 14),
          child: Column(
            children: [
              const SizedBox(height: 34),
              const Text(
                'Report Hub',
                style: TextStyle(
                  fontSize: 26,
                  fontWeight: FontWeight.w800,
                  color: Color(0xff071225),
                ),
              ),
              const SizedBox(height: 44),
              const SizedBox(height: 34),
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceAround,
                children: List.generate(
                  categories.length,
                  (index) {
                    final bool isSelected = selectedCategoryIndex == index;

                    return GestureDetector(
                      onTap: () {
                        setState(() {
                          selectedCategoryIndex = index;
                        });
                      },
                      child: Text(
                        categories[index],
                        style: TextStyle(
                          fontSize: 15,
                          fontWeight:
                              isSelected ? FontWeight.w800 : FontWeight.w500,
                          color: Colors.black,
                        ),
                      ),
                    );
                  },
                ),
              ),
              const SizedBox(height: 28),
              Expanded(
                child: ListView.separated(
                  physics: const BouncingScrollPhysics(),
                  itemCount: filteredReports.length,
                  separatorBuilder: (context, index) =>
                      const SizedBox(height: 22),
                  itemBuilder: (context, index) {
                    return ReportCard(report: filteredReports[index]);
                  },
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}







