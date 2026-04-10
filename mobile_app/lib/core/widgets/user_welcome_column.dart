import 'package:flutter/material.dart';
import '../theme/app_colors.dart';

class UserWelcomeColumn extends StatelessWidget {
  const UserWelcomeColumn({
    super.key,
    required this.userName,
    required this.userRole,
  });

  final String userName;
  final String userRole;

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'Hello, $userName',
          style: const TextStyle(
            fontSize: 24,
            fontWeight: FontWeight.w700,
            color: AppColors.textDark,
          ),
        ),
        const SizedBox(height: 2),
        Text(
          userRole,
          style: const TextStyle(
            fontSize: 15,
            color: AppColors.textGrey,
          ),
        ),
      ],
    );
  }
}