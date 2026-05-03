import 'package:flutter/material.dart';
import '../../../../core/theme/app_colors.dart';

class SystemHealthStatus extends StatelessWidget {
  const SystemHealthStatus({super.key});

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          'System Health Status',
          style: TextStyle(
            fontSize: 22,
            fontWeight: FontWeight.w800,
            color: Colors.black,
          ),
        ),
        const SizedBox(height: 18),
        Container(
          padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 12),
          decoration: BoxDecoration(
            color: Colors.white,
            borderRadius: BorderRadius.circular(14),
            boxShadow: [
              BoxShadow(
                color: Colors.black.withOpacity(0.18),
                blurRadius: 8,
                offset: const Offset(0, 5),
              ),
            ],
          ),
          child: const Column(
            children: [
              _HealthStatusItem(
                icon: Icons.memory_rounded,
                title: 'AI Engine: Running Smoothly.',
              ),
              SizedBox(height: 16),
              _HealthStatusItem(
                icon: Icons.camera_alt_rounded,
                title: 'CCTV Cameras: 12/12 Online.',
              ),
              SizedBox(height: 16),
              _HealthStatusItem(
                icon: Icons.storage_rounded,
                title: 'Database Servers: Synchronized.',
              ),
            ],
          ),
        ),
      ],
    );
  }
}

class _HealthStatusItem extends StatelessWidget {
  final IconData icon;
  final String title;

  const _HealthStatusItem({
    required this.icon,
    required this.title,
  });

  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        Icon(
          icon,
          size: 24,
          color: Colors.black.withOpacity(0.75),
        ),
        const SizedBox(width: 14),
        Expanded(
          child: Text(
            title,
            style: const TextStyle(
              fontSize: 16,
              fontWeight: FontWeight.w500,
              color: Color(0xff1E2433),
            ),
          ),
        ),
        Container(
          width: 18,
          height: 18,
          decoration: BoxDecoration(
            shape: BoxShape.circle,
            color: AppColors.safe,
            border: Border.all(
              color: Colors.green,
              width: 1.5,
            ),
          ),
        ),
      ],
    );
  }
}