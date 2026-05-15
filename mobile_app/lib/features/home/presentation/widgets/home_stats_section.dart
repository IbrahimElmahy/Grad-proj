import 'package:flutter/material.dart';
import 'home_stat_card.dart';

class HomeStatsSection extends StatelessWidget {
  const HomeStatsSection({
    super.key,
    required this.todaysChecks,
    required this.lastStatus,
    required this.nextCheck,
  });

  final int todaysChecks;
  final String lastStatus;
  final String nextCheck;

  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        Expanded(
          child: HomeStatCard(
            title: "Today's Checks",
            value: todaysChecks.toString(),
            icon: Icons.fact_check_outlined,
          ),
        ),
        const SizedBox(width: 10),
        Expanded(
          child: HomeStatCard(
            title: 'Last status',
            value: lastStatus,
            icon: Icons.hub_outlined,
          ),
        ),
        const SizedBox(width: 10),
        Expanded(
          child: HomeStatCard(
            title: 'Next Check',
            value: nextCheck,
            icon: Icons.copy_all_outlined,
          ),
        ),
      ],
    );
  }
}
