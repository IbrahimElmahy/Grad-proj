import 'package:flutter/material.dart';
import '../../../../core/theme/app_colors.dart';
import '../../data/models/alert_model.dart';

class AlertCard extends StatelessWidget {
  const AlertCard({super.key, required this.alert, this.onTap});

  final AlertModel alert;
  final VoidCallback? onTap;

  Color _statusColor(AlertSeverity severity) {
    switch (severity) {
      case AlertSeverity.safe:
        return AppColors.safe;
      case AlertSeverity.medium:
        return AppColors.medium;
      case AlertSeverity.highRisk:
        return AppColors.highRisk;
    }
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.fromLTRB(8, 8, 8, 12),
      decoration: BoxDecoration(
        color: AppColors.softCard,
        borderRadius: BorderRadius.circular(14),
      ),
      child: Column(
        children: [
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 4),
            child: Row(
              children: [
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        alert.runwayTitle,
                        style: const TextStyle(
                          fontSize: 18,
                          fontWeight: FontWeight.w800,
                          color: AppColors.textDark,
                        ),
                      ),
                      const SizedBox(height: 2),
                      Text(
                        '${alert.date}   ${alert.time}',
                        style: const TextStyle(
                          fontSize: 13,
                          color: AppColors.textDark,
                        ),
                      ),
                    ],
                  ),
                ),
                InkWell(
                  onTap: onTap,
                  borderRadius: BorderRadius.circular(50),
                  child: Container(
                    width: 42,
                    height: 42,
                    decoration: const BoxDecoration(
                      color: AppColors.primary,
                      shape: BoxShape.circle,
                    ),
                    child: const Icon(Icons.arrow_forward, color: Colors.white),
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(height: 8),
          Stack(
            children: [
              ClipRRect(
                borderRadius: BorderRadius.circular(8),
                child: Image.asset(
                  alert.imagePath,
                  width: double.infinity,
                  height: 180,
                  fit: BoxFit.cover,
                  errorBuilder: (context, error, stackTrace) {
                    return Container(
                      width: double.infinity,
                      height: 180,
                      color: Colors.grey.shade200,
                      child: Center(
                        child: Icon(
                          Icons.broken_image,
                          color: Colors.grey.shade600,
                          size: 40,
                        ),
                      ),
                    );
                  },
                ),
              ),
              Positioned(
                top: 10,
                left: 12,
                child: Container(
                  padding: const EdgeInsets.symmetric(
                    horizontal: 18,
                    vertical: 8,
                  ),
                  decoration: BoxDecoration(
                    color: _statusColor(alert.severity),
                    borderRadius: BorderRadius.circular(30),
                  ),
                  child: Text(
                    alert.statusText,
                    style: const TextStyle(
                      fontSize: 16,
                      fontWeight: FontWeight.w700,
                      color: Colors.black,
                    ),
                  ),
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }
}
