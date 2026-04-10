class AlertModel {
  final String runwayTitle;
  final String date;
  final String time;
  final String statusText;
  final String imagePath;
  final AlertSeverity severity;

  const AlertModel({
    required this.runwayTitle,
    required this.date,
    required this.time,
    required this.statusText,
    required this.imagePath,
    required this.severity,
  });
}

enum AlertSeverity {
  safe,
  medium,
  highRisk,
}