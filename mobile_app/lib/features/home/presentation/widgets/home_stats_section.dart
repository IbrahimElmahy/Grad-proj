import 'package:flutter/material.dart';
import 'home_stat_card.dart';

class HomeStatsSection extends StatelessWidget {
  const HomeStatsSection({super.key});

  @override
  Widget build(BuildContext context) {
    return const Row(
      children: [
        Expanded(
          child: HomeStatCard(
            title: "Today's Checks",
            value: '3',
            icon: Icons.fact_check_outlined,
          ),
        ),
        SizedBox(width: 10),
        Expanded(
          child: HomeStatCard(
            title: 'Last status',
            value: 'Safe',
            icon: Icons.hub_outlined,
          ),
        ),
        SizedBox(width: 10),
        Expanded(
          child: HomeStatCard(
            title: 'Next Check',
            value: 'Today 05:45 pm',
            icon: Icons.copy_all_outlined,
          ),
        ),
      ],
    );
  }
}