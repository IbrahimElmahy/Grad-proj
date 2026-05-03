enum ReportType {
  system,
  officer,
}

class ReportModel {
  final String title;
  final String createdBy;
  final String date;
  final ReportType type;

  const ReportModel({
    required this.title,
    required this.createdBy,
    required this.date,
    required this.type,
  });
}