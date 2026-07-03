import 'package:flutter/material.dart';

import '../../../../core/theme/app_colors.dart';
import '../../../alerts/data/models/alert_model.dart';
import '../../data/inspection_service.dart';
import '../../data/models/inspection_model.dart';

class InspectionDetailScreen extends StatefulWidget {
  const InspectionDetailScreen({super.key});

  @override
  State<InspectionDetailScreen> createState() => _InspectionDetailScreenState();
}

class _InspectionDetailScreenState extends State<InspectionDetailScreen> {
  final InspectionService _inspectionService = const InspectionService();
  Future<InspectionModel>? _inspectionFuture;

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    _inspectionFuture ??= _buildFuture();
  }

  Future<InspectionModel> _buildFuture() {
    final args = ModalRoute.of(context)?.settings.arguments;
    if (args is InspectionModel) return Future.value(args);
    if (args is AlertModel && args.id.isNotEmpty) {
      return _inspectionService.fetchInspectionDetail(args.id);
    }
    if (args is String && args.isNotEmpty) {
      return _inspectionService.fetchInspectionDetail(args);
    }
    throw Exception('Inspection id is missing.');
  }

  Color _statusColor(AlertSeverity severity) {
    switch (severity) {
      case AlertSeverity.safe:
        return AppColors.safe;
      case AlertSeverity.low:
      case AlertSeverity.medium:
        return AppColors.warning;
      case AlertSeverity.highRisk:
        return AppColors.critical;
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: AppBar(
        backgroundColor: AppColors.primary,
        title: const Text('Inspection Detail'),
      ),
      body: FutureBuilder<InspectionModel>(
        future: _inspectionFuture,
        builder: (context, snapshot) {
          if (snapshot.connectionState == ConnectionState.waiting) {
            return const Center(child: CircularProgressIndicator());
          }
          if (snapshot.hasError) {
            return _MessagePanel(
              icon: Icons.cloud_off_outlined,
              title: 'Could not load inspection',
              message: snapshot.error.toString(),
            );
          }

          final inspection = snapshot.data!;
          return ListView(
            padding: const EdgeInsets.fromLTRB(14, 14, 14, 28),
            children: [
              _HeroImage(inspection: inspection),
              const SizedBox(height: 14),
              Container(
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: Colors.white,
                  borderRadius: BorderRadius.circular(14),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        Expanded(
                          child: Text(
                            inspection.cameraId,
                            style: const TextStyle(
                              fontSize: 20,
                              fontWeight: FontWeight.w900,
                              color: AppColors.textDark,
                            ),
                          ),
                        ),
                        Container(
                          padding: const EdgeInsets.symmetric(
                              horizontal: 12, vertical: 7),
                          decoration: BoxDecoration(
                            color: _statusColor(inspection.severity),
                            borderRadius: BorderRadius.circular(20),
                          ),
                          child: Text(
                            inspection.statusLabel,
                            style: const TextStyle(
                              fontSize: 12,
                              fontWeight: FontWeight.w800,
                              color: Colors.black,
                            ),
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 12),
                    _InfoRow(label: 'Date', value: inspection.date),
                    _InfoRow(label: 'Time', value: inspection.time),
                    _InfoRow(label: 'Status', value: inspection.status),
                    _InfoRow(label: 'Risk level', value: inspection.riskLevel),
                    _InfoRow(
                        label: 'Detections',
                        value: inspection.detectionCount.toString()),
                    _InfoRow(
                        label: 'Hazards',
                        value: inspection.hazardCount.toString()),
                  ],
                ),
              ),
              const SizedBox(height: 14),
              _DetectionsList(detections: inspection.detections),
            ],
          );
        },
      ),
    );
  }
}

class _HeroImage extends StatelessWidget {
  const _HeroImage({required this.inspection});

  final InspectionModel inspection;

