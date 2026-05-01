import 'package:flutter/material.dart';
import '../../../../core/constants/constants.dart';
import '../../../../core/theme/app_colors.dart';

class CustomBottomNavBar extends StatelessWidget {
  final int currentIndex;

  const CustomBottomNavBar({super.key, required this.currentIndex});

  void _navigate(BuildContext context, int index) {
    if (index == currentIndex) return;

    switch (index) {
      case 0:
        Navigator.pushReplacementNamed(context, AppRoutes.home);
        break;
      // case 1:
      //   Navigator.pushReplacementNamed(context, AppRoutes.history);
      //   break;
      // case 2:
      //   Navigator.pushReplacementNamed(context, AppRoutes.alerts);
      //   break;
      case 3:
        Navigator.pushReplacementNamed(context, AppRoutes.settings);
        break;
    }
  }

  @override
  Widget build(BuildContext context) {
    final List<IconData> items = const[
      Icons.home_filled,
      Icons.history,
      Icons.warning_amber_rounded,
      Icons.settings,
    ];

    return Container(
      margin: const EdgeInsets.only(left: 16, right: 16, bottom: 16),
      padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 14),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(22),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(.06),
            blurRadius: 20,
            offset: const Offset(0, 8),
          ),
        ],
      ),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: List.generate(
          items.length,
          (index) => GestureDetector(
            onTap: () => _navigate(context, index),
            child: Icon(
              items[index],
              size: 24,
              color: currentIndex == index
                  ? AppColors.primary
                  : AppColors.primary.withOpacity(.35),
            ),
          ),
        ),
      ),
    );
  }
}
