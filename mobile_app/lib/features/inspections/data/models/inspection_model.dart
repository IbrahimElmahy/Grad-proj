import '../../../../core/network/api_config.dart';
import '../../../alerts/data/models/alert_model.dart';

class InspectionModel {
  const InspectionModel({
    required this.id,
    required this.cameraId,
    required this.timestamp,
    required this.status,
    required this.riskLevel,
    required this.images,
    required this.analysisLog,
    this.video,
  });

  final String id;
  final String cameraId;
  final String timestamp;
  final String status;
  final String riskLevel;
  final List<InspectionImageModel> images;
  final Map<String, dynamic> analysisLog;
  final String? video;

  factory InspectionModel.fromJson(Map<String, dynamic> json) {
    return InspectionModel(
      id: json['id'] as String? ?? '',
      cameraId: json['camera_id'] as String? ?? 'Unknown Camera',
      timestamp: json['timestamp'] as String? ?? '',
      status: json['status'] as String? ?? 'COMPLETED',
      riskLevel: (json['risk_level'] as String? ?? 'SAFE').toUpperCase(),
      video: json['video'] as String?,
      analysisLog: json['analysis_log'] is Map<String, dynamic>
          ? json['analysis_log'] as Map<String, dynamic>
          : const {},
      images: (json['images'] as List<dynamic>? ?? const [])
          .whereType<Map<String, dynamic>>()
          .map(InspectionImageModel.fromJson)
          .toList(),
    );
  }

  String get date => AlertModel.formatDate(timestamp);
  String get time => AlertModel.formatTime(timestamp);
  String get statusLabel => AlertModel.statusLabel(riskLevel);
  AlertSeverity get severity => AlertSeverity.fromRiskLevel(riskLevel);

  List<DetectedObjectModel> get detections {
    return images.expand((image) => image.detectedObjects).toList();
  }

  int get detectionCount => detections.length;
  int get hazardCount => detections.where((item) => item.severity != 'SAFE').length;

  String get imageUrl {
    for (final image in images) {
      final candidate = image.processedImage.isNotEmpty ? image.processedImage : image.image;
      if (candidate.isNotEmpty) return candidate;
    }
    return '';
  }

  AlertModel toAlertModel() {
    return AlertModel(
      id: id,
      runwayTitle: cameraId,
      date: date,
      time: time,
      statusText: statusLabel,
      imagePath: imageUrl,
      severity: severity,
      detectionCount: detectionCount,
    );
  }
}

class InspectionImageModel {
  const InspectionImageModel({
    required this.id,
    required this.image,
    required this.processedImage,
    required this.createdAt,
    required this.detectedObjects,
  });

  final String id;
  final String image;
  final String processedImage;
  final String createdAt;
  final List<DetectedObjectModel> detectedObjects;

  factory InspectionImageModel.fromJson(Map<String, dynamic> json) {
    return InspectionImageModel(
      id: json['id'] as String? ?? '',
      image: ApiConfig.absoluteMediaUrl(json['image'] as String?),
      processedImage: ApiConfig.absoluteMediaUrl(json['processed_image'] as String?),
      createdAt: json['created_at'] as String? ?? '',
      detectedObjects: (json['detected_objects'] as List<dynamic>? ?? const [])
          .whereType<Map<String, dynamic>>()
          .map(DetectedObjectModel.fromJson)
          .toList(),
    );
  }
}

class DetectedObjectModel {
  const DetectedObjectModel({
    required this.id,
    required this.rawLabel,
    required this.objectType,
    required this.confidence,
    required this.severity,
    required this.geminiSuggestion,
    this.frameIndex = 0,
    this.frameTimestampSeconds,
  });

  final String id;
  final String rawLabel;
  final String objectType;
  final double confidence;
  final String severity;
  final String geminiSuggestion;
  final int frameIndex;
  final double? frameTimestampSeconds;

  factory DetectedObjectModel.fromJson(Map<String, dynamic> json) {
    return DetectedObjectModel(
      id: json['id'] as String? ?? '',
      rawLabel: json['raw_label'] as String? ?? '',
      objectType: json['object_type'] as String? ?? 'OTHER',
      confidence: (json['confidence'] as num?)?.toDouble() ?? 0,
      severity: (json['severity'] as String? ?? 'SAFE').toUpperCase(),
      geminiSuggestion: json['gemini_suggestion'] as String? ?? '',
      frameIndex: json['frame_index'] as int? ?? 0,
      frameTimestampSeconds: (json['frame_timestamp_seconds'] as num?)?.toDouble(),
    );
  }

  String get displayLabel {
    if (rawLabel.trim().isNotEmpty) return rawLabel.trim();
    return objectType.replaceAll('_', ' ');
  }

  String get confidencePercent => '${(confidence * 100).round()}%';
}

class DashboardStats {
  const DashboardStats({
    required this.totalInspections,
    required this.todayInspections,
    required this.weekInspections,
    required this.alertsToday,
  });

  final int totalInspections;
  final int todayInspections;
  final int weekInspections;
  final int alertsToday;

  factory DashboardStats.fromJson(Map<String, dynamic> json) {
    return DashboardStats(
      totalInspections: json['total_inspections'] as int? ?? 0,
      todayInspections: json['today_inspections'] as int? ?? 0,
      weekInspections: json['week_inspections'] as int? ?? 0,
      alertsToday: json['alerts_today'] as int? ?? 0,
    );
  }
}