  @override
  Widget build(BuildContext context) {
    final imageUrl = inspection.imageUrl;
    return ClipRRect(
      borderRadius: BorderRadius.circular(14),
      child: imageUrl.isEmpty
          ? const _ImagePlaceholder()
          : Image.network(
              imageUrl,
              height: 230,
              width: double.infinity,
              fit: BoxFit.cover,
              errorBuilder: (_, __, ___) => const _ImagePlaceholder(),
            ),
    );
  }
}

class _DetectionsList extends StatelessWidget {
  const _DetectionsList({required this.detections});

  final List<DetectedObjectModel> detections;

  @override
  Widget build(BuildContext context) {
    if (detections.isEmpty) {
      return const _MessagePanel(
        icon: Icons.verified_outlined,
        title: 'No objects detected',
        message: 'The backend did not store detections for this inspection.',
      );
    }

    return Container(
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(14),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            'Detected Objects',
            style: TextStyle(
              fontSize: 17,
              fontWeight: FontWeight.w900,
              color: AppColors.textDark,
            ),
          ),
          const SizedBox(height: 10),
          ...detections.map((item) => _DetectionTile(item: item)),
        ],
      ),
    );
  }
}

class _DetectionTile extends StatelessWidget {
  const _DetectionTile({required this.item});

  final DetectedObjectModel item;

  @override
  Widget build(BuildContext context) {
    return Container(
      margin: const EdgeInsets.only(bottom: 10),
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: AppColors.background,
        borderRadius: BorderRadius.circular(10),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Expanded(
                child: Text(
                  item.displayLabel,
                  style: const TextStyle(
                    fontSize: 15,
                    fontWeight: FontWeight.w800,
                    color: AppColors.textDark,
                  ),
                ),
              ),
              Text(
                item.confidencePercent,
                style: const TextStyle(
                  fontSize: 12,
                  fontWeight: FontWeight.w800,
                  color: AppColors.primary,
                ),
              ),
            ],
          ),
          const SizedBox(height: 6),
          Text(
            '${item.severity} • frame ${item.frameIndex}',
            style: const TextStyle(fontSize: 12, color: AppColors.textGrey),
          ),
          if (item.geminiSuggestion.trim().isNotEmpty) ...[
            const SizedBox(height: 8),
            Text(
              item.geminiSuggestion,
              style: const TextStyle(
                  fontSize: 12, color: AppColors.textDark, height: 1.35),
            ),
          ],
        ],
      ),
    );
  }
}

class _InfoRow extends StatelessWidget {
  const _InfoRow({required this.label, required this.value});

  final String label;
  final String value;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 5),
      child: Row(
        children: [
          SizedBox(
            width: 92,
            child: Text(
              label,
              style: const TextStyle(fontSize: 13, color: AppColors.textGrey),
            ),
          ),
          Expanded(
            child: Text(
              value,
              style: const TextStyle(
                fontSize: 13,
                fontWeight: FontWeight.w800,
                color: AppColors.textDark,
              ),
            ),
          ),
        ],
      ),
    );
  }
}

class _ImagePlaceholder extends StatelessWidget {
  const _ImagePlaceholder();

  @override
  Widget build(BuildContext context) {
    return Container(
      height: 230,
      color: Colors.grey.shade200,
      child: Center(
        child: Icon(Icons.image_not_supported_outlined,
            color: Colors.grey.shade600, size: 42),
      ),
    );
  }
}

class _MessagePanel extends StatelessWidget {
  const _MessagePanel({
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
      width: double.infinity,
      padding: const EdgeInsets.all(18),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(14),
      ),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(icon, color: AppColors.primary, size: 34),
          const SizedBox(height: 10),
          Text(
            title,
            textAlign: TextAlign.center,
            style: const TextStyle(fontSize: 16, fontWeight: FontWeight.w800),
          ),
          const SizedBox(height: 6),
          Text(
            message,
            textAlign: TextAlign.center,
            style: const TextStyle(
                fontSize: 13, color: AppColors.textGrey, height: 1.4),
          ),
        ],
      ),
    );
  }
}
