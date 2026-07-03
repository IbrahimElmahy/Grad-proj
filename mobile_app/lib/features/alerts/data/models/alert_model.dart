class AlertModel {
  final String id;
  final String runwayTitle;
  final String date;
  final String time;
  final String statusText;
  final String imagePath;
  final AlertSeverity severity;
  final int detectionCount;

  const AlertModel({
    this.id = '',
    required this.runwayTitle,
    required this.date,
    required this.time,
    required this.statusText,
    required this.imagePath,
    required this.severity,
    this.detectionCount = 0,
  });

  factory AlertModel.fromInspectionJson(Map<String, dynamic> json) {
    final images = json['images'] as List<dynamic>? ?? const [];
    final firstImage = images.whereType<Map<String, dynamic>>().isNotEmpty
        ? images.whereType<Map<String, dynamic>>().first
        : null;
    final detections =
        firstImage?['detected_objects'] as List<dynamic>? ?? const [];
    final riskLevel = (json['risk_level'] as String? ?? 'SAFE').toUpperCase();

    return AlertModel(
      id: json['id'] as String? ?? '',
      runwayTitle: json['camera_id'] as String? ?? 'Unknown Camera',
      date: formatDate(json['timestamp'] as String?),
      time: formatTime(json['timestamp'] as String?),
      statusText: statusLabel(riskLevel),
      imagePath: (firstImage?['processed_image'] ?? firstImage?['image'] ?? '')
          as String,
      severity: AlertSeverity.fromRiskLevel(riskLevel),
      detectionCount: detections.length,
    );
  }

  static DateTime? parseTimestamp(String? value) {
    if (value == null || value.isEmpty) return null;
    return DateTime.tryParse(value.replaceFirst(' ', 'T'));
  }

  static String formatDate(String? value) {
    final date = parseTimestamp(value);
    if (date == null) return '--/--/----';
    return '${date.day.toString().padLeft(2, '0')}/${date.month.toString().padLeft(2, '0')}/${date.year}';
  }

  static String formatTime(String? value) {
    final date = parseTimestamp(value);
    if (date == null) return '--:--';
    final hour = date.hour == 0
        ? 12
        : date.hour > 12
            ? date.hour - 12
            : date.hour;
    final period = date.hour >= 12 ? 'PM' : 'AM';
    return '${hour.toString().padLeft(2, '0')}:${date.minute.toString().padLeft(2, '0')} $period';
  }

  static String statusLabel(String riskLevel) {
    switch (riskLevel) {
      case 'HIGH':
        return 'Critical';
      case 'MEDIUM':
      case 'LOW':
        return 'Warning';
      default:
        return 'Safe';
    }
  }
}

enum AlertSeverity {
  safe,
  low,
  medium,
  highRisk;

  static AlertSeverity fromRiskLevel(String riskLevel) {
    switch (riskLevel) {
      case 'HIGH':
        return AlertSeverity.highRisk;
      case 'MEDIUM':
        return AlertSeverity.medium;
      case 'LOW':
        return AlertSeverity.low;
      default:
        return AlertSeverity.safe;
    }
  }
}
