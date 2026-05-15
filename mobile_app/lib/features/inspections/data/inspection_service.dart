import '../../../core/network/api_client.dart';
import '../../alerts/data/models/alert_model.dart';
import 'models/inspection_model.dart';

class InspectionService {
  const InspectionService({this.apiClient = const ApiClient()});

  final ApiClient apiClient;

  Future<List<AlertModel>> fetchInspections() async {
    final inspections = await fetchInspectionModels();
    return inspections.map((inspection) => inspection.toAlertModel()).toList();
  }

  Future<List<InspectionModel>> fetchInspectionModels() async {
    final json = await apiClient.get('/api/inspections/') as List<dynamic>;
    return json
        .whereType<Map<String, dynamic>>()
        .map(InspectionModel.fromJson)
        .toList();
  }

  Future<InspectionModel> fetchInspectionDetail(String id) async {
    final json = await apiClient.get('/api/inspections/$id/') as Map<String, dynamic>;
    return InspectionModel.fromJson(json);
  }

  Future<DashboardStats> fetchDashboardStats() async {
    final json = await apiClient.get('/stats/') as Map<String, dynamic>;
    return DashboardStats.fromJson(json);
  }
}
